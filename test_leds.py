import SerialHandler

print("### Serial controller starts!")
serialComm = SerialHandler.SerialHandler()
ser = serialComm.getSerialPort()

while True:
    keyInput = input("Type a char").upper()
    print("You typed {}".format(keyInput))
    led_command = str.encode('#{}R1!'.format(keyInput))
    ser.write(led_command)
