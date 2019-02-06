#!/usr/bin/python3
import pprint as pp
import Rekognition

imageFile = '/Users/drosdesd/Downloads/empty2.png'
reko = Rekognition.Rekognition(True)

if __name__ == "__main__":
	waste_type = reko.getLabels(imageFile)
	print(waste_type)