import logging
import serial


logger = logging.getLogger("SERIAL")


class SerialHandler:
    def __init__(self):
        self.dev = 0
        self._init_serial()

        if self.ser is not None:
            self.ser.flushInput()
            self.serialStatus = True

            logger.debug("Open serial communication on serial port %s", self.ser.port)
        else:
            logger.critical("Impossible to open the serial communication")
            self.serialStatus = False

    def _init_serial(self):
        try:
            self.ser = serial.Serial("/dev/ttyACM" + str(self.dev), 9600)
        except serial.SerialException as e:
            logger.error("%s", e)
            self.dev += 1
            if self.dev < 5:
                self._init_serial()
            else:
                logger.critical("NO arduino available")
                self.ser = None

    def getSerialPort(self):
        return self.ser

    def isRunning(self):
        return self.serialStatus

    def checkStatus(self):
        if self.ser is None:
            return False

        return True
