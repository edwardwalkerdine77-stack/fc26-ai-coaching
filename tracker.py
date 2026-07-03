from scipy.spatial import distance

class Tracker:

    def __init__(self):
        self.objects = {}
        self.next_id = 0

    def update(self, detections):

        new_objects = {}
        used = set()

        for obj_id, prev in self.objects.items():

            best = None
            best_d = 999999

            for i, det in enumerate(detections):

                if i in used:
                    continue

                d = distance.euclidean(prev, det)

                if d < 70 and d < best_d:
                    best_d = d
                    best = i

            if best is not None:
                new_objects[obj_id] = detections[best]
                used.add(best)

        for i, det in enumerate(detections):
            if i not in used:
                new_objects[self.next_id] = det
                self.next_id += 1

        self.objects = new_objects
        return self.objects