import src.camera
import cv2
import src.pose
import json
import src.analysis

try:
    with open("data/data.json", "r") as f:
        all_shots = json.load(f)
except FileNotFoundError:
    all_shots = {}

shot_num = len(all_shots)
frame_num = 0
running = True
pose = src.pose.pose()
cam = src.camera.startVideo()
prev_wrist = None
anchor = False
prev_anchor = False
anchor_frames = 0
lost_anchor_frames = 0
stable_frames = 0
movement = True
data_dict = {
    "draw_wrist": [],
    "bow_wrist": [],
    "draw_elbow": [],
    "bow_elbow": [],
    "draw_shoulder": [],
    "bow_shoulder": [],
    "nose": []
    }
analyse = src.analysis.analyse()

WRIST_NOSE_DIST_THRESHOLD = 0.24
BUFFER_SIZE = 15
MOVEMENT_THRESHOLD = 0.01
LOST_ANCHOR_THRESHOLD = 5
ELBOW_HEIGHT_TOLLERANCE = 0.02


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


def anchor_detection(prev_wrist, wrist, shoulder_elbow_height, landmarks):
    global stable_frames, movement
    if prev_wrist is not None:
        move = distance(wrist, prev_wrist, landmarks)
        # print(move)
        if move < MOVEMENT_THRESHOLD:
            stable_frames += 1
        else:
            stable_frames = 0
        movement = stable_frames < 5 # v1=10
        print(
            shoulder_elbow_height,
            not movement,
            distance("RWrist", "LWrist", landmarks),
            distance("RWrist", "Nose", landmarks),
            raw_anchor
        )

    return shoulder_elbow_height and not movement and (
            distance("RWrist", "LWrist", landmarks) > distance("RWrist", "Nose", landmarks))


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


def save_data_locally(frame_num, landmarks):
    temp_list = ["draw_wrist", "bow_wrist", "draw_elbow", "bow_elbow", "draw_shoulder", "bow_shoulder", "nose"]
    for part in temp_list:
        data_dict[part].append(
            {"t": frame_num, "x": pose.get_coor(part, landmarks).x, "y": pose.get_coor(part, landmarks).y})


while True:
    while running:
        frame = cam.get_frame()
        if frame is None:
            break
        h, w = frame.shape[:2]
        frame_num += 1
        frame, landmarks = pose.process(frame)
        if landmarks is None:
            prev_wrist = None
            continue

        shoulder_elbow_height = pose.get_coor("RElbow", landmarks).y < pose.get_coor("RShoulder", landmarks).y + ELBOW_HEIGHT_TOLLERANCE
        wrist = pose.get_coor("RWrist", landmarks)
        raw_anchor = anchor_detection(prev_wrist, wrist, shoulder_elbow_height, landmarks)
        if true_anchor(raw_anchor):
            cv2.putText(frame, "Anchor", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            save_data_locally(frame_num, landmarks)
            prev_anchor = True
        else:
            if prev_anchor:
                shot_num += 1
                analyse.anchor_analysis(data_dict)
                all_shots[f"Shot{shot_num}"] = {"Anchor": data_dict}
                data_dict = {
                    "draw_wrist": [],
                    "bow_wrist": [],
                    "draw_elbow": [],
                    "bow_elbow": [],
                    "draw_shoulder": [],
                    "bow_shoulder": [],
                    "nose": []
                }
                
            prev_anchor = False
        prev_wrist = wrist

        with open('data/data.json', "w") as f:
            json.dump(all_shots, f, indent=2)

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
        print(data_dict)
        break
