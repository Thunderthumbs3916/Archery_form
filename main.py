import src.camera
import cv2
import src.pose

running = True
pose = src.pose.pose()

while True:
    cam = src.camera.startVideo()
    while running:
        frame = cam.get_frame()
        if frame is None:
            break
        frame, landmarks = pose.process(frame)
        cv2.imshow("Video", frame)
        cv2.waitKey(1)
        #draw

        if cv2.getWindowProperty("Video", cv2.WND_PROP_VISIBLE) < 1:
            running = False
    cam.release()
    cv2.destroyAllWindows()

    if input("Another end?").lower() == "y":
        running = True
        continue
    else:
        #After ends
        break
