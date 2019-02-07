#!/usr/bin/python3
import pprint as pp
import Rekognition
import subprocess
import os
import VL53L0X
import time

DIRECTORY = '~/pictures/'
WEBCAM = '~/smartbin/scripts/webcam.sh'

RASP = True
KEY_INPUT = False
THRESHOLD = 200

imagePath = '~/Downloads/empty.png'
waste = None
photoTime = 0
is_running = True
isPhoto = False

def takePhoto():
	photoTime = time.time()
	file_name = subprocess.check_output(os.path.expanduser(WEBCAM))
	file_name = os.path.expanduser(DIRECTORY)+str(file_name)[:-1]
	photoTime = time.time() - photoTime

	return file_name, photoTime

def parseWaste(key):
	if(key == '1'):
		return 'UNSORTED'
	elif(key == '2'):
		return 'PLASTIC'
	elif(key == '3'):
		return 'PAPER'
	elif(key == '4'):
		return 'GLASS'
	else:
		return 'UNSORTED'

if __name__ == "__main__":

	if(RASP and not KEY_INPUT):
		tof = VL53L0X.VL53L0X()
	
	reko = Rekognition.Rekognition(True)
	
	while(is_running):
		if(RASP):
			if(KEY_INPUT):
				waste = raw_input('picture?')
				waste = parseWaste(waste)
				file_name, photoTime = takePhoto()
				isPhoto = True
			if(not KEY_INPUT):
				distance = tof.get_distance()
				if(distance > 0):
					if(distance < THRESHOLD):
						file_name, photoTime = takePhoto()
                				isPhoto = True
		else:
			file_name = imagePath
			isPhoto = True
		
		if(isPhoto):
			print(file_name)
			waste_type = reko.getLabels(os.path.expanduser(file_name))
		
			if(RASP and KEY_INPUT):
				if (waste_type != waste):
					#cheat
					print(waste)
				else:
					#true
					print(waste_type)
			else:
				print("\n\nWASTE IS: {}".format(waste_type))
				if(not RASP):
					is_running = False

			reko.timeoutRecap(photoTime)
			isPhoto = False
			time.sleep(2)

