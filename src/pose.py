import mediapipe as mp
import cv2

class pose():
    LEFT_LANDMARKS = {11, 13, 15, 23, 25, 27}
    RIGHT_LANDMARKS = {12, 14, 16, 24, 26, 28}
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

                h, w = frame.shape[:2]
                for i, lm in enumerate(landmarks):
                    x = int(lm.x * w)
                    y = int(lm.y * h)

                    if i in self.LEFT_LANDMARKS:
                        color = (0, 255, 0)
                    elif i in self.RIGHT_LANDMARKS:
                        color = (0, 0, 255)
                    else:
                        color = (255, 255, 255)
                    cv2.circle(frame, (x, y), 5, color, -1)

                connections = self.mp_pose.POSE_CONNECTIONS

                for c in connections:
                    start = landmarks[c[0]]
                    end = landmarks[c[1]]

                    x1, y1 = int(start.x * w), int(start.y * h)
                    x2, y2 = int(end.x * w), int(end.y * h)

                    cv2.line(frame, (x1, y1), (x2, y2), (200, 200, 200), 2)

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
        else:
            return None
