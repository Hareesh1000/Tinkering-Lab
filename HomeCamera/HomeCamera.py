## pip install opencv-python

import os
from datetime import datetime
from pathlib import Path

import cv2

# Corrected and URL-encoded stream URL
stream_url = "rtsp://admin:Homecamera%4010@192.168.1.12:554"

# Path to save video in Documents folder
documents_path = Path.home() / "Documents" / "camera_recording"
documents_path.mkdir(parents=True, exist_ok=True)

date = datetime.now().strftime("%Y-%m-%d")
output_file = documents_path / f"camera_recording_{date}.avi"

# Create a VideoCapture object
cap = cv2.VideoCapture(stream_url)

# Check if the stream opened successfully
if not cap.isOpened():
    print("Error: Unable to open video stream")
    raise SystemExit(1)

# Get frame width and height
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 640
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 480

# Define codec and output file settings using a Windows-friendly format
codec_candidates = [("MJPG", ".avi"), ("mp4v", ".mp4"), ("avc1", ".mp4"), ("XVID", ".avi")]
out = None
for codec, ext in codec_candidates:
    candidate_file = documents_path / f"camera_recording_{date}{ext}"
    fourcc = cv2.VideoWriter_fourcc(*codec)
    out = cv2.VideoWriter(str(candidate_file), fourcc, 20.0, (frame_width, frame_height))
    if out.isOpened():
        output_file = candidate_file
        break
    out = None

if out is None or not out.isOpened():
    print("Error: Unable to initialize video writer")
    cap.release()
    raise SystemExit(1)

print(f"Recording... Saving to: {output_file}. Press Ctrl+C to stop.")

try:
    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Error: Cannot read frame from stream")
            break

        if frame.shape[1] != frame_width or frame.shape[0] != frame_height:
            frame = cv2.resize(frame, (frame_width, frame_height))

        out.write(frame)
        cv2.imshow("Live Stream", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
except KeyboardInterrupt:
    print("Recording stopped manually.")
finally:
    cap.release()
    if out is not None:
        out.release()
    cv2.destroyAllWindows()

print(f"Recording saved to: {output_file}")
