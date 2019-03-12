import RPi.GPIO as GPIO
import time
import pigpio
import motors_constants as m

GPIO.setmode(GPIO.BCM)

class PalettaServo():
	def __init__(self):
		self.servo = pigpio.pi()
		GPIO.setup(m.PIN_MAGNET_PALETTA, GPIO.IN, pull_up_down = GPIO.PUD_UP)
		self.servo.set_servo_pulsewidth(m.PALETTA_MOTOR, m.PALETTA_INIT)
		self.zero_paletta = m.PALETTA_INIT
		print("SERVO: initialization Done")

	def calibration(self):
		for pos in range(m.PALETTA_INIT, m.MAX_MOTOR):
			if(GPIO.input(m.PIN_MAGNET_PALETTA)):
				self.servo.set_servo_pulsewidth(m.PALETTA_MOTOR, pos)
				time.sleep(.02)
			else:
				self.zero_paletta = pos + m.OFFSET_PALETTA
				break
		
		self.servo.set_servo_pulsewidth(m.PALETTA_MOTOR, self.zero_paletta)
		print("PALETTA: Zero pos paletta is : {}".format(self.zero_paletta))

		return True


	def movePaletta(self, waste):
		self.servo.set_servo_pulsewidth(m.PALETTA_MOTOR, self._parsePaletta(waste))

	def _parsePaletta(self, waste):
		if(waste == "UNSORTED"):
			pos = self.zero_paletta + m.PALETTA_UNSORTED
		elif(waste == "PLASTIC"):
			pos = self.zero_paletta + m.PALETTA_PLASTIC
		elif(waste == "PAPER"):
			pos = self.zero_paletta + m.PALETTA_PAPER
		elif(waste == "GLASS"):
			pos = self.zero_paletta + m.PALETTA_GLASS
		elif(waste == "HOME"):
			pos = self.zero_paletta
		else:
			pos = self.zero_paletta
			
		return pos
		
class DiskServo():
	def __init__(self):
		self.servo = pigpio.pi()
		GPIO.setup(m.PIN_MAGNET_DISK, GPIO.IN, pull_up_down = GPIO.PUD_UP)
		self.servo.set_servo_pulsewidth(m.DISK_MOTOR, m.DISK_INIT)
		self.zero_disk = m.DISK_INIT
		print("SERVO: initialization Done")
		
	def calibration(self):
		for pos in range(m.DISK_INIT, m.MAX_MOTOR):
			if(GPIO.input(m.PIN_MAGNET_DISK)):
				self.servo.set_servo_pulsewidth(m.DISK_MOTOR, pos)
				time.sleep(.02)
			else:
				self.zero_disk = pos + m.OFFSET_DISK
				break
		
		self.servo.set_servo_pulsewidth(m.DISK_MOTOR, self.zero_disk)
		print("DISK: Zero pos disk is : {}".format(self.zero_disk))
		return True

	def moveDisk(self, waste):
		self.servo.set_servo_pulsewidth(m.DISK_MOTOR, self._parseDisk(waste))
	
	def _parseDisk(self, waste):
		if(waste == "UNSORTED"):
			pos = self.zero_disk + m.DISK_UNSORTED
		elif(waste == "PLASTIC"):
			pos = self.zero_disk + m.DISK_PLASTIC
		elif(waste == "PAPER"):
			pos = self.zero_disk + m.DISK_PAPER
		elif(waste == "GLASS"):
			pos = self.zero_disk + m.DISK_GLASS
		elif(waste == "HOME"):
			pos = self.zero_disk
		else:
			pos = m.DISK_INIT
			
		return pos

class DoorServo():
	def __init__(self):
		self.servo = pigpio.pi()
		
		self.servo.set_servo_pulsewidth(m.DOOR_MOTOR, m.DOOR_OPEN)
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
		self.servo.set_servo_pulsewidth(m.DOOR_MOTOR, m.DOOR_OPEN)

	def closeLid(self):
		print("SERVO: close the door")
		self.servo.set_servo_pulsewidth(m.DOOR_MOTOR, m.DOOR_CLOSED)

