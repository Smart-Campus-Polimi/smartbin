#!/usr/bin/python3
import pprint as pp
import time

import boto3

import labels


class Rekognition:
    def __init__(self, debug=False):
        self.session = boto3.Session(profile_name='default')
        self.rekognition = self.session.client('rekognition')
        self.debug = debug
        self.request_time = 0
        self.labeling_time = 0

    def getLabels(self, image_file):
        count = 0
        result = {
            "UNSORTED": 75,
            "PLASTIC": 0,
            "ALUMINIUM": 0,
            "PAPER": 0,
            "GLASS": 0,
            "EMPTY": 0
        }

        rekognition_response = self._sendRequest(image_file)
        self.labeling_time = time.time()

        for label in rekognition_response['Labels']:
            if label['Name'] not in labels.drop:
                count += 1
                if label['Name'] in labels.plastic:
                    result["PLASTIC"] += label['Confidence']
                if label['Name'] in labels.aluminium:
                    result["PLASTIC"] += label['Confidence']
                if label['Name'] in labels.paper:
                    result["PAPER"] += label['Confidence']
                if label['Name'] in labels.glass:
                    result["GLASS"] += label['Confidence']

        if count < 2:
            result["EMPTY"] = 100

        if self.debug:
            print(result)
            print("Found {} labels".format(count))

        self.labeling_time = time.time() - self.labeling_time
        return max(zip(result.values(), result.keys()))[1]

    def _sendRequest(self, image_file):
        self.request_time = time.time()

        with open(image_file, 'rb') as image:
            rekognition_response = self.rekognition.detect_labels(
                Image={'Bytes': image.read()},
                MaxLabels=10,
                MinConfidence=50)

            self.request_time = time.time() - self.request_time

        if self.debug:
            pp.pprint(rekognition_response)

        return rekognition_response

    def timeoutRecap(self, photoT):
        print("\n")
        print("-" * 30)
        print("REKO: Taking a picture: {0:.4f} s".format(photoT))
        print("REKO: Request to rekognition: {0:.4f} s".format(self.request_time))
        print("REKO: Parsing response: {0:.4f} s".format(self.labeling_time))
