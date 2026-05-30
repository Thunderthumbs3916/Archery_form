import src.camera
import cv2
import src.pose

running = True
pose = src.pose.pose()


def distance(part1: dict, part2: dict):
    dx = part1.x - part2.x
    dy = part1.y - part2.y
    return ((dx**2) + (dy**2))**0.5


while True:
    cam = src.camera.startVideo()
    while running:
        frame = cam.get_frame()
        if frame is None:
            break
        frame, landmarks = pose.process(frame)
        print(distance(pose.get_coor("Nose", landmarks), pose.get_coor("")))
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