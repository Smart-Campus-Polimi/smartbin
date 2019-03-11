import pygame
import pygame.camera
import sys
import time

pygame.camera.init()
try:
	my_cam = pygame.camera.list_cameras()[0] #Camera detected or not
except IndexError as e:
	print("no camera", e)
	sys.exit(0)
cam = pygame.camera.Camera(my_cam,(320,240))
cam.start()
start_time = time.time()
print("start")
i=0
while True:
	i = i+1
	name = raw_input('?')
	if(name == 1):
		type = 'UNSORTED'
	elif(name == 2):
		type = 'PLASTIC'
	elif(name == 3):
		type = 'PAPER'
	elif(name == 4):
		type = 'GLASS'

	print("shoot {}".format(type))
	print(i)
	img = cam.get_image()
	pygame.image.save(img,"/home/pi/pictures/"+name+str(time.time())+".jpg")
	print("Tot time {}".format(time.time()-start_time))
