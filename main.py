import src.camera
import cv2
import src.pose

running = True
pose = src.pose.pose()
cam = src.camera.startVideo()


def distance(part1: str, part2: str, landmarks: list, w=0, h=0) -> bool:
    if w != 0 and h !=0:
        dx = (pose.get_coor(part1, landmarks).x * w) - (pose.get_coor(part2, landmarks).x * w)
        dy = (pose.get_coor(part1, landmarks).y * h) - (pose.get_coor(part2, landmarks).y * h)
    else:
        dx = pose.get_coor(part1, landmarks).x - pose.get_coor(part2, landmarks).x
        dy = pose.get_coor(part1, landmarks).y - pose.get_coor(part2, landmarks).y
    return ((dx ** 2) + (dy ** 2)) ** 0.5


while True:
    while running:
        frame = cam.get_frame()
        h, w = frame.shape[:2]
        if frame is None:
            break
        frame, landmarks = pose.process(frame)

        # Old anchor detection
        # print("nose wrist " + str((distance("Nose", "RWrist", landmarks, w, h))))
        # if (distance("Nose", "RWrist", landmarks, w, h)) <= 115 and (distance("RShoulder", "RElbow", landmarks, w, h) > 115):
        #     cv2.putText(frame, "Anchor", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # New anchor detection
        print(str(distance("RWrist", "Nose", landmarks)))
        nose_wrist_dist = distance("RWrist", "Nose", landmarks)
        if nose_wrist_dist <= 0.21 and

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
