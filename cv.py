from threading import Thread, Condition
import cv2

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

    def run(self):
        self.__stream = cv2.VideoCapture(0)
        while self.__run:
            # Grab a frame

            # Find objects and draw them
            if self.__recipe is not None:
                self.__lock.acquire()
                recipe = db.recipes[self.__recipe]
                self.__lock.release()
            # Forward stream to ffmpeg
            # thx Brandon
        self.__stream.release()
        self.__stream = None

    def __del__(self):
        self.stop()

    def stop(self):
        if self.__stream is None:
            raise StreamNotStartedException()
        self.__stream.release()
        self.__stream = None

    def set_recipe(self, recipe = None):
        self.__lock.acquire()
        self.__recipe = recipe
        self.__lock.release()

    def find_items(self, items):
        '''
        Looks for the given list of items in the video feed.

        Requires the stream to be started.

        Args:
            items (list(Item)): List of items to be searched for.

        Returns:
            list(ItemResult): List of results.
        '''
        results = []
        for item in items:
            results.append(self.find_item(item))
        return results

    def find_item(self, item):
        '''
        Looks for the given item in the video feed.

        Requires the stream to be started.

        Args:
            item (str): Item to be searched for.
        '''
        if self.__stream is None:
            raise StreamNotStartedException()
        # Read the frame twice because otherwise you get an old frame
        success, frame = self.__stream.read()
        success, frame = self.__stream.read()
        # Recognize stuff here
        return ItemResult()

    def __get_frame(self):
        '''
        Gets a frame from the webcam stream.

        Returns:
            image: A cv2 image.
        '''
        return "Hi, I'm an image!"

class Streamer(Thread):
    def __init__(self, cameraIndex):
        self.__stream = None

    def run(self):
        self.__stream = cv2.VideoCapture(0)

class ItemResult(object):
    '''
    Attributes:
        item (Item): The Item that was being looked up.
        found (bool): If the item was found.
        position (Vector2): The position of the item, if it was found.
    '''
    def __init__(self, **kwargs):
        self.item = None
        self.found = False
        self.position = Vector2(-1, -1)

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
