import logging
import serial

logger = logging.getLogger("MATRIX")


class MatrixLed:
    def __init__(self, ser):
        self.ser = ser

    def turnOff(self):
        try:
            self.ser.write(b'#M0!')
            logger.debug("Turn off")
        except serial.SerialException as e:
            logger.error("Turn off %s", e)

    def greenArrow(self):
        try:
            self.ser.write(b'#M0!')
            self.ser.write(b'#M1!')
            logger.debug("Green arrow")
        except serial.SerialException as e:
            logger.error("Green arrow %s", e)

    def redCross(self):
        try:
            self.ser.write(b'#M0!')
            self.ser.write(b'#M2!')
            logger.warning("Red cross")
        except serial.SerialException as e:
            logger.error("Red cross %s", e)

    def arrowAnimation(self):
        try:
            self.ser.write(b'#M0!')
            self.ser.write(b'#M3!')
            logger.debug("Arrow animation")
        except serial.SerialException as e:
            logger.debug("Arrow animation %s", e)

    def checkStatus(self):
        logger.debug("Checking Matrix...")
        pass
