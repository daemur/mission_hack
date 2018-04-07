from threading import Thread, Condition
import cv2

import db

class StreamNotStartedException(Exception):
    def __init__(self):
        Exception.__init__(self, 'The stream must be started to perform this operation.')

class FeedEater(Thread):
    def __init__(self, webcamIndex = 0):
        '''
        Args:
            webcamIndex (int): The ID of the webcam to capture from.
        '''
        # Thread stuff
        self.__stream = None
        self.__lock = Condition()
        self.__run = True
        # Recipe stuff
        self.__recipe = None
        self.foundRequirements = []
        # Thread init
        Thread.__init__(self)

    def run(self):
        try:
            self.__stream = cv2.VideoCapture(0)
            while self.__run:
                # Grab a frame
                success, frame = self.__stream.read()
                success, frame = self.__stream.read()
                # Do recipe stuff to the image
                if self.__recipe is not None:
                    # Find recipe information
                    self.__lock.acquire()
                    recipe = db.recipes[self.__recipe]
                    self.__lock.release()
                    # Get items from requirements
                    items = [db.items[r['item']] for r in recipe['requirements']]
                    # Find recipe items in frame
                    # TODO
                    # Draw item information on frame
                    # TODO
                # Forward stream to ffmpeg
                # thx Brandon
            self.__stream.release()
            self.__stream = None
        finally:
            if self.__stream is not None:
                self.__stream.release()
                self.__stream = None

    def stop(self):
        if self.__stream is None:
            raise StreamNotStartedException()
        self.__lock.acquire()
        self.__run = False
        self.__lock.release()

    def set_recipe(self, recipe = None):
        self.__lock.acquire()
        self.__recipe = recipe
        self.__foundRequirements = []
        self.__lock.release()

class Vector2(object):
    '''
    Attributes:
        x (int): X position of the point.
        y (int): Y position of the point.
    '''
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @property
    def value(self):
        return [self.x, self.y]

    @value.setter
    def value(self, value):
        self.x, self.y = value
