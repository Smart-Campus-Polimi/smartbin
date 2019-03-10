import paho.mqtt.client as mqtt
import json

BROKER = '34.244.160.143'
TOPIC_TO_PUBLISH_TO = 'response/prediction/fake'
client = mqtt.Client() 
client.connect(BROKER)


def parse_waste(val):
	if(int(val) == 1):
		return "UNSORTED"
	if(int(val) == 2):
		return "PLASTIC"
	if(int(val) == 3):
		return "PAPER"
	if(int(val) == 4):
		return "GLASS"
	if(int(val) == 5):
		return "EMPTY"

print("\n1: UNSORTED\n2: PLASTIC\n3: PAPER\n4: GLASS\n5: EMPTY\n")

while True:
		waste_type = parse_waste(input("?"))

		my_dict = {"category": waste_type,
				   "confidence": 0.99}
		client.publish(TOPIC_TO_PUBLISH_TO, json.dumps(my_dict))
