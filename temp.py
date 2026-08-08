import mediapipe as mp
import sys

#print(mp.__file__)
#print(mp.__version__)
#print(hasattr(mp, "solutions"))
#print(dir(mp))

#print(sys.version)

import cv2

cap = cv2.VideoCapture(2, cv2.CAP_DSHOW)

while True:
    ret, frame = cap.read()
    print(ret)

    if not ret:
        break

    cv2.imshow("Camera 2", frame)

    if cv2.waitKey(1) == 27:   # ESC
        break

cap.release()
cv2.destroyAllWindows()