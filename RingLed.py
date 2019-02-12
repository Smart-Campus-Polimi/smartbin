import serial


class RingLed():
	def __init__(self, ser):
		self.ser = ser
	
	def turnOff(self):
		self.ser.write(b'#R0!')
		print("spengo ring")

	def staticGreen(self):
		self.ser.write(b'#R1!')
		print("led green")

	def staticRed(self):
		self.ser.write(b'#R2!')
		print("led red")

	def breatheGreen(self):
		self.ser.write(b'#R3!')
		print("led breathe green")

	def breatheRed(self):
		self.ser.write(b'#R4!')
		print("led breathe red")

	def checkStatus(self):
		pass
