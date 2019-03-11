import paramiko
from scp import SCPClient
import paho.mqtt.client as mqtt
import time
import json
import threading

HOST = '34.244.160.143'
HOSTV2 = '63.33.41.143'
PORT = '22'
USER = 'ubuntu'
PASS = 'vodafone5G'
KEY = '/home/pi/certs/vf-it-5g.pem'

DESTINATION_FOLDER = '/home/ubuntu/vm1-node-service/raw_field_data'
#DESTINATION_FOLDER2 = '/home/ubuntu/raw_field_data'

ORIGIN_FOLDER = '/home/pi/pictures/'

TOPIC_TO_SUBCRIBE_TO = 'response/prediction/trash'

status = "NONE"
waste = "NONE"
i = 0
array = ["PLASTIC", "PAPER", "PLASTIC", "PAPER", "PLASTIC", "PAPER"]
def on_message_gg(client, userdata, message):
	global status, waste
	if status == "WAIT_RESP":
		global i
		response = str(message.payload.decode("utf-8"))
		print("message received")
		#print("message topic = ", message.topic)
		try:
			resp_parse = json.loads(response)
		except ValueError as e:
			print("malformed json")
			 
		waste = resp_parse['category'].split(" ")[0]
		waste = array[i]
		i = i+1
		print(waste)
		status = "SEND_RESP"

def timeout():
	global status, waste
	if(status == "WAIT_RESP"):
		print("timeout")
		waste = "TIMEOUT"
		status = "SEND_RESP"
	
class GreenGrass():
	def __init__(self):
		self.ssh = self._createSSHClient(HOST, PORT, USER, KEY)
		self.scp = SCPClient(self.ssh.get_transport())
		print("ok scp")
		self.client = mqtt.Client("gg")
		self.client.connect(HOST)
		self.client.subscribe(TOPIC_TO_SUBCRIBE_TO)
		self.client.on_message = on_message_gg
		self.client.loop_start()
		print("GreenGrass initialized")
		
	def _createSSHClient(self, server, port, user, key):
		cl = paramiko.SSHClient()
		cl.load_system_host_keys()
		cl.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		cl.connect(server, port, user, key_filename=key)
		return cl
	
	def getLabels(self, fileName):
		time_s = time.time()
		global status
		with self.scp:
			self.scp.put(fileName, DESTINATION_FOLDER)
		
		status = "WAIT_RESP"
		print("File Sent")
		print(time.time() - time_s)
		
		t = threading.Timer(1.5, timeout)
		t.start() 
		
		
		while(status is not "SEND_RESP"):
			pass
		
		status = "NONE"
		global waste
		print(waste)
		print(time.time() - time_s)
		return waste
