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

def threshold_score(value, breakpoints):
    if value <= breakpoints[0][0]:
        return breakpoints[0][1]

    for i in range(1, len(breakpoints)):
        v0, s0 = breakpoints[i-1]
        v1, s1 = breakpoints[i]
        if value <= v1:
            frac = (value-v0) / (v1-v0)
            return s0 + frac*(s1-s0)
    return breakpoints[-1][1]

WRIST_QUALITY_BREAKPOINTS = [(0, 100), (6, 90), (16, 70), (30, 40), (32, 20)]
NOSE_QUALITY_BREAKPOINTS = [(0, 100), (25, 90), (40, 70), (60, 40)]
ANGLE_QUALITY_BREAKPOINTS = [(0, 100), (8, 90), (10, 80), (20, 50)]

class analyse():
    def __init__(self):
        pass

    def format_analysis(self, title, wrist_disp, nose_disp, angle_disp, mode: int):
        if mode == 1:
            return (f"\n ----- {title} -----\n"
                    f"Mean displacement of draw/right wrist: {wrist_disp}\n"
                    f"Mean displacment of nose: {nose_disp}\n"
                    f"Mean displacement of angle made by draw wrist, shoulder and elbow: {angle_disp}")
        elif mode == 2:
            return (f"\n ----- {title} -----\n"
                    f"Mean displacement of the Mean displacement of draw/right wrist: {wrist_disp}\n"
                    f"Mean displacement of the Mean displacment of nose: {nose_disp}\n"
                    f"mean displacement of the Mean displacement of angle made by draw wrist, shoulder and elbow: {angle_disp}")

    def anchor_analysis(self, data, all_shots, shot_num):
        wrist_disp = self.mean_displacement(data, "draw_wrist")
        if wrist_disp != -1:
            wrist_disp *= 1000

        nose_disp = self.mean_displacement(data, "nose")
        if nose_disp != -1:
            nose_disp *= 10000

        angle_disp = self.elbow_angle_displacement(data)

        anchor_str = self.format_analysis("New Shot", wrist_disp,
                                          nose_disp,
                                          angle_disp, 1)

        combined_str, stats = self.cross_shot_analysis(all_shots)
        score, quality, consistency = self.shot_score(wrist_disp, nose_disp, angle_disp, stats)
        score_str = f"\n Consistency score: {score}"

        wrist_conf = self.mean_visibility(data, "draw_wrist")
        nose_conf = self.mean_visibility(data, "nose")
        conf_str = f"[debug] wrist confidence: {wrist_conf}, nose confidence: {nose_conf}"

        self.save_analysis(f"Shot{shot_num}", anchor_str, combined_str, score, quality, consistency)
        print(anchor_str + "\n" + combined_str + score_str)
        print(conf_str)
        print(f"{score} is your consistency score, {quality} is score based on thresholds, "
              f"{consistency} is score based on deviation from mean")
        return anchor_str, combined_str, score, quality, consistency

    def save_analysis(self, shot_key, shot_str, combined_str, score, quality, consistency):

        try:
            with open("data/samples.json", "r") as f:
                curr_samples = json.load(f)
        except FileNotFoundError:
            curr_samples = {}

        curr_samples[shot_key] = {"small_str": shot_str, "combined": combined_str, "score": score, "quality": quality, "consistency": consistency}

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

            # angle_disp = self.elbow_angle_displacement(data)
            # if angle_disp != -1:
            #     angle_means.append(angle_disp)

            mean_angle = self.mean_angle(data)
            if mean_angle is not None:
                angle_means.append(mean_angle)

        wrist_avg, wrist_spread = self.mean_and_spread(wrist_means)
        nose_avg, nose_spread = self.mean_and_spread(nose_means)
        angle_avg, angle_spread = self.mean_and_spread(angle_means)

        if wrist_avg is not None:
            wrist_avg *= 1000
            wrist_spread *= 1000
        if nose_avg is not None:
            nose_avg *= 10000
            nose_spread *= 10000

        mystr = self.format_analysis("All shots combined", wrist_spread, nose_spread, angle_spread, 2)

        stats = {"wrist": (wrist_avg, wrist_spread),
                 "nose": (nose_avg, nose_spread),
                 "angle": (angle_avg, angle_spread)}
        return mystr, stats


    def mean_and_spread(self, values):
        if len(values)==0:
            return None, None
        mean_val = sum(values)/len(values)
        tot = sum(abs(v-mean_val) for v in values)
        return mean_val, tot/len(values)

    def quality_score(self, wrist_disp, nose_disp, angle_disp):
        scores = []
        if wrist_disp != -1:
            scores.append(threshold_score(wrist_disp, WRIST_QUALITY_BREAKPOINTS))
        if nose_disp != -1:
            scores.append(threshold_score(nose_disp, NOSE_QUALITY_BREAKPOINTS))
        if angle_disp != -1:
            scores.append(threshold_score(angle_disp, ANGLE_QUALITY_BREAKPOINTS))

        if len(scores) == 0:
            return None
        return sum(scores)/len(scores)

    def consistency_score(self, wrist_disp, nose_disp, angle_disp, stats):
        scores = []

        for value, key in ((wrist_disp, "wrist"), (nose_disp, "nose"), (angle_disp, "angle")):
            if value == -1:
                continue
            mean_val, spread = stats[key]
            if mean_val is None:
                continue
            if spread == 0:
                scores.append(100)
            else:
                deviation = abs(value - mean_val) / spread
                scores.append(100 / (1+deviation))

        if len(scores) == 0:
            return None
        return sum(scores)/len(scores)

    def shot_score(self, wrist_disp, nose_disp, angle_disp, stats):
        quality = self.quality_score(wrist_disp, nose_disp, angle_disp)
        consistency = self.consistency_score(wrist_disp, nose_disp, angle_disp, stats)

        if quality is None and consistency is None:
            return None
        if quality is None:
            return consistency
        if consistency is None:
            return quality
        return (quality + consistency)/2 , quality, consistency

    def mean_visibility(self, points: dict, part):
        total = 0
        count = 0
        for frame in points[part]:
            if "visibility" in frame:
                total += frame["visibility"]
                count += 1
        if count==0:
            return None
        return total/count

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
