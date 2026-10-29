# import mediapipe as mp
# import sys
#
# #print(mp.__file__)
# print(mp.__version__)
# #print(hasattr(mp, "solutions"))
# #print(dir(mp))
#
# print(sys.version)

# import cv2
#
# cap = cv2.VideoCapture(2, cv2.CAP_DSHOW)
#
# while True:
#     ret, frame = cap.read()
#     print(ret)
#
#     if not ret:
#         break
#
#     cv2.imshow("Camera 2", frame)
#
#     if cv2.waitKey(1) == 27:   # ESC
#         break
#
# cap.release()
# cv2.destroyAllWindows()

# import json
# import src.analysis
#
# analyse = src.analysis.analyse()
# shot_num = 0
#
# with open("data/data.json", "r") as f:
#     all_shots = json.load(f)
#
# with open("data/samples.json", "w") as f:
#     json.dump({}, f)
#
# running_shots = {}
#
# for shot_name, shot_data in all_shots.items():
#     running_shots[shot_name] = shot_data
#     shot_str, combined_str, score, quality, consistency = analyse.anchor_analysis(shot_data["Anchor"], running_shots, shot_num)
#     shot_num += 1


import json, re, csv

PATH = "data/samples2.json"  # path to your BACKUP copy
num = r"-?\d+(?:\.\d+)?(?:e[-+]?\d+)?"
shots = json.load(open(PATH))
rows = []
for key, s in shots.items():
    wrist, nose, elbow = [float(x) for x in re.findall(num, s["small_str"])]
    rows.append([int(key.replace("Shot", "")), wrist, nose, elbow,
                 s["quality"], s["consistency"], s["score"]])
rows.sort(key=lambda r: r[0])
with open("scores_v0.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["shot_no", "wrist", "nose", "elbow", "threshold", "consistency", "final"])
    w.writerows(rows)
print(len(rows), "shots written")  # expect 37
