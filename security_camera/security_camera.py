import collections
import os
import threading
import time
from datetime import datetime, timezone

import cv2

RECORDINGS_DIR = os.path.join(os.path.dirname(__file__), "recordings")
os.makedirs(RECORDINGS_DIR, exist_ok=True)


class SecurityCamera:
    FOREGROUND_RATIO_THRESHOLD = 0.01
    PRE_BUFFER_SECONDS = 5
    POST_BUFFER_SECONDS = 5

    def __init__(self, name: str = "Camera 1", location: str = "Room") -> None:
        self.name = name
        self.location = location

        self.camera = cv2.VideoCapture(0)
        self.recording = False

        self._fps = int(self.camera.get(cv2.CAP_PROP_FPS)) or 30
        self._width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        self._height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self._frame_buffer = collections.deque(maxlen=self.PRE_BUFFER_SECONDS * self._fps)
        self._lock = threading.Lock()
        self._stop_recording_event = threading.Event()

        self.latest_frame = None

        self._running = True
        self._thread = threading.Thread(target=self.run, daemon=True)
        self._thread.start()

    def __del__(self) -> None:
        self._running = False
        self._stop_recording_event.set()
        self._thread.join()

    def run(self) -> None:
        background_subtractor = cv2.createBackgroundSubtractorMOG2()
        last_motion_time = None
        recording_thread = None
        self.recording = False
        self._stop_recording_event.clear()

        while self._running:
            ret, frame = self.camera.read()
            if not ret:
                print("Failed to read frame from camera")
                continue

            self.latest_frame = frame.copy()

            # add frame to pre-buffer (for motion‐triggered recording)
            with self._lock:
                self._frame_buffer.append(frame.copy())

            foreground_mask = background_subtractor.apply(frame)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            foreground_mask = cv2.morphologyEx(foreground_mask, cv2.MORPH_OPEN, kernel)
            foreground_area = cv2.countNonZero(foreground_mask)
            total_area = foreground_mask.shape[0] * foreground_mask.shape[1]
            foreground_ratio = foreground_area / total_area

            if foreground_ratio > self.FOREGROUND_RATIO_THRESHOLD:
                last_motion_time = time.time()
                if not self.recording:
                    print("Motion Detected - Start Recording")
                    self.recording = True
                    self._stop_recording_event.clear()
                    recording_thread = threading.Thread(target=self.record_video, daemon=True)
                    recording_thread.start()
            else:
                if (
                    self.recording
                    and last_motion_time is not None
                    and time.time() - last_motion_time > self.POST_BUFFER_SECONDS
                ):
                    print("No motion - stop recording")
                    self._stop_recording_event.set()
                    if recording_thread:
                        recording_thread.join()

                    self.recording = False
                    last_motion_time = None

        self.camera.release()

    def record_video(self) -> None:
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(RECORDINGS_DIR, f"motion_{timestamp}.avi")
        out = cv2.VideoWriter(filename, fourcc, self._fps, (self._width, self._height))

        # write pre-buffered frames first
        with self._lock:
            pre_buffer = list(self._frame_buffer)

        for frame in pre_buffer:
            out.write(frame)

        # write frames until stop event is set
        while not self._stop_recording_event.is_set() and self._running:
            ret, frame = self.camera.read()
            if not ret:
                print("Failed to read frame from camera")
                continue

            out.write(frame)

        out.release()
