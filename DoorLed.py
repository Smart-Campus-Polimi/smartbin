import serial


class DoorLed:
	def __init__(self, ser):
		self.ser = ser
	
	def turnOff(self):
		try:
			self.ser.write(b'#D0!')
			print("DOOR: turn off door lights")
		except serial.SerialException as e:
			print("DOOR ERROR: turn off door lights {}".format(e))

	def turnOn(self):
		try: 
			self.ser.write(b'#D1!')
			print("DOOR: turn on door lights")
		except serial.SerialException as e:
			print("DOOR ERROR: turn on door lights {}".format(e))

	def blink(self):
		try:
			self.ser.write(b'#D2!')
			print("DOOR: door blink (error)")
		except serial.SerialException as e:
			print("DOOR ERROR: door blink {}".format(e))

	def checkStatus(self):
		pass
