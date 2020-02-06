import serial


class RingWasteLed:
	def __init__(self, ser, waste_type):
		self.ser = ser
		self.waste_type = waste_type
	
	def setWaste(self, value):
		msg = '#'+self.waste_type+str(value)+'!'
		try:
			self.ser.write(str.encode(msg))
			print("WASTE: set {} to {}%".format(self.waste_type, value))
		except serial.SerialException as e:
			print("WASTE ERROR: set to level {}".format(e))
	
	def turnOffRing(self):
		msg = '#'+self.waste_type+'0!'
		try:
			self.ser.write(str.encode(msg))
		except serial.SerialException as e:
			print("WASTE ERROR: set to level {}".format(e))
	
	def checkStatus(self):
		pass
