import math
import json


def distance(x1, y1, x2, y2):
    return (((x2 - x1) ** 2) + ((y2 - y1) ** 2)) ** 0.5


def angle(p1: dict, p2: dict, p3: dict):
    # law of cosines, finding angle at p2

    a = distance(p2["x"], p2["y"], p3["x"], p3["y"])
    b = distance(p1["x"], p1["y"], p2["x"], p2["y"])
    c = distance(p1["x"], p1["y"], p3["x"], p3["y"])

    temp = ((a ** 2) + (b ** 2) - (c ** 2)) / (2 * a * b)
    if temp > 1:
        temp = 1
    elif temp < -1:
        temp = -1

    return math.degrees(math.acos(temp))


def displacement(list):
    if len(list) != 0:
        if type(list[0]) == type({"wofheof": "eofhiw"}):
            meanx = sum(p["x"] for p in list) / len(list)
            meany = sum(p["y"] for p in list) / len(list)
            tot = sum(distance(meanx, meany, p["x"], p["y"]) for p in list)
        else:
            mean_val = sum(list) / len(list)
            tot = sum(abs(v - mean_val) for v in list)

        return tot / len(list)


class analyse():
    def __init__(self):
        pass

    def format_analysis(self, title, wrist_disp, nose_disp, angle_disp):
        return (f"\n ----- {title} -----\n"
                f"Mean displacement of draw/right wrist: {wrist_disp}\n"
                f"Mean displacment of nose: {nose_disp}\n"
                f"Mean displacement of angle made by draw wrist, shoulder and elbow: {angle_disp}")

    def anchor_analysis(self, data, all_shots, shot_num):
        wrist_disp = self.mean_displacement(data, "draw_wrist")
        if wrist_disp != -1:
            wrist_disp *= 1000

        nose_disp = self.mean_displacement(data, "nose")
        if nose_disp != -1:
            nose_disp *= 10000

        anchor_str = self.format_analysis("New Shot", wrist_disp,
                                          nose_disp,
                                          self.elbow_angle_displacement(data))
        combined_str = self.cross_shot_analysis(all_shots)
        self.save_analysis(f"Shot{shot_num}", anchor_str, combined_str)
        print(anchor_str + "\n" + combined_str)
        return anchor_str, combined_str

    def save_analysis(self, shot_key, shot_str, combined_str):

        try:
            with open("data/samples.json", "r") as f:
                curr_samples = json.load(f)
        except FileNotFoundError:
            curr_samples = {}

        curr_samples[shot_key] = {"small_str": shot_str, "combined": combined_str}

        with open('data/samples.json', "w") as f:
            json.dump(curr_samples, f, indent=2)

    def cross_shot_analysis(self, all_shots):
        wrist_means = []
        nose_means = []
        angle_means = []

        for shot in all_shots.values():
            data = shot["Anchor"]

            wrist_disp = self.mean_displacement(data, "draw_wrist")
            if wrist_disp != -1:
                wrist_means.append(wrist_disp)

            nose_disp = self.mean_displacement(data, "nose")
            if nose_disp != -1:
                nose_means.append(nose_disp)

            mean_angle = self.mean_angle(data)
            if mean_angle is not None:
                angle_means.append(mean_angle)

        mystr = self.format_analysis(
            "All shots combined",
            displacement(wrist_means) * 1000,
            displacement(nose_means) * 10000,
            displacement(angle_means)
        )
        return mystr

    def mean_position(self, points: dict, part):
        totx = 0
        toty = 0
        count = 0

        for frame in points[part]:
            if frame["x"] >= 0 and frame["y"] >= 0:
                count += 1
                totx = totx + frame["x"]
                toty = toty + frame["y"]

        if count == 0:
            return None, None
        return (totx / count), (toty / count)

    def mean_displacement(self, points: dict, part):
        meanx, meany = self.mean_position(points, part)
        tot_dist = 0.0
        count = 0

        for frame in points[part]:
            if frame["x"] >= 0 and frame["y"] >= 0:
                tot_dist += distance(meanx, meany, frame["x"], frame["y"])
                count += 1

        if count == 0:
            return -1
        return tot_dist / count

    def mean_angle(self, points: dict):
        tot_angle = 0.0
        count = 0
        for frame_num in range(len(points["draw_wrist"])):
            if (points["draw_wrist"][frame_num]["x"] >= 0 and points["draw_wrist"][frame_num]["y"] >= 0 and
                    points["draw_shoulder"][frame_num]["x"] >= 0 and points["draw_shoulder"][frame_num]["y"] >= 0 and
                    points["draw_elbow"][frame_num]["x"] >= 0 and points["draw_elbow"][frame_num]["y"] >= 0):
                curr_angle = angle(points["draw_wrist"][frame_num], (points["draw_shoulder"][frame_num]),
                                   (points["draw_elbow"][frame_num]))
                tot_angle += curr_angle
                count += 1

        if count == 0:
            return None
        return tot_angle / count

    def elbow_angle_displacement(self, points: dict):
        mean_angle = self.mean_angle(points)
        if mean_angle is None:
            return -1

        tot_displacement = 0
        count = 0

        for frame_num in range(len(points["draw_wrist"])):
            if (points["draw_wrist"][frame_num]["x"] >= 0 and points["draw_wrist"][frame_num]["y"] >= 0 and
                    points["draw_shoulder"][frame_num]["x"] >= 0 and points["draw_shoulder"][frame_num]["y"] >= 0 and
                    points["draw_elbow"][frame_num]["x"] >= 0 and points["draw_elbow"][frame_num]["y"] >= 0):
                curr_angle = angle(points["draw_wrist"][frame_num], (points["draw_shoulder"][frame_num]),
                                   (points["draw_elbow"][frame_num]))
                tot_displacement += abs(curr_angle - mean_angle)
                count += 1

        return tot_displacement / count

    # def consistency_score(self,wrist_disp,elbow_disp,nose_disp):
