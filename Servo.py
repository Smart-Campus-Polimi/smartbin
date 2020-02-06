import RPi.GPIO as GPIO
import time
import pigpio
import motors_constants as m

GPIO.setmode(GPIO.BCM)


class BladeServo:
    def __init__(self):
        self.servo = pigpio.pi()
        GPIO.setup(m.PIN_MAGNET_BLADE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.servo.set_servo_pulsewidth(m.BLADE_MOTOR, m.BLADE_INIT)
        self.zero_blade = m.BLADE_INIT
        print("BLADE: initialization Done")

    def calibration(self):
        for pos in range(m.BLADE_INIT, m.MAX_MOTOR):
            if GPIO.input(m.PIN_MAGNET_BLADE):
                self.servo.set_servo_pulsewidth(m.BLADE_MOTOR, pos)
                time.sleep(.02)
            else:
                self.zero_blade = pos + m.OFFSET_PALETTA
                break

        if self.zero_blade == m.BLADE_INIT:
            print("BLADE: calibration failed")
            self.zero_blade = m.CORRECT_BLADE

        self.servo.set_servo_pulsewidth(m.BLADE_MOTOR, self.zero_blade)
        print("BLADE: Zero pos blade is : {}".format(self.zero_blade))

        return True

    def move_blade(self, waste):
        self.servo.set_servo_pulsewidth(m.BLADE_MOTOR, self._parse_blade(waste))

    def _parse_blade(self, waste):
        if waste == "UNSORTED":
            pos = self.zero_blade + m.BLADE_UNSORTED
        elif waste == "PLASTIC":
            pos = self.zero_blade + m.BLADE_PLASTIC
        elif waste == "PAPER":
            pos = self.zero_blade + m.BLADE_PAPER
        elif waste == "GLASS":
            pos = self.zero_blade + m.BLADE_GLASS
        elif waste == "HOME":
            pos = self.zero_blade
        else:
            pos = self.zero_blade

        print("BLADE: {}".format(pos))
        return pos


class DiskServo:
    def __init__(self):
        self.servo = pigpio.pi()
        GPIO.setup(m.PIN_MAGNET_DISK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.servo.set_servo_pulsewidth(m.DISK_MOTOR, m.DISK_INIT)
        self.zero_disk = m.DISK_INIT
        print("DISK: initialization Done")

    def calibration(self):
        for pos in range(m.DISK_INIT, m.MAX_MOTOR):
            if GPIO.input(m.PIN_MAGNET_DISK):
                self.servo.set_servo_pulsewidth(m.DISK_MOTOR, pos)
                time.sleep(.02)
            else:
                self.zero_disk = pos + m.OFFSET_DISK
                break

        if self.zero_disk == m.DISK_INIT:
            print("DISK: calibration failed")
            self.zero_disk = m.CORRECT_DISK

        self.servo.set_servo_pulsewidth(m.DISK_MOTOR, self.zero_disk)
        print("DISK: Zero pos disk is : {}".format(self.zero_disk))
        return True

    def moveDisk(self, waste):
        self.servo.set_servo_pulsewidth(m.DISK_MOTOR, self._parseDisk(waste))

    def _parseDisk(self, waste):
        if waste == "UNSORTED":
            pos = self.zero_disk + m.DISK_UNSORTED
        elif waste == "PLASTIC":
            pos = self.zero_disk + m.DISK_PLASTIC
        elif waste == "PAPER":
            pos = self.zero_disk + m.DISK_PAPER
        elif waste == "GLASS":
            pos = self.zero_disk + m.DISK_GLASS
        elif waste == "HOME":
            pos = self.zero_disk
        else:
            pos = m.DISK_INIT

        print("DISK: {}".format(pos))
        return pos


def stopServo():
    print("SERVO: stop the servo")
    # self.servo.stop()


class DoorServo:
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

    def openLid(self):
        print("SERVO: open the door")
        self.servo.set_servo_pulsewidth(m.DOOR_MOTOR, m.DOOR_OPEN)

    def closeLid(self):
        print("SERVO: close the door")
        self.servo.set_servo_pulsewidth(m.DOOR_MOTOR, m.DOOR_CLOSED)
