import mediapipe as mp
import cv2

class pose():
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.mp_draw = mp.solutions.drawing_utils

    def process(self, frame, draw=True):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb)
        landmarks = None

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

        if draw:
            self.mp_draw.draw_landmarks(
                frame,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS
            )
        return frame, landmarks

    def get_coor(self, part: str, landmarks: list):
        if part == "Nose":
            return landmarks[0]
        elif part == "LShoulder":
            return landmarks[11]
        elif part == "RShoulder":
            return landmarks[12]
        elif part == "LElbow":
            return landmarks[13]
        elif part == "RElbow":
            return landmarks[14]
        elif part == "LWrist":
            return landmarks[15]
        elif part == "RWrist":
            return landmarks[16]
