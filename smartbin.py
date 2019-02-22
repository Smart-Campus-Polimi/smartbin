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

#my imports
import Rekognition
import DoorLed
import RingLed
import MatrixLed
import MyCamera
import SerialHandler
import Servo
import RingWasteLed

GPIO.setmode(GPIO.BCM)

CURRENT_STATUS = "INIT"
OLD_STATUS = "NONE"



THRESHOLD_TOF = 300
BIN_HEIGHT = 800.0
TIMER_PHOTO = 5 #seconds
TIMER_DOOR = 10 #seconds

#### PATHS ####
#WEBCAM = '~/smartbin/scripts/webcam.sh'
PICTURE_DIRECTORY = '~/pictures/'

#### GPIO PINS ####
DOOR_SENSOR = 18
SENSOR1 = 20 #tof1
SENSOR2 = 16 #tof2
SENSOR_UNSORTED = 21 #tof unsorted
SENSOR_PLASTIC = 26 #tof plastic



#### VARS ####
timer_door = None
isOpen = False
oldIsOpen = False
is_running = False
#startUp = True
wasteIn = False
oldWasteIn = False
deadToF1 = False
deadToF2 = False

fill_levels = {
				"unsorted": 0,
				"plastic": 0,
				"paper": 0,
				"glass": 0
			   }

####### SIGNAL HANDLER ######
def signal_handler(signal, frame):
	print("Exit from smartbin!")
	doorLed.turnOff()
	ringLed.turnOff()
	matrixLed.turnOff()
	for r in wasteRings:
		r.setWaste(0)
	miniservo.openLid()
	sys.exit(0)


####### SETUP TOF #######
def setupToF(all_tof=True):
	GPIO.setwarnings(False)

	# Setup GPIO for shutdown pins on each VL53L0X
	GPIO.setup(SENSOR1, GPIO.OUT)
	GPIO.setup(SENSOR2, GPIO.OUT)
	GPIO.setup(SENSOR_UNSORTED, GPIO.OUT)
	GPIO.setup(SENSOR_PLASTIC, GPIO.OUT)


	# Set all shutdown pins low to turn off each VL53L0X
	GPIO.output(SENSOR1, GPIO.LOW)
	GPIO.output(SENSOR2, GPIO.LOW)
	GPIO.output(SENSOR_UNSORTED, GPIO.LOW)
	GPIO.output(SENSOR_PLASTIC, GPIO.LOW)

	time.sleep(0.50)

	tof = VL53L0X.VL53L0X(address=0x2B)
	tof1 = VL53L0X.VL53L0X(address=0x2D)
	tof_p = VL53L0X.VL53L0X(address=0x27)
	tof_u = VL53L0X.VL53L0X(address=0x29)
	
	
	GPIO.output(SENSOR1, GPIO.HIGH)
	time.sleep(0.50)
	tof.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)

	GPIO.output(SENSOR2, GPIO.HIGH)
	time.sleep(0.50)
	tof1.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)
	
	if(all_tof):
		GPIO.output(SENSOR_UNSORTED, GPIO.HIGH)
		time.sleep(0.50)
		tof_p.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)
		
		GPIO.output(SENSOR_PLASTIC, GPIO.HIGH)
		time.sleep(0.50)
		tof_u.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)

		return tof, tof1, tof_u, tof_p
	
	return tof, tof1



def door_callback(channel):
	global isOpen
	global CURRENT_STATUS, OLD_STATUS
	oldIsOpen = isOpen
	global timer_door

	isOpen = GPIO.input(DOOR_SENSOR)

	if(isOpen and not oldIsOpen):
		if(CURRENT_STATUS == "PHOTO" or CURRENT_STATUS == "MOTORS" or CURRENT_STATUS == "PHOTO_DONE" or CURRENT_STATUS == "REKOGNITION"):
			print("ERROR!!!!!!")
		else:
			CURRENT_STATUS = "DOOR_OPEN"
			doorLed.turnOn()
			timer_door = threading.Timer(TIMER_DOOR, door_forgotten_open)
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
		level = int((fill_lev/BIN_HEIGHT) * 100.0)
		if(level > 100):
			level = 100
		return level	

##### DOOR SETUP #####
GPIO.setup(DOOR_SENSOR, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.add_event_detect(DOOR_SENSOR, GPIO.BOTH, callback=door_callback)  




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
			
			wasteRings = [unsortedRing, plasticRing, paperRing, glassRing]
			for r in wasteRings:
				r.checkStatus()
			
			tof1, tof2, tof_unsorted, tof_plastic = setupToF()
			
			reko = Rekognition.Rekognition(debug=True)
			
			camera = MyCamera.MyCamera()
			
			miniservo = Servo.DoorServo()
			
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

			if(len(errors) < 1):		
				CURRENT_STATUS = "BOOT"
			else:
				CURRENT_STATUS = "INIT_ERROR" 
				
				#if no errors set current status = boot
			
		
		elif(CURRENT_STATUS == "BOOT"):
			print("\n### Current status: {}".format(CURRENT_STATUS))

			isOpen = GPIO.input(DOOR_SENSOR)
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
			
			print(distance1, distance2)
			
						
			if(distance1 < 5):
				distance1 = 666
				deadToF1 = True
				print("tof1 morto, restart")
				
			if(distance2 < 5):
				distance2 = 666
				deadToF2 = True
				print("tof2 morto, restart")
				
			
			oldWasteIn = wasteIn
			if(distance1 < THRESHOLD_TOF or distance2 < THRESHOLD_TOF):
				CURRENT_STATUS = "WASTE_IN"
			
				
		##### WASTE IN #####
		elif(CURRENT_STATUS == "WASTE_IN"):
			print("oggetto inserito")
			camera.setCameraStatus(False)
			camera.erasePath()
			timer_pic = threading.Timer(TIMER_PHOTO, photo_ready, [camera])
			timer_pic.start()
			CURRENT_STATUS = "WAIT_CLOSE"
			
			
		##### WAIT CLOSE #####
		elif(CURRENT_STATUS == "WAIT_CLOSE"):
			pass
		
		
		##### PHOTO #####
		elif(CURRENT_STATUS == "PHOTO"):
			doorLed.turnOn()
			print("chiudo lo sportello")
			miniservo.closeLid()
			print("scatta foto da chiusura porta")
			timer_pic.cancel()
			camera.takePhoto()
			doorLed.turnOff()
			CURRENT_STATUS = "PHOTO_DONE"
				
		
		
		##### PHOTO DONE #####	
		elif(CURRENT_STATUS == "PHOTO_DONE"):
			#camera.setCameraStatus(False)
			CURRENT_STATUS = "REKOGNITION"
		
		
		##### REKOGNITION #####
		elif(CURRENT_STATUS == "REKOGNITION"):
			waste_type = reko.getLabels(camera.currentPath())
			#camera.erasePath()			
			print("oggetto riconosciuto, e': {}".format(waste_type))

			if(waste_type is "UNSORTED"):
				unsortedRing.setWaste(333)

			elif(waste_type is "PLASTIC"):
				plasticRing.setWaste(333)

			elif(waste_type is "PAPER"):
				paperRing.setWaste(333)

			elif(waste_type is "GLASS"):
				glassRing.setWaste(333)
		
			

			if(waste_type is "EMPTY"):
				CURRENT_STATUS = "IDLE"
				miniservo.openLid()
			else:
				CURRENT_STATUS = "MOTORS"
		
		
		##### MOTORS #####
		elif(CURRENT_STATUS == "MOTORS"):
			print("illumino led")
			ringLed.breatheGreen()
			print("aziono i motori")
			time.sleep(3)
			print("azione finita")
			ringLed.staticGreen()
	
			miniservo.openLid()
			CURRENT_STATUS = "READ_FILL_LEVEL"
			
		
		##### READ WASTE #####
		elif(CURRENT_STATUS == "READ_FILL_LEVEL"):
			for key in fill_levels.keys():
				if key == "unsorted":
					fill_levels[key] = read_bin_level(tof_unsorted)
					unsortedRing.setWaste(fill_levels[key])
				if key == "plastic":
					fill_levels[key] = read_bin_level(tof_plastic)
					plasticRing.setWaste(fill_levels[key])
				if key == "paper":
					fill_levels[key] = randint(0, 100)
					paperRing.setWaste(fill_levels[key])
				if key == "glass":
					fill_levels[key] = randint(0, 100)
					glassRing.setWaste(fill_levels[key])
			
			
			for key, val in fill_levels.items():
				print("{}: {}".format(key, val))
			
			
			CURRENT_STATUS = "IDLE"
		
				
			
		##### IDLE #####
		elif(CURRENT_STATUS == "IDLE"):
			
			if(deadToF1 and deadToF2):
				#reset tof
				miniservo.closeLid()
				ringLed.staticRed()
				matrixLed.redCross()
				tof1.stop_ranging()
				tof2.stop_ranging()
				tof1, tof2 = setupToF(all_tof = False)
				deadToF1 = False
				deadToF2 = False
				miniservo.openLid()
				ringLed.staticGreen()
				matrixLed.greenArrow()

		
				

	print("EOF!")
	tof2.stop_ranging()
	GPIO.output(SENSOR2, GPIO.LOW)
	tof1.stop_ranging()
	GPIO.output(SENSOR1, GPIO.LOW)
	ringLed.staticRed()
