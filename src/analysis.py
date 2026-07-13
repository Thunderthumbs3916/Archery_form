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

        return [(totx/count), (toty/count)]

    #def displacement(self, points):

    #def angle(self, p1, p2, p3):

    #def elbow_angle_displacement(self, shoulder, elbow, wrist):

    #def consistency_score(self,wrist_disp,elbow_disp,nose_disp):
