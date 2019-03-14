#!/usr/bin/python3
import RPi.GPIO as GPIO
import sys
import VL53L0X
import time
import threading
import subprocess
import os
import signal 
from random import randint
import paho.mqtt.client as mqtt
import json
import thread
from multiprocessing.pool import ThreadPool

#my imports
#import Rekognition
import DoorLed
import RingLed
import MatrixLed
import MyCamera
import SerialHandler
import Servo
import RingWasteLed
import GreenGrass
import constants as c


GPIO.setmode(GPIO.BCM)


CURRENT_STATUS = "INIT"
OLD_STATUS = "NONE"

greengrass = True
aws_rekognition = True


#### VARS ####
#most of them are not used 
timer_door = None
isOpen = False
oldIsOpen = False
is_running = False
#startUp = True
wasteIn = False
oldWasteIn = False
deadToF1 = False
deadToF2 = False
total_iteration = 0

bin_json = {"bin_id": c.BIN_NAME, 
			"levels": { "unsorted": 13,
						"plastic": 3,
						"paper": 10,
						"glass": 8
					  }	
		    }

####### SIGNAL HANDLER ######
def signal_handler(signal, frame):
	print("Exit from smartbin!")
	doorLed.turnOff()
	ringLed.turnOff()
	matrixLed.turnOff()
	for r in wasteRings:
		r.setWaste(0)
	doorServo.openLid()
	sys.exit(0)


def on_message(client, userdata, message):
	print("rec")
	response = str(message.payload.decode("utf-8"))
	print(response)
	if(message.topic == c.FILL_LEVEL_FAKE):
		try:
			resp_parse = json.loads(response)
		except ValueError as e:
			print("malformed json")
		
		for key, val in resp_parse.items():
			bin_json["levels"][key] = val
		
		global CURRENT_STATUS
		if(CURRENT_STATUS == "IDLE"):
			CURRENT_STATUS = "SET_FILL_LEVEL"
	
	#if(message.topic == c.TOPIC_TO_FAKE_TO):
	#	print("fake")
		
		
	
def on_connect(client, userdata, flags, rc):
	print("Connected flags"+str(flags)+"result_code"+str(rc)+"client1_id")
	client.subscribe(c.FILL_LEVEL_FAKE)

####### SETUP TOF #######
def setupToF(all_tof=True):
	GPIO.setwarnings(False)

	# Setup GPIO for shutdown pins on each VL53L0X
	GPIO.setup(c.SENSOR1, GPIO.OUT)
	GPIO.setup(c.SENSOR2, GPIO.OUT)
	#GPIO.setup(c.SENSOR_UNSORTED, GPIO.OUT)
	#GPIO.setup(c.SENSOR_PLASTIC, GPIO.OUT)


	# Set all shutdown pins low to turn off each VL53L0X
	GPIO.output(c.SENSOR1, GPIO.LOW)
	GPIO.output(c.SENSOR2, GPIO.LOW)
	#GPIO.output(c.SENSOR_UNSORTED, GPIO.LOW)
	#GPIO.output(c.SENSOR_PLASTIC, GPIO.LOW)

	time.sleep(0.50)

	tof = VL53L0X.VL53L0X(address=0x2B)
	tof1 = VL53L0X.VL53L0X(address=0x2D)
	#tof_p = VL53L0X.VL53L0X(address=0x27)
	#tof_u = VL53L0X.VL53L0X(address=0x29)
	
	
	GPIO.output(c.SENSOR1, GPIO.HIGH)
	time.sleep(0.50)
	tof.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)

	GPIO.output(c.SENSOR2, GPIO.HIGH)
	time.sleep(0.50)
	tof1.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)
	
	#if(all_tof):
	#	GPIO.output(c.SENSOR_UNSORTED, GPIO.HIGH)
	#	time.sleep(0.50)
	#	tof_p.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)
		
	#	GPIO.output(c.SENSOR_PLASTIC, GPIO.HIGH)
	#	time.sleep(0.50)
	#	tof_u.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)

	#	return tof, tof1, tof_u, tof_p
	
	return tof, tof1



def door_callback(channel):
	global isOpen
	global CURRENT_STATUS, OLD_STATUS
	oldIsOpen = isOpen
	global timer_door

	isOpen = GPIO.input(c.DOOR_SENSOR)

	if(isOpen and not oldIsOpen):
		#if(CURRENT_STATUS == "PHOTO" or CURRENT_STATUS == "MOTORS" or CURRENT_STATUS == "PHOTO_DONE" or CURRENT_STATUS == "REKOGNITION"):
		#	print("ERROR!!!!!!")
		#else:
			CURRENT_STATUS = "DOOR_OPEN"
			doorLed.turnOn()
			timer_door = threading.Timer(c.TIMER_DOOR, door_forgotten_open)
			timer_door.start()
		
		
	if(not isOpen and oldIsOpen):
		if(CURRENT_STATUS == "DOOR_OPEN"):
			CURRENT_STATUS = "IDLE"
		if(CURRENT_STATUS == "WASTE_IN" or CURRENT_STATUS == "WAIT_CLOSE"):
			CURRENT_STATUS = "PHOTO"
		
		doorLed.turnOff() #move up in current status idle (if door open)
		if(timer_door is not None):
			if(timer_door.is_alive()):
				timer_door.cancel()


def photo_ready(my_cam):
	print("Scatto foto da timer")
	global CURRENT_STATUS
	CURRENT_STATUS = "WAIT_CLOSE"

def door_forgotten_open():
	#status!
	print("porta aprta da troppo tempo")
	global isOpen
	doorLed.blink()
	while(isOpen):
		#doorLed.blink()
		pass

def read_bin_level(tof):
	fill_lev = tof.get_distance()
	if(fill_lev > 0):
		level = int((fill_lev/c.BIN_HEIGHT) * 100.0)
		if(level > 100):
			level = 100
		return level	

##### DOOR SETUP #####
GPIO.setup(c.DOOR_SENSOR, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.add_event_detect(c.DOOR_SENSOR, GPIO.BOTH, callback=door_callback)  




if __name__ == "__main__":
	signal.signal(signal.SIGINT, signal_handler)
	print("STARTING SMARTBIN V2.0...")
	
	CURRENT_STATUS = "INIT"
	setup = True
	while(setup):
		if(CURRENT_STATUS == "INIT"):
			print("\n### Current status: {}".format(CURRENT_STATUS))
			serialComm = SerialHandler.SerialHandler()

			doorLed = DoorLed.DoorLed(serialComm.getSerialPort())
			doorLed.checkStatus()

			ringLed = RingLed.RingLed(serialComm.getSerialPort())
			ringLed.checkStatus()

			matrixLed = MatrixLed.MatrixLed(serialComm.getSerialPort())
			matrixLed.checkStatus()
			
			unsortedRing = RingWasteLed.RingWasteLed(serialComm.getSerialPort(), 'U')

			plasticRing = RingWasteLed.RingWasteLed(serialComm.getSerialPort(), 'P')

			paperRing = RingWasteLed.RingWasteLed(serialComm.getSerialPort(), 'C')

			glassRing = RingWasteLed.RingWasteLed(serialComm.getSerialPort(), 'G')
			
			
			paletta = Servo.PalettaServo()
			disk = Servo.DiskServo()
			
			calib_paletta = paletta.calibration()
			calib_disk = disk.calibration()
			
			wasteRings = [unsortedRing, plasticRing, paperRing, glassRing]
			for r in wasteRings:
				r.checkStatus()
			
			#MQTT
			client = mqtt.Client("levels")
			client.connect(c.HOST)
			client.on_message = on_message
			client.on_connect = on_connect
			
			
			client.loop_start()
			
			#tof1, tof2, tof_unsorted, tof_plastic = setupToF()
			tof1, tof2 = setupToF(False)
			#reko = Rekognition.Rekognition(debug=True)
			gg = GreenGrass.GreenGrass()
			
			camera = MyCamera.MyCamera()
			
			doorServo = Servo.DoorServo()
		
			pool = ThreadPool(processes=1)
			
			CURRENT_STATUS = "CHECK_INIT"
		
		elif(CURRENT_STATUS == "CHECK_INIT"):
			print("\n### Current status: {}".format(CURRENT_STATUS))
			
			errors = []
			if(not camera.checkStatus()): 
				errors.append("CAMERA")
			if(not serialComm.checkStatus()):
				errors.append("SERIAL")
			if(not tof1.checkStatus("2b")):
				errors.append("TOF1")
			if(not tof2.checkStatus("2d")):
				errors.append("TOF2")
	
			while(not calib_disk):
				print("wait disk calibration")
			while(not calib_paletta):
				print("wait paletta calibration")
				
			#if no errors set current status = boot
			if(len(errors) < 1):		
				CURRENT_STATUS = "BOOT"
			else:
				CURRENT_STATUS = "INIT_ERROR" 
				
				
			
		
		elif(CURRENT_STATUS == "BOOT"):
			print("\n### Current status: {}".format(CURRENT_STATUS))

			isOpen = GPIO.input(c.DOOR_SENSOR)
			startUp = True
			
			if(isOpen):
				CURRENT_STATUS = "DOOR_OPEN_ERROR"
			else:
				CURRENT_STATUS = "BOOT_DONE"
			
			#END BOOT
		
		elif(CURRENT_STATUS == "DOOR_OPEN_ERROR"):
			print("\n### Current status: {}".format(CURRENT_STATUS))
			ringLed.staticRed()
			matrixLed.redCross()
			while(isOpen):
				if(startUp):
					print("--> chiudi lo sportello per avviare lo smartbin")
					doorLed.blink()
					startUp = False
			
			CURRENT_STATUS = "BOOT_DONE"
			
		

		elif(CURRENT_STATUS == "BOOT_DONE"):
			print("\n### Current status: {}".format(CURRENT_STATUS))
			print("--> avvio smartbin...")
			is_running = True
			setup = False
			ringLed.staticGreen()
			matrixLed.greenArrow()
			#doorLed.turnOff()
			paletta.movePaletta("HOME")
			disk.moveDisk("HOME")
			CURRENT_STATUS = "READ_FILL_LEVEL"
			
		
		elif(CURRENT_STATUS == "INIT_ERROR"):
			print("GODAMN!")
			print("errors come from {}".format(errors))
			print("restart")
			sys.exit()
		


	
	#### START SMARTBIN ####
	while is_running:
		if(OLD_STATUS is not CURRENT_STATUS):
			print("\n### Current status: {} - old {}".format(CURRENT_STATUS, OLD_STATUS))
			
		OLD_STATUS = CURRENT_STATUS
		
		
		##### DOOR OPEN #####
		if(CURRENT_STATUS == "DOOR_OPEN"):
			#TODO: create an array with last N values and check wether there are outliers
			distance1 = tof1.get_distance()
			distance2 = tof2.get_distance()
			
			#print(distance1, distance2)
			
						
			if(distance1 < 0):
				distance1 = 666
				deadToF1 = True
				print("tof1 morto, restart")
				
			if(distance2 < 0):
				distance2 = 666
				deadToF2 = True
				print("tof2 morto, restart")
				
			if(deadToF1 or deadToF2):
				CURRENT_STATUS = "WASTE_IN"
			
			oldWasteIn = wasteIn
			if(distance1 < c.THRESHOLD_TOF or distance2 < c.THRESHOLD_TOF):
				CURRENT_STATUS = "WASTE_IN"
			
				
		##### WASTE IN #####
		elif(CURRENT_STATUS == "WASTE_IN"):
			print("oggetto inserito")
			camera.setCameraStatus(False)
			camera.erasePath()
			timer_pic = threading.Timer(c.TIMER_PHOTO, photo_ready, [camera])
			timer_pic.start()
			CURRENT_STATUS = "WAIT_CLOSE"
			
			
		##### WAIT CLOSE #####
		elif(CURRENT_STATUS == "WAIT_CLOSE"):
			pass
		
		
		##### PHOTO #####
		elif(CURRENT_STATUS == "PHOTO"):
			for r in wasteRings:
				r.turnOffRing()
			doorLed.turnOn()
			print("chiudo lo sportello")
			doorServo.closeLid()
			print("scatta foto da chiusura porta")
			timer_pic.cancel()
			camera.takePhoto()
			doorLed.turnOff()
			CURRENT_STATUS = "PHOTO_DONE"
				
		
		
		##### PHOTO DONE #####	
		elif(CURRENT_STATUS == "PHOTO_DONE"):
			CURRENT_STATUS = "REKOGNITION"
		
		 
		##### REKOGNITION #####
		elif(CURRENT_STATUS == "REKOGNITION"):
			
			waste_type_gg = "TIMEOUT"
			waste_type_aws = "UNSORTED"

			if(greengrass):
				async_result = pool.apply_async(gg.getLabels, (camera.currentPath(),))
				#gg_conn_timer = Threading.Timer(3, door_forgotten_open)
						
			if(aws_rekognition):
				#waste_type_aws = reko.getLabels(camera.currentPath())
				print("REKO: oggetto riconosciuto, e': {}".format(waste_type_aws))
	
			if(greengrass):
				waste_type_gg = async_result.get()	
				print("GG: oggetto riconosciuto, e': {}".format(waste_type_gg))


			#waste_type = waste_type_aws
			if(waste_type_gg == "TIMEOUT" or not greengrass):
				#if(waste_type_aws is not None):
				#waste_type = waste_type_aws
				print("this is AWS")
				#else:
				waste_type = "UNSORTED"
			else:
				waste_type = waste_type_gg
				print("This is Greengrass")


			
				
			if(waste_type == "UNSORTED"):
				unsortedRing.setWaste(333)
				bin_json["levels"]["unsorted"] += 2

			elif(waste_type == "PLASTIC"):
				plasticRing.setWaste(333)
				bin_json["levels"]["plastic"] += 2

			elif(waste_type == "PAPER"):
				paperRing.setWaste(333)
				bin_json["levels"]["paper"] += 2

			elif(waste_type == "GLASS"):
				glassRing.setWaste(333)
				bin_json["levels"]["glass"] += 2
		
			
			if(waste_type == "EMPTY"):
				CURRENT_STATUS = "SET_FILL_LEVEL"
				doorServo.openLid()
			else:
				CURRENT_STATUS = "MOTORS"
		
		
		##### MOTORS #####
		elif(CURRENT_STATUS == "MOTORS"):
			print("aziono i motori")
			total_iteration += 1
			
			#go
			paletta.movePaletta(waste_type)
			time.sleep(.2)
			disk.moveDisk(waste_type)
			print("illumino led")
			ringLed.breatheGreen()
			time.sleep(1.5)
			
			
			
			#back
			disk.moveDisk("HOME")
			paletta.movePaletta("HOME")
			time.sleep(1.5)
			print("azione finita")

			ringLed.staticGreen()
			matrixLed.greenArrow()
			doorServo.openLid()
			
			CURRENT_STATUS = "READ_FILL_LEVEL"
			
		
		##### READ WASTE #####
		elif(CURRENT_STATUS == "READ_FILL_LEVEL"):
			for key in bin_json["levels"].keys():
				if key == "unsorted":
					pass
					#fill_levels[key] = read_bin_level(tof_unsorted)
				if key == "plastic":
					pass
					#fill_levels[key] = read_bin_level(tof_plastic)
				if key == "paper":
					pass
				if key == "glass":
					pass
			
			for key, val in bin_json["levels"].items():
				print("{}: {}".format(key, val))
			
			
			CURRENT_STATUS = "SET_FILL_LEVEL"
			
		
		elif(CURRENT_STATUS == "SET_FILL_LEVEL"):
			for key in bin_json["levels"].keys():
				if key == "unsorted":
					unsortedRing.setWaste(bin_json["levels"][key])
				if key == "paper":
					plasticRing.setWaste(bin_json["levels"][key])
				if key == "plastic":
					paperRing.setWaste(bin_json["levels"][key])
				if key == "glass":
					glassRing.setWaste(bin_json["levels"][key])	
			
			print("this is the {} iteration".format(total_iteration))
			CURRENT_STATUS = "SEND_FILL_LEVEL"
			
		elif(CURRENT_STATUS == "SEND_FILL_LEVEL"):
			client.publish(c.FILL_LEVEL_TOPIC, json.dumps(bin_json))
			CURRENT_STATUS = "IDLE"	
			
		##### IDLE #####
		elif(CURRENT_STATUS == "IDLE"):
			if(deadToF1 and deadToF2):
				#reset tof
				doorServo.closeLid()
				#ringLed.staticRed()
				#matrixLed.redCross()
				tof1.stop_ranging()
				tof2.stop_ranging()
				tof1, tof2  = setupToF(all_tof = False)
				deadToF1 = False
				deadToF2 = False
				doorServo.openLid()
				#ringLed.staticGreen()
				#matrixLed.greenArrow()
			else:
				pass

		
				

	print("EOF!")
	tof2.stop_ranging()
	GPIO.output(c.SENSOR2, GPIO.LOW)
	tof1.stop_ranging()
	GPIO.output(c.SENSOR1, GPIO.LOW)
	ringLed.staticRed()
