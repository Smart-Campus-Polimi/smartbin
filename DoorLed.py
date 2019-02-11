import serial


class DoorLed():
	def __init__(self):
		self.dev = 0
		self._initSerial()
		print("serial dev {}".format(self.ser))
		if(self.ser is not  None):
			self.ser.flushInput()
			self.open = False
			self.oldOpen = False
			
	def _initSerial(self):
		try: 
			self.ser = serial.Serial("/dev/ttyACM"+str(self.dev), 9600)
			
		except serial.SerialException as e:
			print("Catch serial exception {}".format(e))
			self.dev += 1
			if(self.dev < 5):
				self._initSerial()
			else:
				print("NO ARDUINO FOUND! Error very very big")
				self.ser = None

	def turnOff(self):
		self.ser.write(b'#D0!')
		print("spengo luci porta")

	def turnOn(self):
		print(self.ser)
		self.ser.write(b'#D1!')
		print("accendo luci porta")

	def blink(self):
		self.ser.write(b'#D2!')
		print("lampeggio porta (errore)")


### maybe ###
	def setDoor(self, value):
		self.oldOpen = self.open
		self.open = value

	def isOpen():
		return self.isOpen

	def oldIsOpen():
		return self.oldOpen
