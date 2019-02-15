import serial


class MatrixLed():
	def __init__(self, ser):
		self.ser = ser
	
	def turnOff(self):
		#self.ser.write(b'#M0!')
		print("MATRIX: spengo matrix")

	def greenArrow(self):
		#self.ser.write(b'#M1!')
		print("MATRIX: green arrow")

	def redCross(self):
		#self.ser.write(b'#M2!')
		print("MATRIX: red matrix")

	def arrowAnimation(self):
		self.ser.write(b'#M3!')
		

	def checkStatus(self):
		pass
