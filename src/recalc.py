import csv, json, re
from src.analysis import analyse

DATA = "../data/data.json"

ERROR_SHOTS = {38: "head", 39: "head", 40: "head",
               41: "wrist", 42: "wrist", 43: "wrist",
               44: "elbow", 45: "elbow", 46: "elbow"}


def get_anchor(shot):
    if "Anchor" in shot:
        return shot["Anchor"]
    if "draw_wrist" in shot:
        return shot


an = analyse()

with open(DATA) as f:
    all_shots = json.load(f)

rows = {}
for i, key in enumerate(all_shots.keys(), start=1):
    numbers = re.findall(r"\d+", key)
    shot_no = int(numbers[0]) if numbers else i
    subset = {k: all_shots[k] for k in list(all_shots.keys())[:i]}

    data = all_shots[key]["Anchor"]
    wrist = an.mean_displacement(data, "draw_wrist")
    if wrist != -1:
        wrist *= 1000
    nose = an.mean_displacement(data, "nose")
    if nose != -1:
        nose *= 10000
    angle = an.elbow_angle_displacement(data)

    my_str, stats = an.cross_shot_analysis(subset)
    score, quality, consistency = an.shot_score(wrist, nose, angle, stats)
    rows[shot_no] = (wrist, nose, angle, quality, consistency, score)

with open(f"../data/newscores.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["shot", "wrist", "nose", "angle", "threshold", "consistency", "final"])
    for shot_no, values in rows.items():
        writer.writerow([shot_no] + ["" if v is None else round(v, 7) for v in values])
