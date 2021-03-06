import datetime
import os
import time

import pygame
import pygame.camera

WIDTH = 320
HEIGHT = 240
PICTURE_DIRECTORY = '~/Pictures/'


class MyCamera:
    def __init__(self):
        pygame.camera.init()
        self.photoDone = False
        self.file_name = None
        try:
            self.dev = pygame.camera.list_cameras()[0]
        except IndexError as e:
            print("CAMERA: no camera", e)
            self.dev = None

        print("CAMERA: camera device {}".format(self.dev))
        if self.dev is not None:
            self.my_cam = pygame.camera.Camera(self.dev, (WIDTH, HEIGHT))

    def checkStatus(self):
        if self.dev is None:
            return False
        if self.my_cam is None:
            return False

        return True

    def takePhoto(self):
        startTime = time.time()
        self.file_name = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
        self.file_name = os.path.expanduser(PICTURE_DIRECTORY) + self.file_name + ".jpg"

        print(self.my_cam)

        self.photoDone = False
        print("CAMERA: take the picture")
        while (not self.photoDone):
            try:
                self.my_cam.start()
                img = self.my_cam.get_image()
                self.photoDone = True
            except Exception as e:
                print("CAMERA: unable to start the cam {}".format(e))
                print("CAMERA: retry in 1 sec")
                time.sleep(1)

        photoTime = time.time() - startTime
        print("CAMERA: photo taken in  {}s".format(photoTime))

        # TODO: try except path?
        pygame.image.save(img, self.file_name)

        saveTime = time.time() - photoTime - startTime
        print("CAMERA: photo saved in {}s".format(saveTime))
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

    # maybe is better to have a switch state method
    def setCameraStatus(self, status):
        self.photoDone = status
        if (not self.photoDone):
            self.file_name = None
