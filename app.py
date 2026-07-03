import streamlit as st
import time
from worker import *

st.set_page_config(page_title="EA FC AI PRO", layout="wide")
st.title("⚽ EA FC AI COACH PRO (15 WIN SYSTEM)")

if "started" not in st.session_state:
    start_worker()
    st.session_state.started = True

page = st.sidebar.radio("Menu", ["Upload", "Dashboard", "History"])

# ---------------- UPLOAD ----------------
if page == "Upload":

    file = st.file_uploader("Upload Match")

    if file:
        import tempfile
        temp = tempfile.NamedTemporaryFile(delete=False)
        temp.write(file.read())

        if st.button("Start Analysis"):
            job_id = add_job(temp.name)
            st.success(f"Job: {job_id}")

# ---------------- DASHBOARD ----------------
elif page == "Dashboard":

    job_id = st.text_input("Job ID")

    bar = st.progress(0)
    info = st.empty()

    if job_id:

        data = get_result(job_id)

        if data:

            bar.progress(min(data["percent"], 99))

            info.json({
                "status": data["status"],
                "fps": data["fps"]
            })

            if "heatmap" in data:
                st.subheader("Heatmap")
                st.pyplot(data["heatmap"])

            if "clips" in data:
                st.subheader("Clips")
                for c in data["clips"]:
                    st.video(c)

            if data["status"] == "done":
                st.success("Complete ✔")

        time.sleep(0.5)
        st.rerun()

# ---------------- HISTORY ----------------
elif page == "History":

    data = get_history()

    for job, d in data.items():
        st.divider()
        st.write(job)
        st.json(d)