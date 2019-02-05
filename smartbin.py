#!/usr/bin/python3
import RPi.GPIO as GPIO
import sys
import VL53L0X
import DoorLed

GPIO.setmode(GPIO.BCM)
THRESHOLDTOF = 374

#### GPIO PINS ####
DOOR_SENSOR = 18
SENSOR1 = 20
SENSOR2 = 16


#### VARS ####
isOpen = False
oldIsOpen = False
is_running = False
startUp = True
wasteIn = False
oldWasteIn = False

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
	isOpen = GPIO.input(DOOR_SENSOR)

	if(isOpen and not oldIsOpen):
		doorLed.turnOn()
	if(not isOpen and oldIsOpen):
		doorLed.turnOff()



##### DOOR SETUP #####
GPIO.setup(DOOR_SENSOR, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.add_event_detect(DOOR_SENSOR, GPIO.BOTH, callback=door_callback)  

tof1, tof2 = setupToF()

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
		distance1 = tof1.get_distance()
		distance2 = tof2.get_distance()

		print(distance1, distance2)
		if(distance1 < THRESHOLD or distance2 < THRESHOLD):
        	print("oggetto")
    	else:
        	print("NO oggetto")

	print("EOF!")
	tof2.stop_ranging()
	GPIO.output(SENSOR2, GPIO.LOW)
	tof1.stop_ranging()
	GPIO.output(SENSOR1, GPIO.LOW)

