#!/usr/bin/python3
import RPi.GPIO as GPIO
import sys


GPIO.setmode(GPIO.BCM)

DOOR_SENSOR = 18

isOpen = False
oldIsOpen = False
is_running = False
startUp = True

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


if __name__ == "__main__":
	doorLed = DoorLed.DoorLed()

	isOpen = GPIO.input(DOOR_SENSOR)

	while(isOpen):
		if(startUp):
			print("chiudi lo sportello per avviare lo smartbin")
			doorLed.blink()
			startUp = False

	if(not isOpen):
		print("avvio smartbin...")
		is_running = True
		doorLed.turnOff()
	
	else:
		print("ERROR STARTUP")
		sys.exit()

	while is_running:
		pass

	print("EOF!")