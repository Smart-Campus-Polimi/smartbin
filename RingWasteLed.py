import logging
import serial


logger = logging.getLogger("WASTE")


class RingWasteLed:
    def __init__(self, ser, waste_type):
        self.ser = ser
        self.waste_type = waste_type

    def setWaste(self, value):
        msg = '#' + self.waste_type + str(value) + '!'
        try:
            self.ser.write(str.encode(msg))
            logger.debug("Set %s to %d%%", self.waste_type, value)
        except serial.SerialException as e:
            logger.error("Set to level %s", e)

    def turnOffRing(self):
        msg = '#' + self.waste_type + '0!'
        try:
            self.ser.write(str.encode(msg))
        except serial.SerialException as e:
            logger.error("Off ring %s", e)

    def checkStatus(self):
        logger.debug("Checking Rubbish Ring...")
        pass
