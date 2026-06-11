import src.camera
import cv2
import src.pose

running = True
pose = src.pose.pose()
cam = src.camera.startVideo()
prev_wrist = None
anchor = False

WRIST_NOSE_DIST_THRESHOLD = 0.2
BUFFER_SIZE = 15
MOVEMENT_THRESHOLD = 0.01


def distance(part1: str or list, part2: str or list, landmarks: list, w=0, h=0) -> bool:
    dx = 0
    dy = 0
    if type(part1) == type("hi"):
        if w != 0 and h != 0:
            dx = (pose.get_coor(part1, landmarks).x * w) - (pose.get_coor(part2, landmarks).x * w)
            dy = (pose.get_coor(part1, landmarks).y * h) - (pose.get_coor(part2, landmarks).y * h)
        else:
            dx = pose.get_coor(part1, landmarks).x - pose.get_coor(part2, landmarks).x
            dy = pose.get_coor(part1, landmarks).y - pose.get_coor(part2, landmarks).y
    else:
        dx = part1.x - part2.x
        dy = part1.y - part2.y
    return ((dx ** 2) + (dy ** 2)) ** 0.5


stable_frames = 0
movement = True
def anchor_detection(prev_wrist, wrist, nose_wrist_dist, landmarks):
    global stable_frames, movement
    if prev_wrist is not None:
        move = distance(wrist, prev_wrist, landmarks)
        # print(move)
        if move < MOVEMENT_THRESHOLD:
            stable_frames += 1
        else:
            stable_frames = 0
        movement = stable_frames < 10
    return nose_wrist_dist <= WRIST_NOSE_DIST_THRESHOLD and not movement


while True:
    while running:
        frame = cam.get_frame()
        h, w = frame.shape[:2]
        if frame is None:
            break
        frame, landmarks = pose.process(frame)
        if landmarks is None:
            prev_wrist = None
            continue

        # Anchor detection
        '''Old anchor detection
        print("nose wrist " + str((distance("Nose", "RWrist", landmarks, w, h))))
        if (distance("Nose", "RWrist", landmarks, w, h)) <= 115 and (distance("RShoulder", "RElbow", landmarks, w, h) > 115):
             cv2.putText(frame, "Anchor", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)'''
        # New anchor detection
        nose_wrist_dist = distance("RWrist", "Nose", landmarks)
        wrist = pose.get_coor("RWrist", landmarks)
        if anchor_detection(prev_wrist, wrist, nose_wrist_dist, landmarks):
            cv2.putText(frame, "Anchor", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        prev_wrist = wrist

        cv2.imshow("Video", frame)
        cv2.waitKey(1)

        if cv2.getWindowProperty("Video", cv2.WND_PROP_VISIBLE) < 1:
            running = False
    cam.release()
    cv2.destroyAllWindows()

    if input("Another shot?").lower() == "y":
        running = True
        continue
    else:
        # After ends
        break
