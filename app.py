import os
import time
from typing import List

import cv2
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse

from security_camera.security_camera import RECORDINGS_DIR, SecurityCamera

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

camera = SecurityCamera()


@app.get("/videos", response_model=List[str])
def list_videos():
    files = os.listdir(RECORDINGS_DIR)
    videos = [f for f in files if f.endswith(".avi")]
    videos.sort(reverse=True)
    return videos


@app.get("/videos/{filename}")
def get_video(filename: str):
    file_path = os.path.join(RECORDINGS_DIR, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Video not found")
    return FileResponse(file_path, media_type="video/x-msvideo", filename=filename)


def mjpeg_generator():
    boundary = b"--frame\r\n"
    while True:
        frame = camera.latest_frame
        if frame is None:
            time.sleep(1)
            continue

        ret, jpeg = cv2.imencode(".jpg", frame)
        if not ret:
            continue

        img_bytes = jpeg.tobytes()
        yield (
            boundary
            + b"Content-Type: image/jpeg\r\n"
            + f"Content-Length: {len(img_bytes)}\r\n\r\n".encode("utf-8")
            + img_bytes
            + b"\r\n"
        )


@app.get("/video_feed")
def video_feed() -> StreamingResponse:
    return StreamingResponse(
        mjpeg_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )
