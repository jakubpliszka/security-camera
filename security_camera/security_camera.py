import cv2
import datetime
import threading
import time
import numpy as np


from pymongo import MongoClient


class SecurityCamera:
    FOREGROUND_RATIO_THRESHOLD = 0.01

    def __init__(self, name: str = "Camera 1", location: str = "Room") -> None:
        self.name = name
        self.location = location

        # initialize the camera (use the first camera device available)
        self.camera = cv2.VideoCapture(0)
        time.sleep(2)  # Warm up the camera
        self.running = False

        # connect to the MongoDB database
        client = MongoClient("mongodb://localhost:27017/")
        db = client["security"]
        self.collection = db["motions"]

    def start(self) -> None:
        # early exit if the camera is already running
        if self.running:
            return

        self.running = True

        # start a background thread for capturing frames
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def stop(self) -> None:
        self.running = False
        # start a background thread for standby mode
        self.thread = threading.Thread(target=self.standby)
        self.thread.start()

    def run(self) -> None:
        # initialize the background model
        background_subtractor = cv2.createBackgroundSubtractorMOG2()

        # capture frames from the camera and detect motion
        while self.running:
            ret, frame = self.camera.read()
            if not ret:
                break

            # apply the background subtraction algorithm to the frame
            foreground_mask = background_subtractor.apply(frame)

            # apply morphological operations to remove noise from the mask
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            foreground_mask = cv2.morphologyEx(
                foreground_mask, cv2.MORPH_OPEN, kernel)

            # calculate the percentage of the mask that is "foreground" (i.e., motion)
            foreground_area = cv2.countNonZero(foreground_mask)
            total_area = foreground_mask.shape[0] * foreground_mask.shape[1]
            foreground_ratio = foreground_area / total_area

            # if the percentage of foreground is above a threshold, motion is detected
            if foreground_ratio > self.FOREGROUND_RATIO_THRESHOLD:
                self.motion_detected(frame)
                print("Motion Detected")

            # display the original frame and the foreground mask for debugging
            cv2.imshow("Original Frame", frame)
            cv2.imshow("Foreground Mask", foreground_mask)

            # wait for a key press to exit the loop
            if cv2.waitKey(1) == ord('q'):
                break

        # cClean up
        self.camera.release()
        cv2.destroyAllWindows()

    def motion_detected(self, frame: np.ndarray) -> None:
        # get the current time
        now = datetime.datetime.now()

        # create a document to insert into the database
        motion_event = {
            "time": now,
            "location": self.location,
            "camera": self.name,
            "description": "Motion Detected",
            "image": frame
        }

        # insert the document into the database
        self.collection.insert_one(motion_event)

    def standby(self) -> None:
        while not self.running:
            time.sleep(1)
            print("Standby Mode")
