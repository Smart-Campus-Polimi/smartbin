#!/usr/bin/python3
import pprint as pp
import Rekognition
import subprocess

imageFile = '/Users/drosdesd/Downloads/empty2.png'
reko = Rekognition.Rekognition(True)

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
	while(True):

		waste = raw_input('picture?')
		waste = parseWaste(waste)
		file_name = subprocess.check_output('/home/pi/smartbin/scripts/webcam.sh')
		file_name = '/home/pi/pictures/'+str(file_name)[:-1]
		print file_name
		waste_type = reko.getLabels(file_name)
		

		if(waste_type != waste):
			print(waste)
		else:
			print(waste_type)

