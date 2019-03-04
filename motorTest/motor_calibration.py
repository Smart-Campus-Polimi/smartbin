import pigpio
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

PIN_MOTOR_DISC = 6
PIN_MOTOR_PALET = 24
PIN_MAGNET = 25

zero = True

UNSORTED = +65
PLASTIC = -60
GLASS = +170
PAPER = -192

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
pi.set_servo_pulsewidth(PIN_MOTOR_DISC, 800)

print("Move to initial position")
zero_pos = 1000
time.sleep(1)

status = "CALIBRATION"

for i in range(800, 2500):
	print(i)
	pi.set_servo_pulsewidth(PIN_MOTOR_DISC, i)
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
		pi.set_servo_pulsewidth(PIN_MOTOR_DISC, zero_pos + UNSORTED)
		pi.set_servo_pulsewidth(PIN_MOTOR_PALET, zero_pos + UNSORTED)

	elif(position == "2"):
		print("Butto in plastic")
		pi.set_servo_pulsewidth(PIN_MOTOR_DISC, zero_pos + PLASTIC)
		pi.set_servo_pulsewidth(PIN_MOTOR_PALET, zero_pos + PLASTIC)
		
	elif(position == "3"):
		print("Butto in paper")
                pi.set_servo_pulsewidth(PIN_MOTOR_DISC, zero_pos + PAPER)
                pi.set_servo_pulsewidth(PIN_MOTOR_PALET, zero_pos + PAPER)
	
	elif(position == "4"):
		print("Butto in glass")
		pi.set_servo_pulsewidth(PIN_MOTOR_DISC, zero_pos + GLASS)
		pi.set_servo_pulsewidth(PIN_MOTOR_PALET, zero_pos + PLASTIC)

	else:
		print("torno a casa")
		pi.set_servo_pulsewidth(PIN_MOTOR_DISC, zero_pos)
		pi.set_servo_pulsewidth(PIN_MOTOR_PALET, zero_pos)
