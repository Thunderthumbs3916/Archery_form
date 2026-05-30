import src.camera
import cv2
import src.pose

running = True
pose = src.pose.pose()


def distance(part1: str, part2: str, landmarks):
    dx = pose.get_coor(part1, landmarks).x - pose.get_coor((part2, landmarks)).x
    dy = pose.get_coor(part1, landmarks).y - pose.get_coor((part2, landmarks)).y
    return ((dx**2) + (dy**2))**0.5


while True:
    cam = src.camera.startVideo()
    while running:
        frame = cam.get_frame()
        if frame is None:
            break
        frame, landmarks = pose.process(frame)
        print(distance("RShoulder", "RElbow", landmarks))
        if ((distance("Nose", "RWrist", landmarks)) <= 0.2) :
            cv2.putText(frame, "Anchor", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Video", frame)
        cv2.waitKey(1)
        #draw

        if cv2.getWindowProperty("Video", cv2.WND_PROP_VISIBLE) < 1:
            running = False
    cam.release()
    cv2.destroyAllWindows()

    if input("Another shot?").lower() == "y":
        running = True
        continue
    else:
        #After ends
        break