#!/usr/bin/python3
import boto3
import time
import labels as l
import pprint as pp

class Rekognition():
		def __init__(self,debug=False):
			self.session = boto3.Session(profile_name='default')
			self.rekognition = self.session.client('rekognition')
			#self.imageFile = imageFile
			self.debug = debug
		
		def getLabels(self, imageFile):
			count = 0
			result = {
				"UNSORTED": 75,
				"PLASTIC": 0,
				"ALUMINIUM": 0,
				"PAPER": 0,
				"GLASS": 0, 
				"NONE": 0
					}

			rekognition_response = self._sendRequest(imageFile)
			for label in rekognition_response['Labels']:
				count += 1
				if label['Name'] in l.plastic:
					result['PLASTIC'] += label['Confidence']
				if label['Name'] in l.aluminium:
					result['ALUMINIUM'] += label['Confidence']
				if label['Name'] in l.paper:
					result['PAPER'] += label['Confidence']
				if label['Name'] in l.glass:
					result['GLASS'] += label['Confidence']
			
			if(count<2):
				result['NONE'] = 100

			if(self.debug):
				print(count)
				pp.pprint(result)

			return max(zip(result.values(), result.keys()))[1]			

		def _sendRequest(self, imageFile):
			start_request = time.time()

			with open(imageFile, 'rb') as image: 
				rekognition_response = self.rekognition.detect_labels(
							Image = {'Bytes': image.read()},
							MaxLabels=10,
							MinConfidence=50)

				print("{0:.4f}".format(time.time() - start_request), "sec")
				
			if(self.debug):
				pp.pprint(rekognition_response)

			return rekognition_response
			