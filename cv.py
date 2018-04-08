from threading import Thread, Condition
from colorsys import hsv_to_rgb
import subprocess as sp
import numpy as np
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
        self.__webcamIndex = webcamIndex
        # Thread stuff
        self.__stream = None
        self.__ffmpeg = None
        self.__lock = Condition()
        self.__run = True
        # Recipe stuff
        self.__requirements = set()
        self.__foundRequirements = set()
        # Debug stuff
        self.__print = True
        # Thread init
        Thread.__init__(self)

    def run(self):
        try:
            self.__stream = cv2.VideoCapture(self.__webcamIndex)
            if self.__stream.isOpened():
                print('Stream started.')
                success, frame = self.__stream.read()
                assert success, 'Stream started but could not capture an image.'
                h, w, _ = frame.shape
                self.__ffmpeg = None
                # self.__ffmpeg = sp.Popen(['vlc',
                #                           '--demux=rawvideo',
                #                           '--rawvid-width={}'.format(w),
                #                           '--rawvid-height={}'.format(h),
                #                           '--rawvid-chroma=RV24',
                #                           '-',
                #                           '--sout=#transcode{vcodec=theo,vb=512,scale=1,acodec=none}:http{mux=ogg,dst=:8090/feed}',
                #                           ':no-sout-rtp-sap',
                #                           ':no-sout-standard-sap',
                #                           ':ttl=1',
                #                           ':sout-keep'],
                #                          stdin = sp.PIPE)
                # self.__ffmpeg = sp.Popen(['ffmpeg',
                #                           '-f', 'rawvideo',
                #                           '-pixel_format', 'bgr24',
                #                           '-video_size', '{}x{}'.format(w, h),
                #                           '-i', '-',
                #                           '-preset', 'ultrafast',
                #                           '-vcodec', 'h264',
                #                           '-acodec', 'none',
                #                           '-tune', 'zerolatency',
                #                           '-f', 'rtp',
                #                           'rtp://localhost:8090'],
                #                          stdin = sp.PIPE)
                # self.__ffmpeg = sp.Popen(['ffmpeg',
                #                           '-f', 'rawvideo',
                #                           '-pixel_format', 'bgr24',
                #                           '-video_size', '{}x{}'.format(w, h),
                #                           '-i', '-',
                #                           '-acodec', 'libvorbis',
                #                           '-vcodec', 'libtheora'
                #                           '-f', 'ogg',
                #                           'feed.ogv'],
                #                          stdin = sp.PIPE)
                while self.__run:
                    # Grab a frame
                    success, frame = self.__stream.read()
                    if not success:
                        break
                    # Do recipe stuff to the image
                    if self.__requirements:
                        # Get items from requirements
                        self.__lock.acquire()
                        items = set(self.__requirements)
                        self.__lock.release()
                        # Find recipe items in frame
                        for item in items:
                            color = hsv_to_bgr(*db.items[item]['color'])
                            tolerance = 24
                            low = [max(*c) for c in zip([0, 0, 0], [c - tolerance for c in color])]
                            high = [min(*c) for c in zip([255, 255, 255], [c + tolerance for c in color])]
                            if self.__print:
                                print("{}: {}, {}".format(item, low, high))
                            # Threshold
                            masked = cv2.inRange(frame,
                                                 np.array(low),
                                                 np.array(high))
                            # Filter noise
                            filtered = cv2.medianBlur(masked, 5)
                            # Contour
                            _, contours, hierarchy = cv2.findContours(filtered, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                            for contour in contours:
                                if cv2.contourArea(contour) >= 250:
                                    # We found it!
                                    self.__foundRequirements.add(item)
                                    # Draw contours
                                    cv2.drawContours(frame, [contour], 0, (255, 128, 0), 4)
                        self.__print = False
                    # Forward stream to ffmpeg
                    # self.__ffmpeg.stdin.write(frame.tostring())
                    # TODO - the real thing
                    cv2.imshow('tmp output', frame)
                    # Press escape to quit
                    if cv2.waitKey(1) == 27:
                       break
                self.__stream.release()
            self.__stream = None
        finally:
            # Kill ffmpeg
            if self.__ffmpeg is not None:
                self.__ffmpeg.kill()
                self.__ffmpeg = None
            # Kill webcam stream
            if self.__stream is not None:
                self.__stream.release()
                self.__stream = None
            print('Stream stopped.')

    def stop(self):
        if self.__stream is None:
            raise StreamNotStartedException()
        self.__lock.acquire()
        self.__run = False
        self.__lock.release()
        self.join()

    def set_requirements(self, requirements = []):
        self.__lock.acquire()
        self.__requirements = set(requirements)
        self.__lock.release()

    def reset_found_requirements(self):
        self.__lock.acquire()
        self.__foundRequirements = set()
        self.__lock.release()

    @property
    def foundRequirements(self):
        return set(self.__foundRequirements)

def hsv_to_bgr(h, s, v):
    r, g, b = hsv_to_rgb(h / 360.0, s / 100.0, v / 100.0)
    return [int(c * 255) for c in [b, g, r]]
