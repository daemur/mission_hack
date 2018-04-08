from threading import Thread, Condition
from colorsys import hsv_to_rgb
import subprocess as sp
import numpy as np
import math
import cv2

import db

class StreamNotStartedException(Exception):
    def __init__(self):
        Exception.__init__(self, 'The stream must be started to perform this operation.')

class FeedEater(Thread):
    def __init__(self, webcamIndex = 0, tolerance = 24):
        '''
        Args:
            webcamIndex (int): The ID of the webcam to capture from.
        '''
        self.__webcamIndex = webcamIndex
        self.__tolerance = tolerance
        # Thread stuff
        self.__stream = None
        self.__ffmpeg = None
        self.__lock = Condition()
        self.__run = True
        # Recipe stuff
        self.__requirements = set()
        self.__targets = []
        self.__foundRequirements = set()
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
                #                           '-f', 'mpegts',
                #                           'udp://localhost:8090'],
                #                          stdin = sp.PIPE)
                # self.__ffmpeg = sp.Popen(['ffmpeg',
                #                           '-f', 'rawvideo',
                #                           '-pixel_format', 'bgr24',
                #                           '-video_size', '{}x{}'.format(w, h),
                #                           '-i', '-',
                #                           '-f', 'mp4',
                #                           '-vcodec', 'libx264',
                #                           '-preset', 'ultrafast',
                #                           '-acodec', 'aac',
                #                           'feed.mp4'],
                #                          stdin = sp.PIPE)
                while self.__run:
                    # Grab a frame
                    success, frame = self.__stream.read()
                    if not success:
                        break
                    # Do recipe stuff to the image
                    if self.__requirements:
                        # Get requirements and targets
                        self.__lock.acquire()
                        items = set(self.__requirements)
                        targets = list(self.__targets)
                        self.__lock.release()
                        # Find recipe items in frame
                        for item in items:
                            for contour in get_contours(frame, db.items[item]['color'], self.__tolerance):
                                # We found it!
                                self.__foundRequirements.add(item)
                                # Draw contours
                                cv2.drawContours(frame, [contour], 0, (255, 128, 0), 4)
                        # Find targets in frame
                        boxesDrawn = set()
                        for target in targets:
                            for contour in get_contours(frame, db.items[target['item']]['color'], self.__tolerance):
                                # Find object min rectangle
                                rect = cv2.minAreaRect(contour)
                                # Draw box around target
                                if target['item'] not in boxesDrawn:
                                    box = np.int0(cv2.boxPoints(rect))
                                    cv2.drawContours(frame, [box], 0, (0, 224, 255), 4)
                                # Make angle point up
                                angleTarget = 180
                                angleRange = 46
                                angle = rect[2]
                                w, h = rect[1]
                                while abs(angle_difference(angle, angleTarget)) >= angleRange:
                                    angle = (angle + 90) % 360
                                    w, h = h, w
                                if target['type'] == 'point':
                                    # Point target
                                    pos = rotate_point((0, 0),
                                                       [c[0] * c[1] - c[0] * 0.5 for c in zip((w, h), target['position'])],
                                                       angle)
                                    cv2.circle(frame, tuple(int(n[0] + n[1]) for n in zip(rect[0], pos)), 2, (0, 128, 255), 3)
                                elif target['type'] == 'line':
                                    # Line target
                                    pos1 = rotate_point((0, 0),
                                                        [c[0] * c[1] - c[0] * 0.5 for c in zip((w, h), target['position'][:2])],
                                                        angle)
                                    pos1 = tuple(int(n[0] + n[1]) for n in zip(rect[0], pos1))
                                    pos2 = rotate_point((0, 0),
                                                        [c[0] * c[1] - c[0] * 0.5 for c in zip((w, h), target['position'][2:])],
                                                        angle)
                                    pos2 = tuple(int(n[0] + n[1]) for n in zip(rect[0], pos2))
                                    cv2.line(frame, pos1, pos2, (0, 128, 255), 4)
                                elif target['type'] == 'rectangle':
                                    # Rectangle target
                                    pos = rotate_point((0, 0),
                                                       [c[0] * c[1] - c[0] * 0.5 for c in zip((w, h), target['position'][:2])],
                                                       angle)
                                    pos = tuple(int(n[0] + n[1]) for n in zip(rect[0], pos))
                                    box2d = (pos, tuple(int(n[0] * n[1]) for n in zip((w, h), target['position'][2:])), (angle + 180) % 360)
                                    box = np.int0(cv2.boxPoints(box2d))
                                    cv2.drawContours(frame, [box], 0, (0, 128, 255), 4)
                            boxesDrawn.add(target['item'])
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

    def set_targets(self, targets = []):
        self.__lock.acquire()
        self.__targets = list(targets)
        self.__lock.release()

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

def color_low_high(color, tolerance):
    col = hsv_to_bgr(*color)
    low = [max(*c) for c in zip([0, 0, 0], [c - tolerance for c in col])]
    high = [min(*c) for c in zip([255, 255, 255], [c + tolerance for c in col])]
    return low, high

def get_contours(frame, color, tolerance, minArea = 250):
    low, high = color_low_high(color, tolerance)
    # Threshold
    masked = cv2.inRange(frame,
                         np.array(low),
                         np.array(high))
    # Filter noise
    filtered = cv2.medianBlur(masked, 5)
    # Contour
    _, contours, _ = cv2.findContours(filtered, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    return [contour for contour in contours if cv2.contourArea(contour) >= minArea]

def rotate_point(origin, point, angle):
    rads = math.radians(angle)
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(rads) * (px - ox) - math.sin(rads) * (py - oy)
    qy = oy + math.sin(rads) * (px - ox) + math.cos(rads) * (py - oy)
    return int(qx), int(qy)

def angle_difference(source, target):
    return ((((target - source) % 360) + 540) % 360) - 180
