import src.camera
import cv2
import src.pose

running = True
pose = src.pose.pose()
cam = src.camera.startVideo()
prev_wrist = None
anchor = False
anchor_frames = 0
lost_anchor_frames = 0

data_dict = {"wrist": [{"t": -1, "x": -1, "y": -1}],
             "draw_elbow": [{"t": -1, "x": -1, "y": -1}],
             "bow_elbow": [{"t": -1, "x": -1, "y": -1}],
             "draw_shoulder": [{"t": -1, "x": -1, "y": -1}],
             "bow_shoulder": [{"t": -1, "x": -1, "y": -1}],
             "nose": [{"t": -1, "x": -1, "y": -1}]}

WRIST_NOSE_DIST_THRESHOLD = 0.24
BUFFER_SIZE = 15
MOVEMENT_THRESHOLD = 0.01
LOST_ANCHOR_THRESHOLD = 5


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

def anchor_detection(prev_wrist, wrist, wrist_elbow_height, landmarks):
    global stable_frames, movement
    if prev_wrist is not None:
        move = distance(wrist, prev_wrist, landmarks)
        # print(move)
        if move < MOVEMENT_THRESHOLD:
            stable_frames += 1
        else:
            stable_frames = 0
        movement = stable_frames < 10
    return wrist_elbow_height and not movement
def true_anchor(raw_anchor):
    global anchor_frames, anchor, lost_anchor_frames

    if raw_anchor:
        anchor_frames += 1
        lost_anchor_frames = 0
    else:
        lost_anchor_frames += 1
        anchor_frames = 0

    if anchor_frames >= LOST_ANCHOR_THRESHOLD:
        anchor = True
    if lost_anchor_frames >= LOST_ANCHOR_THRESHOLD:
        anchor = False
    return anchor


while True:
    while running:
        frame = cam.get_frame()
        h, w = frame.shape[:2]
        anchor = False
        if frame is None:
            break
        frame, landmarks = pose.process(frame)
        if landmarks is None:
            prev_wrist = None
            continue

        #nose_wrist_dist = distance("RWrist", "Nose", landmarks)
        wrist_elbow_height = pose.get_coor("RElbow", landmarks).y < pose.get_coor("RWrist", landmarks).y
        wrist = pose.get_coor("RWrist", landmarks)
        raw_anchor = anchor_detection(prev_wrist, wrist, wrist_elbow_height, landmarks)
        if true_anchor(raw_anchor):
            cv2.putText(frame, "Anchor", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        prev_wrist = wrist

        cv2.imshow("Video", frame)
        cv2.waitKey(1)

        if cv2.getWindowProperty("Video", cv2.WND_PROP_VISIBLE) < 1:
            running = False
    cam.release()
    cv2.destroyAllWindows()

    if input("Continue?").lower() == "y":
        running = True
        continue
    else:
        # After ends
        break
