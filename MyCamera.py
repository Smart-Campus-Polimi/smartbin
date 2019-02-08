import pygame
import pygame.camera

class MyCamera():
	def __init__(self):
		pygame.camera.init()
		#TODO: check initialization
		if not _initializeCamera():
			print("ERROR!")
			return False

	def _initializeCamera(self):
		try:
			self.dev = pygame.camera.list_cameras()[0]
		except IndexError as e:
			print("no camera", e)
			return None

		self.cam = pygame.camera.Camera(self.dev, (320, 240))
		self.cam.start()

		return self.cam

	def takePhoto(self):
		#TODO
		startTime = time.time()
	#file_name = subprocess.check_output(os.path.expanduser(WEBCAM))
	file_name = os.path.expanduser(DIRECTORY)+str("my_name.jpg") 
	img = my_cam.get_image()
	photoTime = time.time() - startTime
	print("photo taken in  {}s".format(photoTime))
	pygame.image.save(img, file_name)
	saveTime = time.time() - startTime 
	print("photo saved in {}s".format(saveTime))