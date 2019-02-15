import serial


class RingLed():
	def __init__(self, ser):
		self.ser = ser
	
	def turnOff(self):
		self.ser.write(b'#R0!')
		print("RING: spengo ring")

	def staticGreen(self):
		#self.ser.write(b'#R1!')
		print("RING: led green")

	def staticRed(self):
		#self.ser.write(b'#R2!')
		print("RING: led red")

	def breatheGreen(self):
		#self.ser.write(b'#R3!')
		print("RING: led breathe green")

	def breatheRed(self):
		#self.ser.write(b'#R4!')
		print("RING: led breathe red")

	def checkStatus(self):
		pass

	def waitingForToF(self):
		pass

	def ToFRunning(self):
		pass

	def ToFNOTRunning(self):
		#differenciate
		pass
