import threading

import cv2
from stella.tello.constants import TELLO_STREAM_PORT


class TelloStream:
    def __init__(self) -> None:
        self.video = cv2.VideoCapture(f"udp://0.0.0.0:{TELLO_STREAM_PORT}")
        self.frame = None

        self.receive_thread = threading.Thread(target=self._receive_video, name="TelloStreamReceiver", daemon=True)
        self.receive_thread.start()

    def __del__(self) -> None:
        self.video.release()

    def _receive_video(self) -> None:
        while True:
            success, frame = self.video.read()
            if success:
                self.frame = frame
