import pigpio

PIN_MOTOR1 = 24
PIN_MOTOR2 = 25
pi = pigpio.pi()
pos = 901

pi.set_servo_pulsewidth(PIN_MOTOR2, pos)
pi.set_servo_pulsewidth(PIN_MOTOR1, pos)

while True:
    print(pi.read(PIN_MOTOR2))
    position = int(raw_input('?'))
    # pos = 900

    pi.set_servo_pulsewidth(PIN_MOTOR2, position)
    pi.set_servo_pulsewidth(PIN_MOTOR1, position)
    '''
    while(True):
        #print (pi.get_servo_pulsewidth(PIN_MOTOR2))
        print(pi.read(PIN_MOTOR2))
        print(pi.get_servo_pulsewidth(PIN_MOTOR2))
        #print(pi.get_servo_pulsewidth(PIN_MOTOR1))	
        #pi.set_servo_pulsewidth(PIN_MOTOR1, pos)
        #pi.set_servo_pulsewidth(PIN_MOTOR2, pos)
        #pos += 1
    
    print(pi.read(PIN_MOTOR2))
    #print(pi.read(PIN_MOTOR1))	
    print("finish")
    '''
