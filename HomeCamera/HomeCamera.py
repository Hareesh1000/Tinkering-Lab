## pip install opencv-python

import cv2
import os
from datetime import datetime
from pathlib import Path

# Corrected and URL-encoded stream URL
stream_url = "rtsp://admin:Homecamera%4010@192.168.1.12:554"

# Path to save video in Documents folder
documents_path = os.path.join(os.path.expanduser('~'), 'Documents/camera_recording')
# documents_path = Path.home() / 'Documents' / 'camera_recording'

date = datetime.now().strftime('%Y-%m-%d')
output_file = os.path.join(documents_path, f'camera_recording_{date}.mp4')

# Create a VideoCapture object
cap = cv2.VideoCapture(stream_url)

# Check if the stream opened successfully
if not cap.isOpened():
    print("Error: Unable to open video stream")
    exit()

# Get frame width and height
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Define codec and output file settings (use MP4)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_file, fourcc, 20.0, (frame_width, frame_height))

print(f"Recording... Saving to: {output_file}. Press Ctrl+C to stop.")

try:
    while True:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
            # Optional: display the stream
            cv2.imshow('Live Stream', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            print("Error: Cannot read frame from stream")
            break
except KeyboardInterrupt:
    print("Recording stopped manually.")

# Release resources
cap.release()
out.release()
cv2.destroyAllWindows()

print(f"Recording saved to: {output_file}")
