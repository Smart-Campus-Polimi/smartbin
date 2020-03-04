import logging
import serial


logger = logging.getLogger("RING")


class RingLed:
    def __init__(self, ser):
        self.ser = ser

    def turnOff(self):
        try:
            self.ser.write(b'#R0!')
            logger.debug("Turn off")
        except serial.SerialException as e:
            logger.error("Turn off %s", e)

    def staticGreen(self):
        try:
            self.ser.write(b'#R1!')
            logger.debug("Green")
        except serial.SerialException as e:
            logger.error("Green %s", e)

    def staticRed(self):
        try:
            self.ser.write(b'#R2!')
            logger.warning("Red")
        except serial.SerialException as e:
            logger.error("Red %s", e)

    def breatheGreen(self):
        try:
            self.ser.write(b'#R3!')
            logger.debug("Breathe green")
        except serial.SerialException as e:
            logger.error("Breathe green %s", e)

    def breatheRed(self):
        try:
            self.ser.write(b'#R4!')
            logger.warning("Breathe red")
        except serial.SerialException as e:
            logger.debug("Breathe red %s", e)

    def wipeRing(self):
        try:
            self.ser.write(b'#R7!')
            logger.debug("Wipe")
        except serial.SerialException as e:
            logger.debug("Wipe %s", e)

    def checkStatus(self):
        logger.debug("Checking Main Ring...")
        pass

    def waitingForToF(self):
        # TODO
        pass

    def ToFRunning(self):
        # TODO
        pass

    def ToFNOTRunning(self):
        # TODO
        pass
