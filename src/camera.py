import numpy as np
import cv2 as cv


class startVideo():
    def __init__(self, camera_index=0):
        self.cap = cv.VideoCapture(camera_index)

    def get_frame(self):
        ret, frame = self.cap.read()

        if not ret:
            return None
        return frame
    def release(self):
        self.cap.release()
