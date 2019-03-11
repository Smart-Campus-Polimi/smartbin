import RPi.GPIO as GPIO
import time
import pigpio

DOOR_MOTOR = 17
DISK_MOTOR = 24
PALETTA_MOTOR = 25


MOTOR_OPEN = 1500
MOTOR_CLOSED = 900

DISK_INIT = 1500
PALETTA_INIT = 1500

PALETTA_UNSORTED = +60
PALETTA_PLASTIC = -60
PALETTA_PAPER = +150
PALETTA_GLASS = -150

DISK_UNSORTED = +60
DISK_PLASTIC = -60
DISK_PAPER = +150
DISK_GLASS = -150

class PalettaServo():
	def __init__(self):
		self.servo = pigpio.pi()
		
		self.servo.set_servo_pulsewidth(PALETTA_MOTOR, PALETTA_INIT)
		self.zero_paletta = PALETTA_INIT
		print("SERVO: initialization Done")
		
	def movePaletta(self, waste):
		self.servo.set_servo_pulsewidth(PALETTA_MOTOR, self._parsePaletta(waste))
	
	def _parsePaletta(self, waste):
		if(waste == "UNSORTED"):
			pos = self.zero_paletta + PALETTA_UNSORTED
		elif(waste == "PLASTIC"):
			pos = self.zero_paletta + PALETTA_PLASTIC
		elif(waste == "PAPER"):
			pos = self.zero_paletta + PALETTA_PAPER
		elif(waste == "GLASS"):
			pos = self.zero_paletta + PALETTA_GLASS
		elif(waste == "HOME"):
			pos = self.zero_paletta
		else:
			pos = self.zero_paletta
			
		return pos
		
class DiskServo():
	def __init__(self):
		self.servo = pigpio.pi()
		
		self.servo.set_servo_pulsewidth(DISK_MOTOR, DISK_INIT)
		self.zero_disk = DISK_INIT
		print("SERVO: initialization Done")
		
	def moveDisk(self, waste):
		self.servo.set_servo_pulsewidth(DISK_MOTOR, self._parseDisk(waste))
	
	def _parseDisk(self, waste):
		if(waste == "UNSORTED"):
			pos = self.zero_disk + DISK_UNSORTED
		elif(waste == "PLASTIC"):
			pos = self.zero_disk + DISK_PLASTIC
		elif(waste == "PAPER"):
			pos = self.zero_disk + DISK_PAPER
		elif(waste == "GLASS"):
			pos = self.zero_disk + DISK_GLASS
		elif(waste == "HOME"):
			pos = self.zero_disk
		else:
			pos = DISK_INIT
			
		return pos

class DoorServo():
	def __init__(self):
		self.servo = pigpio.pi()
		
		self.servo.set_servo_pulsewidth(DOOR_MOTOR, MOTOR_OPEN)
		print("SERVO: initialization Done")
		
		time.sleep(.5)
		self.closeLid()
		time.sleep(.5)
		self.openLid()	
			
	def getServo(self):
		return self.servo

	def stopServo(self):
		print("SERVO: stop the servo")
		#self.servo.stop()

	def openLid(self):
		print("SERVO: open the door")
		self.servo.set_servo_pulsewidth(DOOR_MOTOR, MOTOR_OPEN)

	def closeLid(self):
		print("SERVO: close the door")
		self.servo.set_servo_pulsewidth(DOOR_MOTOR, MOTOR_CLOSED)

