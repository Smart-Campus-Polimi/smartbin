import serial


class MatrixLed():
	def __init__(self, ser):
		self.ser = ser
	
	def turnOff(self):
		self.ser.write(b'#M0!')
		print("spengo matrix")

	def greenArrow(self):
		self.ser.write(b'#M1!')
		print("green arrow")

	def redCross(self):
		self.ser.write(b'#M2!')
		print("red matrix")

	def arrowAnimation(self):
		self.ser.write(b'#M3!')
		

	def checkStatus(self):
		pass
