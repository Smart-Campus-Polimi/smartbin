import pigpio

PIN_MOTOR = 17

pi = pigpio.pi()

while True:
	position = raw_input('?')
	pi.set_servo_pulsewidth(PIN_MOTOR, position)
