#!/usr/bin/python3
import boto3
import time
import labels as l
import pprint as pp

class Rekognition():
		def __init__(self,debug=False):
			self.session = boto3.Session(profile_name='default')
			self.rekognition = self.session.client('rekognition')
			self.debug = debug
			self.requestTime = 0
			self.labelingTime = 0


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
			self.labelingTime = time.time()

			#TODO: drop labels

			for label in rekognition_response['Labels']:
				if label['Name'] in l.drop:
					continue
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

			self.labelingTime = time.time() - self.labelingTime
			return max(zip(result.values(), result.keys()))[1]			

		def _sendRequest(self, imageFile):
			self.requestTime = time.time()

			with open(imageFile, 'rb') as image: 
				rekognition_response = self.rekognition.detect_labels(
							Image = {'Bytes': image.read()},
							MaxLabels=10,
							MinConfidence=50)

				self.requestTime = time.time() - self.requestTime
				
			if(self.debug):
				pp.pprint(rekognition_response)

			return rekognition_response


		def timeoutRecap(self, photoT):
			print("\n")
			print("-"*30)
			print("Taking a picture: %f sec", "{0:.4f}".format(photoT))
			print("Request to rekognition: %f sec", "{0:.4f}".format(self.requestTime))
			print("Parsing response: %f sec", "{0:.4f}".format(self.labelingTime))

				
			