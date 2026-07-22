import math

def distance(x1, y1, x2, y2):
    return (((x2-x1)**2) + ((y2-y1)**2))**0.5
def angle(p1: dict, p2: dict, p3: dict):
    #law of cosines, finding angle at p2
    a = distance(p2.x, p2.y, p3.x, p3.y)
    b = distance(p1.x, p1.y, p2.x, p2.y)
    c = distance(p1.x, p1.y, p3.x, p3.y)

    temp = ((c**2) - (a**2) - (b**2))/(2*a*b)

    angle = math.degrees(math.acos(temp))
    return angle

class analyse():
    def __init__(self):

    #def anchor_analysis(self, data):

    def mean_position(self, points: dict, part):
        totx = 0
        toty = 0
        count = 0
        for key,value in points.items():
            if key == part:
                for frame in value:
                    if frame.x >= 0 and frame.y >= 0:
                        count += 1
                        totx = totx + frame.x
                        toty = toty + frame.y

        return (totx/count), (toty/count)

    def mean_displacement(self, points: dict, part):
        meanx, meany = self.mean_position(points, part)
        tot_dist = 0.00
        count = 0
        for key,value in points.items():
            if key==part:
                for frame in value:
                    tot_dist += distance(meanx, meany, frame.x, frame.y)
                    count += 1

        return tot_dist/count

    #def elbow_angle_displacement(self, shoulder, elbow, wrist):

    #def consistency_score(self,wrist_disp,elbow_disp,nose_disp):
