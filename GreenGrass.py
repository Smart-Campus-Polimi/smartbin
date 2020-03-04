import json
import logging
import os
import threading
import time

import paho.mqtt.client as mqtt
import paramiko
from scp import SCPClient

TIMEOUT_GG_RESPONSE = 2
TIMEOUT_CHEAT = 30
CONFIDENCE_THRESHOLD = .05

status = "NONE"
waste = "NONE"
next_one = None
timer_cheat = None

logger = logging.getLogger("GREENGRASS")
logger.setLevel(10)


def _timeout_cheat():
    global next_one
    next_one = None
    logger.debug("Next_one expired")


def _createSSHClient(server, port, user, key):
    cl = paramiko.SSHClient()
    cl.load_system_host_keys()
    cl.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cl.connect(server, port, user, key_filename=key)
    return cl


def _timeout_gg_resp():
    global status, waste, next_one, timer_cheat
    if status == "WAIT_RESP":
        logger.debug("Reach the timeout")
        if next_one is not None:
            waste = next_one
            next_one = None
            timer_cheat.cancel()
        else:
            waste = "TIMEOUT"

        status = "SEND_RESP"


def _parse_msg(resp):
    _waste = None
    print("resp", resp)
    try:
        resp_parse = json.loads(resp)
    except ValueError as e:
        logger.error("%s - %s", e, resp_parse)
        print(e)
        return "UNSORTED"
    print("resp:", resp_parse)

    print("cate", resp_parse["category"])
    # _waste = resp_parse['category'].split(" ")[0]
    try:
        _waste = resp_parse['category'].split(" ")[0]
        if float(resp_parse['confidence']) < CONFIDENCE_THRESHOLD:
            _waste = "UNSORTED"
    except ValueError as e:
        logger.error("%s - %s", e, resp_parse)
        print(e)
        return "UNSORTED"

    print("waste: ", _waste)
    if _waste == "EMPTY":
        _waste = "PLASTIC"
    return _waste


class GreenGrass:
    def __init__(self, config, environment, debug):
        self.mqtt_conf = config.mqtt
        self.server = getattr(config, environment)
        self.server.key = self.server.key_path + self.server.key
        self.ssh = _createSSHClient(self.server.host, self.server.port, self.server.user, self.server.key)
        self.scp = SCPClient(self.ssh.get_transport())

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message_gg

        self.time_start = 0
        self.time_scp = 0
        self.time_greengrass = 0
        self.time_local = 0

        if debug:
            self.server.destination_folder = self.server.destination_folder_debug
        try:
            self.client.connect(self.server.host)
        except ValueError as e:
            logger.error("%s", e)

        logger.info("Initialization done")
        self.client.loop_start()

    def getLabels(self, file_name):
        global status
        logger.info("New request")
        self.time_start = time.time()
        with self.scp:
            self.scp.put(file_name, self.server.destination_folder)

        status = "WAIT_RESP"
        logger.info("File Sent")
        self.time_scp = time.time() - self.time_start
        logger.warning("scp time %.2f sec", self.time_scp)

        t = threading.Timer(TIMEOUT_GG_RESPONSE, _timeout_gg_resp)
        t.start()

        while status != "SEND_RESP":
            pass

        status = "NONE"
        global waste
        logger.info("Response %s", waste)
        logger.warning("Total time %.2f sec", time.time() - self.time_start)
        return waste

    def on_message_gg(self, client, userdata, message):
        global status, waste, next_one, timer_cheat
        logger.debug("Message received: %s on topic %s", str(message.payload.decode("utf-8")), message.topic)

        logger.debug(status)
        logger.debug("%s, %s", os.path.split(message.topic)[0], os.path.split(self.mqtt_conf.greengrass_response)[0])
        if status == "WAIT_RESP":
            if str(os.path.split(message.topic)[0]) == str(os.path.split(self.mqtt_conf.greengrass_response)[0]):
                logger.debug("dentro")
                if next_one is None:
                    print("aoooo")
                    waste = _parse_msg(str(message.payload.decode("utf-8")))
                    print("aoooo 2")
                    logger.warning(waste)
                else:
                    waste = next_one
                    next_one = None
                    timer_cheat.cancel()

                logger.error("message topic: %s", str(os.path.split(message.topic)[1]))
                if str(os.path.split(message.topic)[1]) == "greengrass":
                    self.time_greengrass = time.time() - self.time_start
                if str(os.path.split(message.topic)[1]) == "local":
                    self.time_local = time.time() - self.time_start

                if str(message.topic) == str(self.mqtt_conf.prediction_fake):
                    waste = _parse_msg(str(message.payload.decode("utf-8")))

                logger.debug("asd")
                status = "SEND_RESP"

        else:
            if message.topic == self.mqtt_conf.prediction_fake:
                next_one = _parse_msg(str(message.payload.decode("utf-8")))
                logger.warning("Next waste is %s", next_one)
                timer_cheat = threading.Timer(TIMEOUT_CHEAT, _timeout_cheat)
                timer_cheat.start()

    def on_connect(self, client, userdata, flags, rc):
        logger.debug("Connected with result code %s", str(rc))
        client.subscribe(self.mqtt_conf.greengrass_response)
        client.subscribe(self.mqtt_conf.prediction_fake)

    def time_recap(self):
        return self.time_scp, self.time_local, self.time_greengrass
