import pygame
import pygame.camera
import os
import time, datetime

WIDTH = 320
HEIGHT = 240
PICTURE_DIRECTORY = '~/pictures/'

class MyCamera():
	def __init__(self):
		pygame.camera.init()
		self.photoDone = False
		self.file_name = None
		self._initializeCamera() 
		#if self.my_cam is not None:
		#	print("ERROR!")
		#	#TODO: check initialization
		#	return None
		#self.my_cam.stop()

	def _initializeCamera(self):
		try:
			self.dev = pygame.camera.list_cameras()[0]
		except IndexError as e:
			print("no camera", e)
			return None
		
		print("camera device {}".format(self.dev))
		self.my_cam = pygame.camera.Camera(self.dev, (320, 240))
	
		#while(True):
		#	try:
		#		self.my_cam.start()
		#		return self.my_cam
		#	except Exception as e:
		#		print("unable to start the cam {}".format(e))
		#		print("retry in 1 sec")
		#		time.sleep(1)
		return self.my_cam
	
	def stop(self):
		self.my_cam.stop()
	
	def takePhoto(self):
		startTime = time.time()
		self.file_name = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
		self.file_name = os.path.expanduser(PICTURE_DIRECTORY)+self.file_name+".jpg" 
		
		self.photoDone = False
		print("take the picture")
		while(not self.photoDone):
			try:
				self.my_cam.start()
				img = self.my_cam.get_image()
				self.photoDone = True

			except Exception as e:
				print("unable to start the cam {}".format(e))
				print("retry in 1 sec")
				time.sleep(.1)
		#self.my_cam.start()
		#img = self.my_cam.get_image()
		#self.photoDone = True

		photoTime = time.time() - startTime
		print("photo taken in  {}s".format(photoTime))
		
		#TODO: try except path?
		pygame.image.save(img, self.file_name)
		
		saveTime = time.time() - photoTime - startTime 
		print("photo saved in {}s".format(saveTime))
		self.my_cam.stop()
		return self.file_name

	#### PATH ####
	def currentPath(self):
		return self.file_name

	def erasePath(self):
		self.file_name = None

	#### PHOTO ####
	def isPhotoDone(self):
		return self.photoDone

	#maybe is better to have a switch state method
	def setCameraStatus(self, status):
		self.photoDone = status
		if(not self.photoDone):
			self.file_name = None
