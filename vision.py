from ultralytics import YOLO

class Vision:

    def __init__(self):
        self.model = YOLO("models/yolov8n.pt")

    def detect(self, frame):

        results = self.model.predict(
            frame,
            imgsz=640,
            conf=0.10,
            iou=0.5,
            verbose=False
        )

        players = []
        ball_candidates = []

        for r in results:
            for box in r.boxes:

                cls = int(box.cls[0])
                x1, y1, x2, y2 = box.xyxy[0]

                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)

                # -------------------------
                # PLAYER DETECTION
                # -------------------------
                if cls == 0:
                    players.append((cx, cy))

                # -------------------------
                # BALL DETECTION (FIXED)
                # collect multiple instead of overwriting
                # -------------------------
                if cls == 32:
                    ball_candidates.append((cx, cy))

        # pick most recent/strongest detection
        ball = None
        if len(ball_candidates) > 0:
            ball = ball_candidates[-1]

        return players, ball