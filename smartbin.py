#!/usr/bin/python3
import RPi.GPIO as GPIO
import sys
import VL53L0X
import time
import threading
import signal
import paho.mqtt.client as mqtt
import json
from multiprocessing.pool import ThreadPool

# my imports
import DoorLed
import RingLed
import MatrixLed
import MyCamera
import SerialHandler
import Servo
import RingWasteLed
import GreenGrass
import constants as c

GPIO.setmode(GPIO.BCM)

CURRENT_STATUS = "INIT"
OLD_STATUS = "NONE"

greengrass = True
aws_rekognition = True

#### VARS ####
timer_door = None
isOpen = False
oldIsOpen = False
is_running = False
wasteIn = False
oldWasteIn = False
deadToF1 = False
deadToF2 = False
total_iteration = 0

bin_json = {"bin_id": c.BIN_NAME,
            "levels": {"unsorted": 13,
                       "plastic": 3,
                       "paper": 10,
                       "glass": 8
                       }
            }


####### SIGNAL HANDLER ######
def signal_handler(signal, frame):
    print("Exit from smartbin!")
    doorLed.turnOff()
    ringLed.turnOff()
    matrixLed.turnOff()
    for r in wasteRings:
        r.setWaste(0)
    doorServo.openLid()
    sys.exit(0)


def on_message(client, userdata, message):
    print("receive message")
    response = str(message.payload.decode("utf-8"))
    print(response)
    if message.topic == c.FILL_LEVEL_FAKE:
        try:
            resp_parse = json.loads(response)
        except ValueError as e:
            print("malformed json")

        for key, val in resp_parse["levels"].items():
            bin_json["levels"][key] = val

        global CURRENT_STATUS

        if CURRENT_STATUS == "IDLE" or CURRENT_STATUS == "FULL" \
                or CURRENT_STATUS == "DOOR_OPEN" \
                or CURRENT_STATUS == "CHECK_TOF":
            CURRENT_STATUS = "SEND_FILL_LEVEL"

    if message.topic == c.FILL_LEVEL_TOPIC:
        if message.retain:
            for key, val in resp_parse["levels"].items():
                bin_json["levels"][key] = val


def on_connect(client, userdata, flags, rc):
    print("Connected flags" + str(flags) + "result_code" + str(rc) + "client1_id")
    client.subscribe(c.FILL_LEVEL_FAKE)


####### SETUP TOF #######
def setupToF(all_tof=True):
    GPIO.setwarnings(False)

    # Setup GPIO for shutdown pins on each VL53L0X
    GPIO.setup(c.SENSOR1, GPIO.OUT)
    GPIO.setup(c.SENSOR2, GPIO.OUT)

    # Set all shutdown pins low to turn off each VL53L0X
    GPIO.output(c.SENSOR1, GPIO.LOW)
    GPIO.output(c.SENSOR2, GPIO.LOW)

    time.sleep(0.50)

    tof = VL53L0X.VL53L0X(address=0x2B)
    tof1 = VL53L0X.VL53L0X(address=0x2D)

    GPIO.output(c.SENSOR1, GPIO.HIGH)
    time.sleep(0.50)
    tof.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)

    GPIO.output(c.SENSOR2, GPIO.HIGH)
    time.sleep(0.50)
    tof1.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)

    return tof, tof1


def door_callback(channel):
    global isOpen
    global CURRENT_STATUS, OLD_STATUS
    oldIsOpen = isOpen

    isOpen = GPIO.input(c.DOOR_SENSOR)
    if isOpen and not oldIsOpen:
        if (
                CURRENT_STATUS == "PHOTO" or CURRENT_STATUS == "MOTORS" or CURRENT_STATUS == "PHOTO_DONE" or CURRENT_STATUS == "REKOGNITION" or CURRENT_STATUS == "FULL" or CURRENT_STATUS == "SEND_FILL_LEVEL" or CURRENT_STATUS == "CHECK_FULL"):
            pass
        # print("ERROR!!!!!!")
        else:
            CURRENT_STATUS = "DOOR_OPEN"

    if not isOpen and oldIsOpen:
        if CURRENT_STATUS == "DOOR_OPEN" or CURRENT_STATUS == "CHECK_TOF":
            CURRENT_STATUS = "IDLE"
        if CURRENT_STATUS == "WASTE_IN" or CURRENT_STATUS == "WAIT_CLOSE":
            CURRENT_STATUS = "PHOTO"

        doorLed.turnOff()  # move up in current status idle (if door open)
        if timer_door is not None:
            if timer_door.is_alive():
                timer_door.cancel()


def photo_ready(my_cam):
    print("Taking a picture after the timer")
    global CURRENT_STATUS
    CURRENT_STATUS = "WAIT_CLOSE"


def door_forgotten_open():
    # status!
    print("Close the fockin door dude!")
    global isOpen
    doorLed.blink()
    while isOpen:
        # doorLed.blink()
        pass


def read_bin_level(tof):
    fill_lev = tof.get_distance()
    if fill_lev > 0:
        level = int((fill_lev / c.BIN_HEIGHT) * 100.0)
        if level > 100:
            level = 100
        return level


##### DOOR SETUP #####
GPIO.setup(c.DOOR_SENSOR, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(c.DOOR_SENSOR, GPIO.BOTH, callback=door_callback)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    print("STARTING SMARTBIN V{}...".format(c.VERSION))

    CURRENT_STATUS = "INIT"
    setup = True
    while setup:
        if CURRENT_STATUS == "INIT":
            print("\n### Current status: {}".format(CURRENT_STATUS))
            serialComm = SerialHandler.SerialHandler()

            print("Checking Door...")
            doorLed = DoorLed.DoorLed(serialComm.getSerialPort())
            doorLed.checkStatus()

            print("Checking Main Ring...")
            ringLed = RingLed.RingLed(serialComm.getSerialPort())
            ringLed.checkStatus()

            print("Checking Matrix...")
            matrixLed = MatrixLed.MatrixLed(serialComm.getSerialPort())
            matrixLed.checkStatus()

            print("Checking Rubbish Ring...")
            unsortedRing = RingWasteLed.RingWasteLed(serialComm.getSerialPort(), 'U')
            plasticRing = RingWasteLed.RingWasteLed(serialComm.getSerialPort(), 'P')
            paperRing = RingWasteLed.RingWasteLed(serialComm.getSerialPort(), 'C')
            glassRing = RingWasteLed.RingWasteLed(serialComm.getSerialPort(), 'G')

            blade = Servo.BladeServo()
            disk = Servo.DiskServo()

            calibration_blade = blade.calibration()
            calibration_disk = disk.calibration()

            tof1, tof2 = setupToF(False)

            wasteRings = [unsortedRing, plasticRing, paperRing, glassRing]
            for r in wasteRings:
                r.checkStatus()

            # MQTT
            print("\n")
            print("MQTT tentative connection...", end=' ')
            client = mqtt.Client()
            client.connect(c.HOST)
            client.on_message = on_message
            client.on_connect = on_connect

            client.loop_start()
            print("DONE")

            # reko = Rekognition.Rekognition(debug=True)

            print("MQTT tentative connection...", end=' ')
            gg = GreenGrass.GreenGrass()
            print("DONE")

            matrixLed.greenArrow()

            camera = MyCamera.MyCamera()

            doorServo = Servo.DoorServo()

            pool = ThreadPool(processes=1)

            CURRENT_STATUS = "CHECK_INIT"

        elif CURRENT_STATUS == "CHECK_INIT":
            print("\n### Current status: {}".format(CURRENT_STATUS))

            errors = []
            if not camera.checkStatus():
                errors.append("CAMERA")
            if not serialComm.checkStatus():
                errors.append("SERIAL")

            if not tof1.checkStatus("2b"):
                errors.append("TOF1")
            if not tof2.checkStatus("2d"):
                errors.append("TOF2")

            while not calibration_disk:
                print("wait disk calibration")
            while not calibration_blade:
                print("wait blade calibration")

            # if no errors set current status = boot
            if len(errors) < 1:
                CURRENT_STATUS = "BOOT"
            else:
                CURRENT_STATUS = "INIT_ERROR"

        elif CURRENT_STATUS == "BOOT":
            print("\n### Current status: {}".format(CURRENT_STATUS))

            isOpen = GPIO.input(c.DOOR_SENSOR)
            startUp = True

            if isOpen:
                CURRENT_STATUS = "DOOR_OPEN_ERROR"
            else:
                CURRENT_STATUS = "BOOT_DONE"

        # END BOOT

        elif CURRENT_STATUS == "DOOR_OPEN_ERROR":
            print("\n### Current status: {}".format(CURRENT_STATUS))
            ringLed.staticRed()
            matrixLed.redCross()
            while isOpen:
                if startUp:
                    print("--> close the front door to boot the smartbin")
                    doorLed.blink()
                    startUp = False

            CURRENT_STATUS = "BOOT_DONE"

        elif CURRENT_STATUS == "BOOT_DONE":
            print("\n### Current status: {}".format(CURRENT_STATUS))
            print("--> boot...")
            is_running = True
            setup = False
            ringLed.staticGreen()
            matrixLed.greenArrow()
            # doorLed.turnOff()
            blade.move_blade("HOME")
            disk.moveDisk("HOME")
            CURRENT_STATUS = "READ_FILL_LEVEL"

        elif CURRENT_STATUS == "INIT_ERROR":
            print("GODDAMN!")
            print("errors come from {}".format(errors))
            print("restart")
            sys.exit()

    #### START SMARTBIN ####
    while is_running:
        if OLD_STATUS is not CURRENT_STATUS:
            print("\n### Current status: {} - old {}".format(CURRENT_STATUS, OLD_STATUS))

        OLD_STATUS = CURRENT_STATUS
        # if(CURRENT_STATUS != "IDLE"):
        #	print("delete idle timer")
        #	if(len(timer_idle) > 0):
        #		timer_idle[0].cancel()

        ##### DOOR_OPEN ######
        if CURRENT_STATUS == "DOOR_OPEN":
            # global timer_door
            doorLed.turnOn()
            timer_door = threading.Timer(c.TIMER_DOOR, door_forgotten_open)
            timer_door.start()
            CURRENT_STATUS = "CHECK_TOF"

        ##### CHECK_TOF #####
        if CURRENT_STATUS == "CHECK_TOF":
            # TODO: create an array with last N values and check whether there are outliers
            distance1 = tof1.get_distance()
            distance2 = tof2.get_distance()

            # print(distance1, distance2)

            if distance1 < 0:
                distance1 = 666
                deadToF1 = True
                print("tof1 dead, restart")

            if distance2 < 0:
                distance2 = 666
                deadToF2 = True
                print("tof2 dead, restart")

            if deadToF1 or deadToF2:
                CURRENT_STATUS = "WASTE_IN"

            oldWasteIn = wasteIn
            if distance1 < c.THRESHOLD_TOF or distance2 < c.THRESHOLD_TOF:
                CURRENT_STATUS = "WASTE_IN"


        ##### WASTE IN #####
        elif CURRENT_STATUS == "WASTE_IN":
            print("Rubbish inside")
            camera.setCameraStatus(False)
            camera.erasePath()
            timer_pic = threading.Timer(c.TIMER_PHOTO, photo_ready, [camera])
            timer_pic.start()
            CURRENT_STATUS = "WAIT_CLOSE"


        ##### WAIT CLOSE #####
        elif CURRENT_STATUS == "WAIT_CLOSE":
            pass


        ##### PHOTO #####
        elif CURRENT_STATUS == "PHOTO":
            for r in wasteRings:
                r.turnOffRing()
            doorLed.turnOn()
            print("Close the front door")
            doorServo.closeLid()
            print("Front door is closed: taking picture")
            timer_pic.cancel()
            camera.takePhoto()
            doorLed.turnOff()
            CURRENT_STATUS = "PHOTO_DONE"



        ##### PHOTO DONE #####
        elif CURRENT_STATUS == "PHOTO_DONE":
            CURRENT_STATUS = "REKOGNITION"


        ##### REKOGNITION #####
        elif CURRENT_STATUS == "REKOGNITION":

            waste_type_gg = "TIMEOUT"
            waste_type_aws = "UNSORTED"

            if greengrass:
                async_result = pool.apply_async(gg.getLabels, (camera.currentPath(),))

            if aws_rekognition:
                # waste_type_aws = reko.getLabels(camera.currentPath())
                print("REKO: rubbish identified, it's: {}. Innit?".format(waste_type_aws))

            if greengrass:
                waste_type_gg = async_result.get()
                print("GG: rubbish identified, it's: {}. Innit?".format(waste_type_gg))

            # waste_type = waste_type_aws
            if waste_type_gg == "TIMEOUT" or not greengrass:
                # if(waste_type_aws is not None):
                # waste_type = waste_type_aws
                # print("this is AWS")
                # else:
                waste_type = "UNSORTED"
            else:
                waste_type = waste_type_gg
                print("This is Greengrass")

            if waste_type == "UNSORTED":
                unsortedRing.setWaste(333)
                bin_json["levels"]["unsorted"] += 2
                if bin_json["levels"]["unsorted"] > 100:
                    bin_json["levels"]["unsorted"] = 100

            elif waste_type == "PLASTIC":
                plasticRing.setWaste(333)
                bin_json["levels"]["plastic"] += 2
                if bin_json["levels"]["plastic"] > 100:
                    bin_json["levels"]["plastic"] = 100

            elif waste_type == "PAPER":
                paperRing.setWaste(333)
                bin_json["levels"]["paper"] += 2
                if bin_json["levels"]["paper"] > 100:
                    bin_json["levels"]["paper"] = 100

            elif waste_type == "GLASS":
                glassRing.setWaste(333)
                bin_json["levels"]["glass"] += 2
                if bin_json["levels"]["glass"] > 100:
                    bin_json["levels"]["glass"] = 100

            if waste_type == "EMPTY":
                CURRENT_STATUS = "SET_FILL_LEVEL"
                doorServo.openLid()
            else:
                CURRENT_STATUS = "MOTORS"


        ##### MOTORS #####
        elif CURRENT_STATUS == "MOTORS":
            print("Activate motors")
            total_iteration += 1

            # go
            blade.move_blade(waste_type)
            time.sleep(.2)
            disk.moveDisk(waste_type)
            print("Turning on the LEDs")
            ringLed.breatheGreen()
            time.sleep(1.8)

            # way back
            disk.moveDisk("HOME")
            blade.move_blade("HOME")
            time.sleep(1.5)
            print("Action done")

            for r in wasteRings:
                r.turnOffRing()
            CURRENT_STATUS = "SEND_FILL_LEVEL"


        ##### READ WASTE #####
        elif CURRENT_STATUS == "READ_FILL_LEVEL":
            for key in bin_json["levels"].keys():
                if key == "unsorted":
                    pass
                # fill_levels[key] = read_bin_level(tof_unsorted)
                if key == "plastic":
                    pass
                # fill_levels[key] = read_bin_level(tof_plastic)
                if key == "paper":
                    pass
                if key == "glass":
                    pass

            for key, val in bin_json["levels"].items():
                print("{}: {}".format(key, val))

            CURRENT_STATUS = "SEND_FILL_LEVEL"

        elif CURRENT_STATUS == "SEND_FILL_LEVEL":
            client.publish(c.FILL_LEVEL_TOPIC, json.dumps(bin_json), retain=True, qos=1)
            CURRENT_STATUS = "CHECK_FULL"

        elif CURRENT_STATUS == "CHECK_FULL":
            full_bin = []
            for key, value in bin_json["levels"].items():
                if value >= 100:
                    full_bin.append(key)

            if len(full_bin) < 1:
                CURRENT_STATUS = "SET_FILL_LEVEL"
            else:
                first_full = True
                CURRENT_STATUS = "FULL"

        elif CURRENT_STATUS == "SET_FILL_LEVEL":
            ringLed.staticGreen()
            matrixLed.greenArrow()
            doorServo.openLid()
            print("this is the {} iteration".format(total_iteration))
            for key in bin_json["levels"].keys():
                if key == "unsorted":
                    unsortedRing.setWaste(bin_json["levels"][key])
                if key == "paper":
                    plasticRing.setWaste(bin_json["levels"][key])
                if key == "plastic":
                    paperRing.setWaste(bin_json["levels"][key])
                if key == "glass":
                    glassRing.setWaste(bin_json["levels"][key])

            CURRENT_STATUS = "IDLE"
            first_idle = True

        elif CURRENT_STATUS == "FULL":
            if first_full:
                for r in wasteRings:
                    r.turnOffRing()
                doorServo.closeLid()
                ringLed.staticRed()
                matrixLed.redCross()
                for f in full_bin:
                    if f == "unsorted":
                        unsortedRing.setWaste(100)
                    if f == "paper":
                        plasticRing.setWaste(100)
                    if f == "plastic":
                        paperRing.setWaste(100)
                    if f == "glass":
                        glassRing.setWaste(100)
                client.publish("smartbin/message/bin0", "I'm full")
                first_full = False

        ##### IDLE #####
        elif CURRENT_STATUS == "IDLE":
            if first_idle:
                # print("timer")
                # timer_idle.append(threading.Timer(c.TIMER_IDLE, activate_wipe))
                first_idle = False
                if GPIO.input(c.DOOR_SENSOR):
                    CURRENT_STATUS = "DOOR_OPEN"
            if deadToF1 and deadToF2:
                # reset tof
                doorServo.closeLid()
                tof1.stop_ranging()
                tof2.stop_ranging()
                tof1, tof2 = setupToF(all_tof=False)
                deadToF1 = False
                deadToF2 = False
                doorServo.openLid()
            else:
                pass

    print("EOF!")
    tof2.stop_ranging()
    GPIO.output(c.SENSOR2, GPIO.LOW)
    tof1.stop_ranging()
    GPIO.output(c.SENSOR1, GPIO.LOW)
    ringLed.staticRed()
