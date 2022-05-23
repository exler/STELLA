import logging
import threading
from typing import Optional

import av
import numpy as np
from stella.tello.constants import TELLO_STREAM_PORT

logging.getLogger("libav").setLevel(logging.FATAL)


class TelloStream:
    def __init__(self) -> None:
        self.video = av.open(f"udp://0.0.0.0:{TELLO_STREAM_PORT}")
        self.frame: Optional[np.ndarray] = None

        self.receive_thread = threading.Thread(target=self._receive_video, name="TelloStreamReceiver", daemon=True)
        self.receive_thread.start()

    def __del__(self) -> None:
        self.video.close()

    def _receive_video(self) -> None:
        for frame in self.video.decode(video=0):
            frame_arr = frame.to_ndarray(format="rgb24")
            frame_arr = np.rot90(frame_arr)
            frame_arr = np.flipud(frame_arr)
            self.frame = frame_arr
