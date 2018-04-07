from threading import Thread, Condition
import cv2

class StreamNotStartedException(Exception):
    def __init__(self):
        Exception.__init__(self, 'The stream must be started to perform this operation.')

class StreamAlreadyStartedException(Exception):
    def __init__(self):
        Exception.__init__(self, 'The stream must be stopped to perform this operation.')

class FeedEater(Thread):
    def __init__(self, webcamIndex = 0):
        '''
        Args:
            webcamIndex (int): The ID of the webcam to capture from.
        '''
        self.__stream = None

    def start(self):
        '''
        Starts streaming the primary webcam.
        '''
        if self.__stream is not None:
            raise StreamAlreadyStartedException()
        self.__stream = cv2.VideoCapture(0)

    def stop(self):
        '''
        Stops the webcam stream.
        '''
        if self.__stream is None:
            raise StreamNotStartedException()
        self.__stream = None

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
        frame = self.__get_frame()
        # Recognize stuff here
        return ItemResult()

    def __get_frame(self):
        '''
        Gets a frame from the webcam stream.

        Returns:
            image: A cv2 image.
        '''
        return "Hi, I'm an image!"

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
