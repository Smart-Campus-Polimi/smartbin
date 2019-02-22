import serial


class RingWasteLed():
	def __init__(self, ser, waste_type):
		self.ser = ser
		self.waste_type = waste_type
	
	def setWaste(self, value):
		try:
			self.ser.write(bytes('#'+self.waste_type+str(value)+'!', encoding='utf-8'))
			print("WASTE: set {} to {}%".format(self.waste_type, value))
		except serial.SerialException as e:
			print("WASTE ERROR: set to level {}".format(e))

	def checkStatus(self):
		pass
