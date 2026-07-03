import streamlit as st
import threading
import json
from worker import add_job, get_result

st.set_page_config(page_title="EA FC AI COACH", layout="wide")
st.title("⚽ EA FC AI COACH")

# ---------------- SIDEBAR MODES ----------------
st.sidebar.title("⚽ EA FC Coach Mode")
mode = st.sidebar.selectbox(
    "Select Mode",
    ["Casual Analysis", "Ranked Review", "Pro Coaching"]
)

# ---------------- INPUT ----------------
video_url = st.text_input("Paste Match Video Link (Google Drive / MP4 URL)")

output_placeholder = st.empty()
progress_bar = st.progress(0)

if video_url:

    if st.button("Analyse Match"):

        job_id = add_job(video_url)

        st.success(f"Job started: {job_id}")

        while True:

            data = get_result(job_id)

            if data:

                percent = data.get("percent", 0)
                progress_bar.progress(min(percent, 99))

                output_placeholder.json(data)

                if data.get("done"):
                    break

        st.success("Analysis complete ✔")

        coach = data.get("coach_report", {})

        # ---------------- SUMMARY ----------------
        st.divider()
        st.subheader("⚽ Match Summary")

        summary = coach.get("summary", {})

        st.metric("Elite Rating", summary.get("elite_rating", 0))
        st.write("**Playstyle:**", summary.get("playstyle", "Unknown"))
        st.write("**Biggest Mistake:**", summary.get("biggest_mistake", "None"))

        # ---------------- ANALYSIS ----------------
        st.divider()
        st.subheader("📉 Performance Breakdown")

        analysis = coach.get("analysis", {})

        st.write("**Issues:**")
        st.write(analysis.get("issues", []))

        st.write("**Strengths:**")
        st.write(analysis.get("strengths", []))

        # ---------------- IMPROVEMENT ----------------
        st.divider()
        st.subheader("🎯 Improvement Plan")

        improvement = coach.get("improvement", {})

        st.write(improvement.get("fix_plan", []))

        st.subheader("📚 Training Suggestions")
        st.write(improvement.get("training", []))

        # ---------------- CLIPS ----------------
        st.divider()
        st.subheader("🎥 Mistake Clips")

        clips = data.get("clip_files", [])

        if clips:
            for c in clips:
                st.video(c)
        else:
            st.write("No clips detected.")