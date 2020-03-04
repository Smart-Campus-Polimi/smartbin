import datetime
import logging
import os
import time

import pygame
import pygame.camera

logger = logging.getLogger("CAMERA")


class MyCamera:
    def __init__(self, pic):
        pygame.camera.init()
        self.folder = pic.folder
        self.width = pic.width
        self.height = pic.height
        self.photo_done = False
        self.file_name = None
        self.total_time = 0
        try:
            self.dev = pygame.camera.list_cameras()[0]
        except IndexError as e:
            logging.critical("No camera present", e)
            self.dev = None

        logging.debug("Camera device %s", self.dev)
        if self.dev is not None:
            self.my_cam = pygame.camera.Camera(self.dev, (self.width, self.height))

    def checkStatus(self):
        if self.dev is None:
            return False
        if self.my_cam is None:
            return False

        return True

    def takePhoto(self):
        start_time = time.time()
        self.file_name = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
        self.file_name = os.path.expanduser(self.folder) + self.file_name + ".jpg"

        self.photo_done = False
        logging.info("Taking picture")
        while not self.photo_done:
            try:
                self.my_cam.start()
                img = self.my_cam.get_image()
                self.photo_done = True
            except Exception as e:
                logger.warning("Unable to start the cam %s", e)
                logger.debug("Retry in 1 sec")
                time.sleep(1)

        # TODO: try except path?
        pygame.image.save(img, self.file_name)

        self.total_time = time.time() - start_time
        logger.debug("Photo taken in %s s", self.total_time)
        self.my_cam.stop()
        return self.file_name

    #### PATH ####
    def currentPath(self):
        return self.file_name

    def erasePath(self):
        self.file_name = None

    #### PHOTO ####
    def isPhotoDone(self):
        return self.photo_done

    # maybe is better to have a switch state method
    def setCameraStatus(self, status):
        self.photo_done = status
        if not self.photo_done:
            self.file_name = None

    def get_photo_time(self):
        return self.total_time
