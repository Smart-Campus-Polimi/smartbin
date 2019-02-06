#!/usr/bin/python3
import RPi.GPIO as GPIO
import sys
import VL53L0X
import time
import threading

import Rekognition
import DoorLed


GPIO.setmode(GPIO.BCM)
THRESHOLD_TOF = 374
TIMER_PHOTO = 5 #seconds
TIMER_DOOR = 20 #seconds

#### GPIO PINS ####
DOOR_SENSOR = 18
SENSOR1 = 20
SENSOR2 = 16


#### VARS ####
timer_door = None
isOpen = False
oldIsOpen = False
is_running = False
startUp = True
wasteIn = False
oldWasteIn = False
photoDone = False

####### SETUP TOF #######
def setupToF():
	GPIO.setwarnings(False)

	# Setup GPIO for shutdown pins on each VL53L0X
	GPIO.setup(SENSOR1, GPIO.OUT)
	GPIO.setup(SENSOR2, GPIO.OUT)

	# Set all shutdown pins low to turn off each VL53L0X
	GPIO.output(SENSOR1, GPIO.LOW)
	GPIO.output(SENSOR2, GPIO.LOW)

	time.sleep(0.50)

	tof = VL53L0X.VL53L0X(address=0x2B)
	tof1 = VL53L0X.VL53L0X(address=0x2D)

	GPIO.output(SENSOR1, GPIO.HIGH)
	time.sleep(0.50)
	tof.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)

	GPIO.output(SENSOR2, GPIO.HIGH)
	time.sleep(0.50)
	tof1.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)

	return tof, tof1



def door_callback(channel):
	global isOpen
	oldIsOpen = isOpen
	global timer_door

	isOpen = GPIO.input(DOOR_SENSOR)

	if(isOpen and not oldIsOpen):
		doorLed.turnOn()
		timer_door = threading.Timer(TIMER_DOOR, door_forgotten_open)
		timer_door.start()
	if(not isOpen and oldIsOpen):
		doorLed.turnOff()
		if(timer_door is not None):
			if(timer_door.is_alive()):
				timer_door.cancel()

def takePicture():
	path = subprocess.check_output('scripts/webcam.sh')

	global photoDone
	photoDone = True

	#TODO: parse path
	return path


def handleWaste(imageFile):
	waste_type = reko.getLabels(imageFile)
	print("oggetto riconosciuto, e':")
	print(waste_type)
	print("illumino led")
	print("aziono i motori")
	time.sleep(2)
	print("azione finita")
	global photoDone, wasteIn, oldWasteIn
	photoDone = False
	wasteIn = False
	oldWasteIn = False
	my_photo = None


def photo_ready():
	global photoDone, my_photo
	print("Scatto foto da timer")
	my_photo = takePicture()

def door_forgotten_open():
	print("porta aprta da troppo tempo")
	global isOpen
	while(isOpen):
		doorLed.blink()

##### DOOR SETUP #####
GPIO.setup(DOOR_SENSOR, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.add_event_detect(DOOR_SENSOR, GPIO.BOTH, callback=door_callback)  

tof1, tof2 = setupToF()

reko = Rekognition.Rekognition(debug=True)

if __name__ == "__main__":
	doorLed = DoorLed.DoorLed()
	doorLed.turnOff()
	isOpen = GPIO.input(DOOR_SENSOR)

	while(isOpen):
		doorLed.blink()
		if(startUp):
			print("chiudi lo sportello per avviare lo smartbin")
			startUp = False

	if(not isOpen):
		print("avvio smartbin...")
		startUp = False
		is_running = True
		doorLed.turnOff()
	else:
		print("ERROR STARTUP")
		sys.exit()

	while is_running:
		oldWasteIn = wasteIn
		if(isOpen):
			#TODO: create an array with last N values and check wether there are outliers
			distance1 = tof1.get_distance()
			distance2 = tof2.get_distance()

			print(distance1, distance2)
			
			if(distance1 < THRESHOLD_TOF or distance2 < THRESHOLD_TOF):
				wasteIn = True
				if (wasteIn and not oldWasteIn):
					print("oggetto inserito")
					photoDone = False
					timer_pic = threading.Timer(TIMER_PHOTO, photo_ready)
					timer_pic.start()

		if(not isOpen and wasteIn):
			if(not photoDone):
				print("chiudo ilo sportello")
				#TODO: motore sportello
				print("scatta foto da chiusura porta")
				timer_pic.cancel()
				my_photo = takePicture()
			


			if(photoDone):
				#TODO photo
				handleWaste(my_photo)
			
			
		
				

	print("EOF!")
	tof2.stop_ranging()
	GPIO.output(SENSOR2, GPIO.LOW)
	tof1.stop_ranging()
	GPIO.output(SENSOR1, GPIO.LOW)
