import serial
import logging

logger = logging.getLogger("DOOR")


class DoorLed:
    def __init__(self, ser):
        self.ser = ser

    def turnOff(self):
        try:
            self.ser.write(b'#D0!')
            logger.debug("Turn off lights")
        except serial.SerialException as e:
            logger.critical("Turn off lights %s", e)

    def turnOn(self):
        try:
            self.ser.write(b'#D1!')
            logger.debug("Turn on lights")
        except serial.SerialException as e:
            logger.critical("Turn on lights %s", e)

    def blink(self):
        try:
            self.ser.write(b'#D2!')
            logger.warning("Blink")
        except serial.SerialException as e:
            logger.critical("Blink %s", e)

    def checkStatus(self):
        logger.debug("Checking Door...")
        pass
