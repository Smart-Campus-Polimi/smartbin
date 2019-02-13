import RPi.GPIO as GPIO

servoPIN = 17

class DoorServo():
	def __init__(self):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(servoPIN, GPIO.OUT)


		self.servo = GPIO.PWM(servoPIN, 50) # GPIO 17 for PWM with 50Hz
		self.servo.start(7.5) # Initialization

	def getServo(self):
		return self.servo

	def stopServo(self):
		self.servo.stop()
		GPIO.cleanup()

	def openLid(self):
		self.servo.ChangeDutyCycle(7.5)

	def closeLid(self):
		self.servo.ChangeDutyCycle(2.5)


