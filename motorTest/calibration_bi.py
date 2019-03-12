import pigpio
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

PIN_MOTOR_PALETTA = 24
PIN_MAGNET_PALETTA = 27#?

PIN_MOTOR_DISK = 25
PIN_MAGNET_DISK = 27

zero_paletta = False
zero_disk = False

INIT_PALETTA = 900
INIT_DISK = 900

UNSORTED_PALETTA = +60
PLASTIC_PALETTA = -60
GLASS_PALETTA = +150
PAPER_PALETTA = -150

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
GPIO.setup(PIN_MAGNET_PALETTA, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(PIN_MAGNET_DISK, GPIO.IN, pull_up_down = GPIO.PUD_UP)


#INIT
pi.set_servo_pulsewidth(PIN_MOTOR_PALETTA, INIT_PALETTA)
pi.set_servo_pulsewidth(PIN_MOTOR_DISK, INIT_DISK)

print("Move to initial position")
#zero_pos = 800
time.sleep(1)

#PALETTA
status = "CALIBRATION"
#for i in range(800, 2500):
#	print(i)
#	if(GPIO.input(PIN_MAGNET_PALETTA)):
#		pi.set_servo_pulsewidth(PIN_MOTOR_PALETTA, i)
#		time.sleep(.02)
#	else:
#		zero_paletta = i
#		break

#print("Zero pos paletta is : {}".format(zero_paletta))

#DISK
for i in range(800, 2500):
	print(i)
	if(GPIO.input(PIN_MAGNET_DISK)):
		pi.set_servo_pulsewidth(PIN_MOTOR_DISK, i)
		time.sleep(.02)
	else:
		zero_disk = i-45
		break

print("Zero pos paletta is : {}".format(zero_disk))
pi.set_servo_pulsewidth(PIN_MOTOR_DISK, zero_disk)
status = "WASTE"

while True:
	position = raw_input('?')
	
	if(position == "1"):
		print("Butto in unsorted")
		pi.set_servo_pulsewidth(PIN_MOTOR_PALETTA, zero_paletta + UNSORTED)
		pi.set_servo_pulsewidth(PIN_MOTOR_DISK, zero_disk + UNSORTED)

	elif(position == "2"):
		print("Butto in plastic")
		pi.set_servo_pulsewidth(PIN_MOTOR_PALETTA, zero_paletta + PLASTIC)
		pi.set_servo_pulsewidth(PIN_MOTOR_DISK, zero_disk + PLASTIC)


	elif(position == "3"):
		print("Butto in paper")
		pi.set_servo_pulsewidth(PIN_MOTOR_PALETTA, zero_paletta + PAPER)
		pi.set_servo_pulsewidth(PIN_MOTOR_DISK, zero_disk + PAPER)

	
	elif(position == "4"):
		print("Butto in glass")
		pi.set_servo_pulsewidth(PIN_MOTOR_PALETTA, zero_paletta + GLASS)
		pi.set_servo_pulsewidth(PIN_MOTOR_DISK, zero_disk + GLASS)


	else:
		print("torno a casa")
		pi.set_servo_pulsewidth(PIN_MOTOR_PALETTA, zero_paletta)
		pi.set_servo_pulsewidth(PIN_MOTOR_DISK, zero_disk)

