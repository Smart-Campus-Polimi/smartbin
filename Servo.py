import RPi.GPIO as GPIO
import time

servoPIN = 17

class DoorServo():
	def __init__(self):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(servoPIN, GPIO.OUT)

		self.servo = GPIO.PWM(servoPIN, 50) # GPIO 17 for PWM with 50Hz
		self.servo.start(7.5) # Initialization
		print("SERVO: initialization Done")
		time.sleep(.5)
		self.closeLid()
		time.sleep(.5)
		self.openLid()	
			
	def getServo(self):
		return self.servo

	def stopServo(self):
		print("SERVO: stop the servo")
		self.servo.stop()
		GPIO.cleanup()

	def openLid(self):
		print("SERVO: open the door")
		self.servo.ChangeDutyCycle(7.5)

	def closeLid(self):
		print("SERVO: close the door")
		self.servo.ChangeDutyCycle(2.5)


