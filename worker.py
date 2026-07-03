import cv2
import time
import queue
import threading
import uuid

from vision import Vision
from tracker import Tracker
from coach import generate_coach_report
from clipper import export_clips
from heatmap import heatmap

job_queue = queue.Queue()
results = {}
history = {}
cancel_flags = {}

# ---------------- START WORKER ----------------
def worker_loop():
    while True:
        job_id, video_input = job_queue.get()

        if cancel_flags.get(job_id):
            results[job_id] = {"status": "cancelled"}
            job_queue.task_done()
            continue

        results[job_id] = {
            "status": "processing",
            "percent": 0,
            "fps": 0
        }

        run_analysis(video_input, job_id)

        if not cancel_flags.get(job_id):
            results[job_id]["status"] = "done"
            history[job_id] = results[job_id]

        job_queue.task_done()


def start_worker():
    threading.Thread(target=worker_loop, daemon=True).start()


# ---------------- JOB API ----------------
def add_job(video_input):
    job_id = str(uuid.uuid4())[:8]
    job_queue.put((job_id, video_input))
    return job_id


def cancel_job(job_id):
    cancel_flags[job_id] = True


def get_result(job_id):
    return results.get(job_id)


def get_history():
    return history


# ---------------- CORE ANALYSIS ENGINE ----------------
def run_analysis(video_input, job_id):

    vision = Vision()
    tracker = Tracker()

    cap = cv2.VideoCapture(video_input)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1

    SKIP = 4
    frame_id = 0
    processed = 0

    start_time = time.time()

    positions = []
    ball_positions = []

    phases = {
        "build_up": 0,
        "progression": 0,
        "final_third": 0,
        "defensive": 0
    }

    phase_events = []
    clips = []

    last_phase = None
    last_ball = None

    while cap.isOpened():

        if cancel_flags.get(job_id):
            results[job_id]["status"] = "cancelled"
            cap.release()
            return

        ret, frame = cap.read()
        if not ret:
            break

        frame_id += 1
        if frame_id % SKIP != 0:
            continue

        frame = cv2.resize(frame, (640, 360))

        players, ball = vision.detect(frame)
        tracked = tracker.update(players)

        current_phase = None

        # ---------------- PLAYER DATA ----------------
        for x, y in tracked.values():
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

        # ---------------- PHASE TRACKING ----------------
        if last_phase and current_phase and last_phase != current_phase:
            phase_events.append(f"{last_phase}_to_{current_phase}")

            if current_phase == "final_third":
                clips.append({
                    "start": max(0, frame_id - 20),
                    "end": frame_id + 20,
                    "reason": "attacking_transition"
                })

        last_phase = current_phase

        # ---------------- BALL ----------------
        if ball:
            ball_positions.append(ball)

            if last_ball:
                dist = ((ball[0]-last_ball[0])**2 + (ball[1]-last_ball[1])**2) ** 0.5

        last_ball = ball

        # ---------------- PROGRESS ----------------
        processed += 1

        elapsed = max(time.time() - start_time, 0.1)
        fps = processed / elapsed
        percent = int((frame_id / total_frames) * 100)

        results[job_id].update({
            "percent": min(percent, 99),
            "fps": round(fps, 2),
            "processed": processed,
            "status": "processing"
        })

    cap.release()

    # ---------------- HEATMAP ----------------
    heatmap_data = heatmap(positions)

    # ---------------- COACH REPORT ----------------
    stats = {
        "passes": len(ball_positions) // 2,
        "zones": {
            "attack": phases["final_third"],
            "midfield": phases["progression"],
            "defence": phases["defensive"]
        },
        "positions": len(positions),
        "balls": len(ball_positions),
        "phases": phases,
        "phase_events": phase_events
    }

    try:
        report = generate_coach_report(stats)
    except:
        report = {"summary": {"playstyle": "Unknown"}}

    # ---------------- EXPORT CLIPS ----------------
    clip_files = export_clips(video_input, clips)

    results[job_id].update({
        "percent": 100,
        "status": "done",
        "coach_report": report,
        "clips": clip_files,
        "heatmap": heatmap_data
    })