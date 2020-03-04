import sys
import time

import pygame.camera

pygame.camera.init()
try:
    my_cam = pygame.camera.list_cameras()[0]  # Camera detected or not
except IndexError as e:
    print(("no camera", e))
    sys.exit(0)
cam = pygame.camera.Camera(my_cam, (320, 240))
cam.start()
start_time = time.time()
print("start")
i = 0
while True:
    i = i + 1
    name = input('?')
    if (name == '1'):
        _type = 'UNSORTED'
    elif (name == '2'):
        _type = 'PLASTIC'
    elif (name == '3'):
        _type = 'PAPER'
    elif (name == '4'):
        _type = 'GLASS'

    print(("shoot {}".format(_type)))
    print(i)
    img = cam.get_image()
    pygame.image.save(img, "/home/pi/Pictures/" + _type + str(time.time()) + ".jpg")
    print(("Tot time {}".format(time.time() - start_time)))
