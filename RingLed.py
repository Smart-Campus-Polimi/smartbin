import serial


class RingLed():
	def __init__(self, ser):
		self.ser = ser
	
	def turnOff(self):
		try:
			self.ser.write(b'#R0!')
			print("RING: spengo ring")
		except serial.SerialException as e:
			print("RING ERROR: spengo ring {}".format(e))

	def staticGreen(self):
		try: 
			self.ser.write(b'#R1!')
			print("RING: led green")
		except serial.SerialException as e:
			print("RING ERROR: led green {}".format(e))

	def staticRed(self):
		try:
			self.ser.write(b'#R2!')
			print("RING: led red")
		except serial.SerialException as e:
			print("RING ERROR: led red {}".format(e))

	def breatheGreen(self):
		try:
			self.ser.write(b'#R3!')
			print("RING: led breathe green")
		except serial.SerialException as e:
			print("RING ERROR: led breathe green {}".format(e))

	def breatheRed(self):
		try:
			self.ser.write(b'#R4!')
			print("RING: led breathe red")
		except serial.SerialException as e:
			print("RING ERROR: led breathe red {}".format(e))

	def checkStatus(self):
		pass

	def waitingForToF(self):
		pass

	def ToFRunning(self):
		pass

	def ToFNOTRunning(self):
		#differenciate
		pass
