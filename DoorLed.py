import serial

class DoorLed():
	def __init__(self):
		self.ser = serial.Serial("/dev/ttyACM0", 9600)
		self.ser.flushInput()
		self.open = False
		self.oldOpen = False

	def turnOff(self):
		self.ser.write(b'#D0!')
		print("spengo luci porta")

	def turnOn(self):
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
