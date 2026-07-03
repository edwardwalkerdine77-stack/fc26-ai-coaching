import cv2
import numpy as np
from vision import Vision
from tracker import Tracker

class Analyzer:

    def __init__(self, video_path):
        self.video_path = video_path
        self.vision = Vision()
        self.tracker = Tracker()

    def zone(self, y):
        if y < 180:
            return "attack"
        elif y < 360:
            return "midfield"
        return "defence"

    def run(self):

        cap = cv2.VideoCapture(self.video_path)

        frame_id = 0

        positions = []
        ball_positions = []

        zones = {"attack": 0, "midfield": 0, "defence": 0}

        passes = 0
        last_ball = None
        pass_cooldown = 0

        while cap.isOpened():

            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (960, 540))

            players, ball = self.vision.detect(frame)
            tracked = self.tracker.update(players)

            # -------------------------
            # PLAYER POSITIONS
            # -------------------------
            for p in tracked.values():
                x, y = p

                if 0 <= x <= 960 and 0 <= y <= 540:
                    positions.append((x, y))
                    zones[self.zone(y)] += 1

            # -------------------------
            # BALL + PASS LOGIC
            # -------------------------
            if ball:
                ball_positions.append(ball)

                if last_ball and pass_cooldown == 0:
                    dist = np.linalg.norm(np.array(ball) - np.array(last_ball))

                    if 25 < dist < 250:
                        passes += 1
                        pass_cooldown = 8

                last_ball = ball

            if pass_cooldown > 0:
                pass_cooldown -= 1

            frame_id += 1

        cap.release()

        stats = {
            "passes": passes,
            "zones": zones,
            "positions": len(positions),
            "ball": len(ball_positions)
        }

        return positions, ball_positions, stats