import streamlit as st
import tempfile
import time
import json
import threading

from worker import run_analysis

st.set_page_config(page_title="EA FC AI COACH", layout="wide")
st.title("⚽ EA FC AI COACH")

video = st.file_uploader("Upload Match Video")

if video:

    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write(video.read())
    path = temp.name

    st.video(path)

    output_file = "result.json"

    # ---------------- FRIEND MODE ----------------
    st.sidebar.title("⚽ EA FC Coach Mode")
    mode = st.sidebar.selectbox(
        "Select Mode",
        ["Casual Analysis", "Ranked Review", "Pro Coaching"]
    )

    if st.button("Analyse Match"):

        thread = threading.Thread(
            target=run_analysis,
            args=(path, output_file)
        )
        thread.start()

        progress = st.progress(0)
        status = st.empty()

        # ---------------- LOADING LOOP ----------------
        while True:

            try:
                with open(output_file, "r") as f:
                    data = json.load(f)

                if "percent" not in data:
                    time.sleep(0.2)
                    continue

            except:
                time.sleep(0.2)
                continue

            percent = data.get("percent", 0)
            remaining = data.get("remaining", 0)

            mins = int(remaining // 60)
            secs = int(remaining % 60)

            progress.progress(min(percent, 99))
            status.text(f"Analysing... {percent}% | {mins}m {secs}s")

            if data.get("done"):
                break

            time.sleep(0.2)

        progress.progress(100)
        status.text("Analysis complete ✔")

        coach = data.get("coach_report", {})

        summary = coach.get("summary", {})
        analysis = coach.get("analysis", {})
        improvement = coach.get("improvement", {})

        st.divider()

        # ---------------- MATCH SUMMARY ----------------
        st.subheader("⚽ Match Summary")

        st.metric("Elite Rating", summary.get("elite_rating", 0))
        st.write("**Playstyle:**", summary.get("playstyle", "Unknown"))
        st.write("**Biggest Mistake:**", summary.get("biggest_mistake", "None"))

        st.divider()

        # ---------------- BREAKDOWN ----------------
        st.subheader("📉 Performance Breakdown")

        st.write("**Issues:**")
        st.write(analysis.get("issues", []))

        st.write("**Strengths:**")
        st.write(analysis.get("strengths", []))

        st.divider()

        # ---------------- IMPROVEMENT ----------------
        st.subheader("🎯 Improvement Plan")
        st.write(improvement.get("fix_plan", []))

        st.subheader("📚 Training Suggestions")
        st.write(improvement.get("training", []))

        st.divider()

        # ---------------- CLIPS ----------------
        st.subheader("🎥 Mistake Clips")

        clips = data.get("clip_files", [])

        if not clips:
            st.write("No clips detected in this match.")
        else:
            for clip in clips:
                st.video(clip)

else:
    st.info("Upload a video to start analysis")