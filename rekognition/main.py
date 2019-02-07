#!/usr/bin/python3
import pprint as pp
import Rekognition
import subprocess
import os
import VL53L0X
import time
import Queue
import signal
import sys
import MyCheat as c

DIRECTORY = '~/pictures/'
WEBCAM = '~/smartbin/scripts/webcam.sh'

RASP = True
KEY_INPUT = True
THRESHOLD = 200

imagePath = '~/Downloads/empty.png'
cheat_waste = None
photoTime = 0
is_running = True
isPhoto = False

q = Queue.Queue(10)
t = c.MyCheat(q)

def signal_handler(signal, frame):
	print("Exit!")

	t.stop()
	sys.exit(0)

def takePhoto():
	photoTime = time.time()
	file_name = subprocess.check_output(os.path.expanduser(WEBCAM))
	file_name = os.path.expanduser(DIRECTORY)+str(file_name)[:-1]
	photoTime = time.time() - photoTime

	return file_name, photoTime


if __name__ == "__main__":
	signal.signal(signal.SIGINT, signal_handler)
	print("shoot and reko portable just started ;)")

	if(RASP and not KEY_INPUT):
		tof = VL53L0X.VL53L0X()
	
	if(not KEY_INPUT):	
		t.setDaemon(True)
		t.start()

	reko = Rekognition.Rekognition(True)
	
	while(is_running):
		if(RASP):
			if(KEY_INPUT):
				cheat_waste = raw_input('picture?')
				cheat_waste = c.parseWaste(cheat_waste)
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
			
			if not q.empty():
				cheat_waste = q.get()
			
			if cheat_waste is not None:
				print("yeah")
				waste_type = cheat_waste
					
			print("\n\nWASTE IS: {}".format(waste_type))
			
			if(not RASP):
				is_running = False

			reko.timeoutRecap(photoTime)
			isPhoto = False
			cheat_waste = None
			time.sleep(2)

