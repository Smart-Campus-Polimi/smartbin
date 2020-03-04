import logging
import time

import RPi.GPIO as GPIO
import pigpio
import yaml
from munch import munchify


logger = logging.getLogger("MOTOR")


GPIO.setmode(GPIO.BCM)
with open('motors.yaml', 'r') as conf_yaml:
    CONFIG = munchify(yaml.load(conf_yaml, yaml.SafeLoader))


# TODO merge blade and disk in a single class
class BladeServo:
    def __init__(self, config):
        self.pin_config = config
        self.servo = pigpio.pi()
        GPIO.setup(self.pin_config.magnet, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.servo.set_servo_pulsewidth(self.pin_config.motor, CONFIG.blade.init)
        self.zero_blade = CONFIG.blade.init
        logger.debug("BLADE: initialization Done")

    def calibration(self):
        for pos in range(CONFIG.blade.init, CONFIG.max):
            if GPIO.input(self.pin_config.magnet):
                self.servo.set_servo_pulsewidth(self.pin_config.motor, pos)
                time.sleep(.02)
            else:
                self.zero_blade = pos + CONFIG.blade.offset
                break

        if self.zero_blade == CONFIG.blade.init:
            logger.critical("BLADE: calibration failed")
            self.zero_blade = CONFIG.blade.correct

        self.servo.set_servo_pulsewidth(self.pin_config.motor, self.zero_blade)
        logger.debug("BLADE: Zero pos blade is : %s", self.zero_blade)

        return True

    def move_blade(self, waste):
        self.servo.set_servo_pulsewidth(self.pin_config.motor, self._parse_blade(waste))

    def _parse_blade(self, waste):
        if waste == "UNSORTED":
            pos = self.zero_blade + CONFIG.blade.rubbish.unsorted
        elif waste == "PLASTIC":
            pos = self.zero_blade + CONFIG.blade.rubbish.plastic
        elif waste == "PAPER":
            pos = self.zero_blade + CONFIG.blade.rubbish.paper
        elif waste == "GLASS":
            pos = self.zero_blade + CONFIG.blade.rubbish.glass
        elif waste == "HOME":
            pos = self.zero_blade
        else:
            pos = self.zero_blade

        logger.debug("BLADE: %s", pos)
        return pos


class DiskServo:
    def __init__(self, config):
        self.pin_config = config
        self.servo = pigpio.pi()
        GPIO.setup(self.pin_config.magnet, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.servo.set_servo_pulsewidth(self.pin_config.motor, CONFIG.disk.init)
        self.zero_disk = CONFIG.disk.init
        logger.debug("DISK: initialization Done")

    def calibration(self):
        for pos in range(CONFIG.disk.init, CONFIG.max):
            if GPIO.input(self.pin_config.magnet):
                self.servo.set_servo_pulsewidth(self.pin_config.motor, pos)
                time.sleep(.02)
            else:
                self.zero_disk = pos + CONFIG.disk.offset
                break

        if self.zero_disk == CONFIG.disk.init:
            logger.critical("DISK: calibration failed")
            self.zero_disk = CONFIG.disk.correct

        self.servo.set_servo_pulsewidth(self.pin_config.motor, self.zero_disk)
        logger.debug("DISK: Zero pos disk is : %s", self.zero_disk)
        return True

    def moveDisk(self, waste):
        self.servo.set_servo_pulsewidth(self.pin_config.motor, self._parseDisk(waste))

    def _parseDisk(self, waste):
        if waste == "UNSORTED":
            pos = self.zero_disk + CONFIG.disk.rubbish.unsorted
        elif waste == "PLASTIC":
            pos = self.zero_disk + CONFIG.disk.rubbish.unsorted
        elif waste == "PAPER":
            pos = self.zero_disk + CONFIG.disk.rubbish.unsorted
        elif waste == "GLASS":
            pos = self.zero_disk + CONFIG.disk.rubbish.unsorted
        elif waste == "HOME":
            pos = self.zero_disk
        else:
            pos = CONFIG.disk.init

        logger.debug("DISK: %s", pos)
        return pos


def stopServo():
    logger.debug("Stop the servo")
    # self.servo.stop()


class DoorServo:
    def __init__(self, config):
        self.servo = pigpio.pi()
        self.pin_config = config
        self.servo.set_servo_pulsewidth(self.pin_config.motor, CONFIG.door.open)
        logger.debug("DOOR: initialization Done")

        time.sleep(.5)
        self.closeLid()
        time.sleep(.5)
        self.openLid()

    def getServo(self):
        return self.servo

    def openLid(self):
        logger.debug("DOOR: open the door")
        self.servo.set_servo_pulsewidth(self.pin_config.motor, CONFIG.door.open)

    def closeLid(self):
        logger.debug("DOOR: close the door")
        self.servo.set_servo_pulsewidth(self.pin_config.motor, CONFIG.door.closed)
