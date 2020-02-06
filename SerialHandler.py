import serial


class SerialHandler:
    def __init__(self):
        self.dev = 0
        self._init_serial()

        if self.ser is not None:
            self.ser.flushInput()
            self.serialStatus = True

            print("SERIAL: Open serial communication on serial port {}".format(self.ser.port))
        else:
            print("SERIAL: Impossible to open the serial communication")
            self.serialStatus = False

    def _init_serial(self):
        try:
            self.ser = serial.Serial("/dev/ttyACM" + str(self.dev), 9600)
        except serial.SerialException as e:
            print("SERIAL: Catch serial exception {}".format(e))
            self.dev += 1
            if self.dev < 5:
                self._init_serial()
            else:
                print("SERIAL: NO ARDUINO FOUND! Error very very big")
                self.ser = None

    def getSerialPort(self):
        return self.ser

    def isRunning(self):
        return self.serialStatus

    def checkStatus(self):
        if self.ser is None:
            return False

        return True
