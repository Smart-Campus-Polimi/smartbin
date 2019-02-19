import pigpio
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

PIN_MOTOR = 17
PIN_MAGNET = 27

zero = False

UNSORTED = +60
PLASTIC = -60
GLASS = +150
PAPER = -150

status = "INIT"

def readMagnet(channel):
	global zero
	global  status
	magnet = GPIO.input(PIN_MAGNET)	
	
	if(status == "CALIBRATION"):
		if(not magnet):
			zero = True
	
	print(magnet)


pi = pigpio.pi()
GPIO.setup(PIN_MAGNET, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.add_event_detect(PIN_MAGNET, GPIO.BOTH, callback=readMagnet)


#INIT
pi.set_servo_pulsewidth(PIN_MOTOR, 800)

print("Move to initial position")
zero_pos = 800
time.sleep(1)

status = "CALIBRATION"

for i in range(800, 2500):
	print(i)
	pi.set_servo_pulsewidth(PIN_MOTOR, i)
	time.sleep(.02)
	if(zero):
		zero_pos = i
		zero = False
		break

print("Zero pos is : {}".format(zero_pos))

status = "WASTE"

while True:
	position = raw_input('?')
	
	if(position == "1"):
		print("Butto in unsorted")
		pi.set_servo_pulsewidth(PIN_MOTOR, zero_pos + UNSORTED)

	elif(position == "2"):
		print("Butto in plastic")
		pi.set_servo_pulsewidth(PIN_MOTOR, zero_pos + PLASTIC)

	elif(position == "3"):
		print("Butto in paper")
                pi.set_servo_pulsewidth(PIN_MOTOR, zero_pos + PAPER)
	
	elif(position == "4"):
		print("Butto in glass")
		pi.set_servo_pulsewidth(PIN_MOTOR, zero_pos + GLASS)

	else:
		print("torno a casa")
		pi.set_servo_pulsewidth(PIN_MOTOR, zero_pos)
