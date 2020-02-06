import serial


class MatrixLed:
	def __init__(self, ser):
		self.ser = ser
	
	def turnOff(self):
		try:
			self.ser.write(b'#M0!')
			print("MATRIX: turn off matrix")
		except serial.SerialException as e:
			print("MATRIX: turn off matrix {}".format(e))

	def greenArrow(self):
		try:
			self.ser.write(b'#M0!')
			self.ser.write(b'#M1!')
			print("MATRIX: green arrow")
		except serial.SerialException as e:
			print("MATRIX ERROR: green arrow {}".format(e))

	def redCross(self):
		try:
			self.ser.write(b'#M0!')
			self.ser.write(b'#M2!')
			print("MATRIX: red cross")
		except serial.SerialException as e:
			print("MATRIX ERROR: red cross {}".format(e))

	def arrowAnimation(self):
		try:
			self.ser.write(b'#M0!')
			self.ser.write(b'#M3!')
			print("MATRIX: arrow animation")
		except serial.SerialException as e:
			print("MATRIX ERROR: arrow animation {}".format(e))
		
	def checkStatus(self):
		pass
