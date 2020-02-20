import RPi.GPIO as GPIO
import pigpio

GPIO.setmode(GPIO.BCM)

PIN_MOTOR = 17
PIN_MAGNET = 27


def readMagnet(channel):
    magnet = GPIO.input(PIN_MAGNET)

    print(magnet)


pi = pigpio.pi()
GPIO.setup(PIN_MAGNET, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(PIN_MAGNET, GPIO.BOTH, callback=readMagnet)

while True:
    position = raw_input('?')
    pi.set_servo_pulsewidth(PIN_MOTOR, position)
