import serial


class DoorLed():
	def __init__(self, ser):
		self.ser = ser
	
	def turnOff(self):
		try:
			self.ser.write(b'#D0!')
			print("DOOR: spengo luci porta")
		except serial.SerialException as e:
			print("DOOR ERROR: spengo luci porta {}".format(e))

	def turnOn(self):
		try: 
			self.ser.write(b'#D1!')
			print("DOOR: accendo luci porta")
		except serial.SerialException as e:
			print("DOOR ERROR: accendo luci porta {}".format(e))

	def blink(self):
		try:
			self.ser.write(b'#D2!')
			print("DOOR: lampeggio porta (errore)")
		except serial.SerialException as e:
			print("DOOR ERROR: lampeggio luci porta {}".format(e))

	def checkStatus(self):
		pass
