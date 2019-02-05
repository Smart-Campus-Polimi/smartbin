#!/usr/bin/python3
import pprint as pp
import Rekognition

imageFile = '/Users/drosdesd/Downloads/paper.jpg'
reko = Rekognition.Rekognition(imageFile)

if __name__ == "__main__":
	waste_type = reko.getLabels()
	print(waste_type)