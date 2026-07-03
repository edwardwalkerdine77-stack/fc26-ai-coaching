import cv2
import time
import json
from analyzer import Analyzer
from coach import generate_coach_report


def run_analysis(video_path, output_path):

    analyzer = Analyzer(video_path)
    vision = analyzer.vision
    tracker = analyzer.tracker

    cap = cv2.VideoCapture(video_path)

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames <= 0:
        total_frames = 1

    SKIP = 4

    frame_id = 0
    processed = 0

    positions = []
    ball_positions = []

    zones = {"attack": 0, "midfield": 0, "defence": 0}

    passes = 0
    last_ball = None
    prev_ball = None
    cooldown = 0

    # ---------------- PHASE SYSTEM ----------------
    phases = {
        "build_up": 0,
        "progression": 0,
        "final_third": 0,
        "defensive": 0
    }

    phase_events = []
    prev_phase = None

    # ---------------- NEW SYSTEMS ----------------
    mistakes_timeline = []
    clips = []

    start_time = time.time()

    while cap.isOpened():

        ret, frame = cap.read()
        if not ret:
            break

        frame_id += 1

        if frame_id % SKIP != 0:
            continue

        frame = cv2.resize(frame, (640, 360))

        players, ball = vision.detect(frame)
        tracked = tracker.update(players)

        # ---------------- PLAYER + PHASE TRACKING ----------------
        current_phase = None
        frame_zones = {"attack": 0, "midfield": 0, "defence": 0}

        for p in tracked.values():
            x, y = p
            positions.append((x, y))

            if y < 120:
                phases["build_up"] += 1
                current_phase = "build_up"

            elif y < 240:
                phases["progression"] += 1
                current_phase = "progression"

            elif y < 320:
                phases["final_third"] += 1
                current_phase = "final_third"

            else:
                phases["defensive"] += 1
                current_phase = "defensive"

            if y < 120:
                frame_zones["attack"] += 1
            elif y < 240:
                frame_zones["midfield"] += 1
            else:
                frame_zones["defence"] += 1

        if frame_zones:
            dominant_zone = max(frame_zones, key=frame_zones.get)
            zones[dominant_zone] += 1

        # ---------------- PHASE TRANSITIONS ----------------
        if prev_phase and current_phase and prev_phase != current_phase:
            transition = f"transition_{prev_phase}_to_{current_phase}"

            if len(phase_events) == 0 or phase_events[-1] != transition:
                phase_events.append(transition)

                # ---------------- MISTAKE DETECTION ----------------
                if "final_third" in transition:
                    time_stamp = round(frame_id / 30, 2)

                    mistakes_timeline.append({
                        "time": time_stamp,
                        "type": "rushed_attack_transition"
                    })

                    clips.append({
                        "start": max(0, frame_id - 30),
                        "end": frame_id + 30,
                        "reason": "rushed_transition"
                    })

        prev_phase = current_phase

        # ---------------- BALL TRACKING ----------------
        if ball is not None:
            ball_positions.append(ball)
            prev_ball = last_ball
            last_ball = ball

        # ---------------- PASS DETECTION ----------------
        if last_ball is not None and prev_ball is not None and cooldown == 0:

            dist = ((last_ball[0] - prev_ball[0]) ** 2 +
                    (last_ball[1] - prev_ball[1]) ** 2) ** 0.5

            if 15 < dist < 250:
                passes += 1
                cooldown = 5

        if cooldown > 0:
            cooldown -= 1

        # ---------------- PROGRESS ----------------
        percent = int((frame_id / total_frames) * 100)

        elapsed = time.time() - start_time
        fps = processed / elapsed if elapsed > 0 else 1
        remaining = (total_frames - frame_id) / fps if fps > 0 else 0

        processed += 1

        result = {
            "percent": min(percent, 99),
            "remaining": max(0, remaining),
            "passes": passes,
            "zones": zones,
            "positions": len(positions),
            "balls": len(ball_positions),

            # CORE SYSTEM
            "phases": phases,
            "phase_events": phase_events,

            # NEW SYSTEMS
            "mistakes_timeline": mistakes_timeline,
            "clips": clips,

            "done": False
        }

        with open(output_path, "w") as f:
            json.dump(result, f)

    cap.release()

    # ---------------- FINAL REPORT ----------------
    try:
        result["coach_report"] = generate_coach_report(result)
    except:
        result["coach_report"] = {
            "playstyle": "Unknown",
            "issues": ["Insufficient data"],
            "strengths": [],
            "fix_plan": [],
            "training": []
        }

    result["done"] = True
    result["percent"] = 100

    with open(output_path, "w") as f:
        json.dump(result, f)