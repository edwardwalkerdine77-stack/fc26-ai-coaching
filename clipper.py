import cv2

def export_clips(video_path, clips):

    cap = cv2.VideoCapture(video_path)

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    outputs = []

    for i, clip in enumerate(clips):

        start = clip["start"]
        end = clip["end"]

        cap.set(cv2.CAP_PROP_POS_FRAMES, start)

        out_path = f"clip_{i}.mp4"

        writer = cv2.VideoWriter(
            out_path,
            cv2.VideoWriter_fourcc(*'mp4v'),
            fps,
            (width, height)
        )

        for f in range(start, end):
            ret, frame = cap.read()
            if not ret:
                break
            writer.write(frame)

        writer.release()
        outputs.append(out_path)

    cap.release()
    return outputs