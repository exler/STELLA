import logging
import socket
import threading
from typing import Optional, Union

from stella.tello.constants import TELLO_STATE_PORT


class TelloState:
    FIELDS_TYPES_MAP = {
        "mid": int,
        "x": int,
        "y": int,
        "z": int,
        "pitch": int,
        "roll": int,
        "yaw": int,
        "vgx": int,
        "vgy": int,
        "vgz": int,
        "templ": int,
        "temph": int,
        "tof": int,
        "h": int,
        "bat": int,
        "time": int,
        "baro": float,
        "agx": float,
        "agy": float,
        "agz": float,
    }

    def __init__(self) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(("", TELLO_STATE_PORT))

        self._state: Optional[str] = None

        self.receive_thread = threading.Thread(target=self._receive_state, name="TelloStateReceiver", daemon=True)
        self.receive_thread.start()

    def _receive_state(self) -> None:
        while True:
            try:
                response, _ = self.socket.recvfrom(1024)
                self._state = response.decode("ascii")
            except Exception:
                logging.error("Unknown error occurred", exc_info=True)
                break

    def get_state(self) -> Optional[dict[str, Union[int, float, str]]]:
        if self._state is None:
            return None

        state: dict[str, Union[int, float, str]] = {}
        for field in self._state.split(";"):
            arr = field.split(":")
            if len(arr) < 2:
                continue

            key = arr[0]
            value: Union[int, float, str] = arr[1]

            if value in self.FIELDS_TYPES_MAP:
                value = self.FIELDS_TYPES_MAP[value](value)

            state[key] = value

        return state
