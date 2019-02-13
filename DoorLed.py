import serial


class DoorLed():
	def __init__(self, ser):
		self.ser = ser
	
	def turnOff(self):
		self.ser.write(b'#D0!')
		print("spengo luci porta")

	def turnOn(self):
		self.ser.write(b'#D1!')
		print("accendo luci porta")

	def blink(self):
		self.ser.write(b'#D2!')
		print("lampeggio porta (errore)")

	def checkStatus(self):
		pass
