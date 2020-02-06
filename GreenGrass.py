import paramiko
from scp import SCPClient
import paho.mqtt.client as mqtt
import time
import json
import threading
import constants as c

HOST = '34.244.160.143'
HOSTV2 = '63.33.41.143'
PORT = '22'
USER = 'ubuntu'
PASS = 'vodafone5G'
KEY_PATH = '/home/pi/certs/'
KEY = KEY_PATH + 'vf-it-5g.pem'
TIMEOUT_GG_RESPONSE = 1.5
TIMEOUT_CHEAT = 30

DESTINATION_FOLDER = '/home/ubuntu/vm1-node-service/raw_field_data'
# DESTINATION_FOLDER2 = '/home/ubuntu/raw_field_data'

ORIGIN_FOLDER = '/home/pi/pictures/'

TOPIC_TO_SUBSCRIBE_TO = 'response/prediction/trash'
TOPIC_FAKE = 'response/prediction/fake'

status = "NONE"
waste = "NONE"
next_one = None
timer_cheat = None


def _parse_msg(resp):
    _waste = None
    try:
        resp_parse = json.loads(resp)
    except ValueError as e:
        print("GREENGRASS: malformed json")
        return "UNSORTED"

    try:
        _waste = resp_parse['category'].split(" ")[0]
        if float(resp_parse['confidence']) < .05:
            _waste = "UNSORTED"
    except ValueError as e:
        print("GREENGRASS: wrong split")
        return "UNSORTED"

    return _waste


def on_message_gg(client, userdata, message):
    global status, waste, next_one, timer_cheat
    print("GREENGRASS: message received")
    if status == "WAIT_RESP":
        if message.topic == TOPIC_TO_SUBSCRIBE_TO:
            if next_one is None:
                waste = _parse_msg(str(message.payload.decode("utf-8")))
            else:
                waste = next_one
                next_one = None
                timer_cheat.cancel()

        if message.topic == TOPIC_FAKE:
            waste = _parse_msg(str(message.payload.decode("utf-8")))

        status = "SEND_RESP"

    else:
        if message.topic == TOPIC_FAKE:
            next_one = _parse_msg(str(message.payload.decode("utf-8")))
            print("GREENGRASS: next waste is {}".format(next_one))
            timer_cheat = threading.Timer(TIMEOUT_CHEAT, _timeout_cheat)
            timer_cheat.start()


def on_connect(client, userdata, flags, rc):
    print("GREENGRASS: Connected with result code " + str(rc))
    client.subscribe(TOPIC_TO_SUBSCRIBE_TO)
    client.subscribe(TOPIC_FAKE)


def _timeout_gg_resp():
    global status, waste, next_one, timer_cheat
    if status == "WAIT_RESP":
        print("GG: timeout")
        if next_one is not None:
            waste = next_one
            next_one = None
            timer_cheat.cancel()
        else:
            waste = "TIMEOUT"

        status = "SEND_RESP"


def _timeout_cheat():
    global next_one
    next_one = None
    print("GREENGRASS: next_one expired")


def _createSSHClient(server, port, user, key):
    cl = paramiko.SSHClient()
    cl.load_system_host_keys()
    cl.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cl.connect(server, port, user, key_filename=key)
    return cl


class GreenGrass:
    def __init__(self):
        self.ssh = _createSSHClient(c.HOST, PORT, USER, KEY)
        self.scp = SCPClient(self.ssh.get_transport())

        self.client = mqtt.Client()
        self.client.on_connect = on_connect
        self.client.on_message = on_message_gg
        self.client.connect(c.HOST)

        self.client.loop_start()
        print("GREENGRASS: initialization done")

    def getLabels(self, file_name):
        print("-----\nNEW GG REQUEST")
        time_s = time.time()
        global status
        with self.scp:
            self.scp.put(file_name, DESTINATION_FOLDER)

        status = "WAIT_RESP"
        print("GREENGRASS: File Sent")
        print("GREENGRASS: scp time {0:.2f} sec".format(time.time() - time_s))

        t = threading.Timer(TIMEOUT_GG_RESPONSE, _timeout_gg_resp)
        t.start()

        while status != "SEND_RESP":
            pass

        status = "NONE"
        global waste
        print("GREENGRASS: response {}".format(waste))
        print("GREENGRASS: total time {0:.2f} sec".format(time.time() - time_s))
        return waste
