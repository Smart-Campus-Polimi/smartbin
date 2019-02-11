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
		self.my_cam = self._initializeCamera() 
		if self.my_cam is not None:
			print("ERROR!")
			#TODO: check initialization
			return None

	def _initializeCamera(self):
		try:
			self.dev = pygame.camera.list_cameras()[0]
		except IndexError as e:
			print("no camera", e)
			return None
		
		print("camera device {}".format(self.dev))
		self.cam = pygame.camera.Camera(self.dev, (320, 240))
		while(True):
			try:
				self.cam.start()
				break
			except Exception as e:
				print("unable to start the cam {}".format(e))
				print("retry in 1 sec")
				time.sleep(1)

		return self.cam
	
	def stop(self):
		self.cam.stop()
	
	def takePhoto(self):
		startTime = time.time()
		self.file_name = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
		self.file_name = os.path.expanduser(PICTURE_DIRECTORY)+self.file_name+".jpg" 
		
		#TODO: try except?
		img = self.my_cam.get_image()
		self.photoDone = True

		photoTime = time.time() - startTime
		print("photo taken in  {}s".format(photoTime))
		
		#TODO: try except path?
		pygame.image.save(img, self.file_name)
		
		saveTime = time.time() - photoTime - startTime 
		print("photo saved in {}s".format(saveTime))

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
