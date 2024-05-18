import logging
import socket
import threading
import time
from enum import Enum
from typing import Optional

from stella.tello.constants import (
    RESPONSE_TIMEOUT,
    TELLO_CONTROL_PORT,
    TELLO_IP,
    TIME_BETWEEN_SAFE_COMMANDS,
    TIME_BETWEEN_UNSAFE_COMMANDS,
)
from stella.tello.exceptions import (
    TelloInvalidResponse,
    TelloNoConnection,
    TelloNoState,
)
from stella.tello.state import TelloState
from stella.tello.stream import TelloStream


class TelloControlResponse(bytes, Enum):
    OK = b"ok"
    ERROR = b"error"


class TelloFlipDirection(str, Enum):
    LEFT = "l"
    RIGHT = "r"
    FORWARD = "f"
    BACK = "b"


class TelloClient:
    def __init__(self) -> None:
        self.tello_address = (TELLO_IP, TELLO_CONTROL_PORT)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(("", TELLO_CONTROL_PORT))

        self.response: Optional[bytes] = None
        self.last_received_timestamp: float = 0
        self.last_unsafe_command: float = 0

        self.receive_thread = threading.Thread(
            target=self._receive, name="TelloControlReceiver", daemon=True
        )
        self.receive_thread.start()

        self.state = TelloState()
        self.stream: Optional[TelloStream] = None

    def __del__(self) -> None:
        self.socket.close()

    def _receive(self) -> None:
        while True:
            try:
                self.response, _ = self.socket.recvfrom(1024)
                logging.debug(f"Control data received: {self.response}")
            except Exception:
                logging.error("Unknown error occurred", exc_info=True)
                break

    def connect(self, wait_for_state: bool = True) -> None:
        try:
            self.send_safe("command")  # Enable SDK mode
        except TimeoutError:
            raise TelloNoConnection("Could not enable SDK mode")

        if wait_for_state:
            for i in range(10):
                if self.state.get_state():
                    logging.debug(f"Tello state received on {i+1} iteration")
                    break

                time.sleep(0.1)

            if not self.state.get_state():
                raise TelloNoState("Did not receive a state packet from Tello")

    def send_safe(self, command: str) -> str:
        diff = time.time() - self.last_received_timestamp
        if diff < TIME_BETWEEN_SAFE_COMMANDS:
            time.sleep(diff)

        self.socket.sendto(command.encode("utf-8"), self.tello_address)
        timestamp = time.time()

        while self.response is None:
            if time.time() - timestamp > RESPONSE_TIMEOUT:
                raise TimeoutError("Tello did not respond in time")
            time.sleep(0.1)

        self.last_received_timestamp = time.time()
        response, self.response = self.response, None

        return response

    def send_unsafe(self, command: str) -> None:
        diff = time.time() - self.last_unsafe_command
        if diff > TIME_BETWEEN_UNSAFE_COMMANDS:
            self.socket.sendto(command.encode("utf-8"), self.tello_address)
            self.last_unsafe_command = time.time()

    """
    Control Commands
    """

    def takeoff(self) -> None:
        """
        Auto takeoff.
        """

        self.send_unsafe("takeoff")

    def land(self) -> None:
        """
        Auto landing.
        """

        self.send_unsafe("land")

    def enable_stream(self) -> TelloControlResponse:
        """
        Enable video stream.
        """

        response = TelloControlResponse(self.send_safe("streamon"))
        self.stream = TelloStream()
        return response

    def disable_stream(self) -> TelloControlResponse:
        """
        Disable video stream.
        """

        response = TelloControlResponse(self.send_safe("streamoff"))
        self.stream = None
        return response

    def emergency(self) -> TelloControlResponse:
        """
        Stop motors immediately.
        """

        return TelloControlResponse(self.send_safe("emergency"))

    def up(self, x: int) -> TelloControlResponse:
        if x < 20 or x > 500:
            raise ValueError("Value must be in range (20;500)")

        return TelloControlResponse(self.send_safe(f"up {x}"))

    def down(self, x: int) -> TelloControlResponse:
        if x < 20 or x > 500:
            raise ValueError("Value must be in range (20;500)")

        return TelloControlResponse(self.send_safe(f"down {x}"))

    def left(self, x: int) -> TelloControlResponse:
        if x < 20 or x > 500:
            raise ValueError("Value must be in range (20;500)")

        return TelloControlResponse(self.send_safe(f"left {x}"))

    def right(self, x: int) -> TelloControlResponse:
        if x < 20 or x > 500:
            raise ValueError("Value must be in range (20;500)")

        return TelloControlResponse(self.send_safe(f"right {x}"))

    def cw(self, x: int) -> TelloControlResponse:
        if x < 1 or x > 360:
            raise ValueError("Value must be in range (1;360)")

        return TelloControlResponse(self.send_safe(f"cw {x}"))

    def ccw(self, x: int) -> TelloControlResponse:
        if x < 1 or x > 360:
            raise ValueError("Value must be in range (1;360)")

        return TelloControlResponse(self.send_safe(f"ccw {x}"))

    def flip(self, x: TelloFlipDirection) -> TelloControlResponse:
        return TelloControlResponse(self.send_safe(f"flip {x.value}"))

    def go(self, x: int, y: int, z: int, speed: int) -> TelloControlResponse:
        if any(v for v in [x, y, z] if v < -500 or x > 500):
            raise ValueError("Coordinates must be in range (-500;500)")

        if speed < 10 or speed > 100:
            raise ValueError("Speed must be in range(10;100)")

        return TelloControlResponse(self.send_safe(f"go {x} {y} {z} {speed}"))

    def stop(self) -> TelloControlResponse:
        """
        Hovers in the air.

        Notes:
            Works at any time.
        """

        return TelloControlResponse(self.send_safe("stop"))

    def curve(
        self, x1: int, y1: int, z1: int, x2: int, y2: int, z2: int, speed: int
    ) -> TelloControlResponse:
        if any(v for v in [x1, y1, z1, x2, y2, z2] if v < -500 or v > 500):
            raise ValueError("Coordinates must be in range (-500;500)")

        if speed < 10 or speed > 100:
            raise ValueError("Speed must be in range(10;100)")

        return TelloControlResponse(
            self.send_safe(f"curve {x1} {y1} {z1} {x2} {y2} {z2} {speed}")
        )

    """
    Set Commands
    """

    def set_speed(self, x: int) -> TelloControlResponse:
        if x < 10 or x > 100:
            raise ValueError("Speed must be in range (10;100)")

        return TelloControlResponse(self.send_safe(f"speed {x}"))

    def set_rc(self, a: int, b: int, c: int, d: int) -> None:
        """
        Set remote controller control via four channels.

        Args:
            - a: left/right (-100 - 100)
            - b: forward/backward (-100 - 100)
            - c: up/down (-100 - 100)
            - d: yaw (-100 - 100)
        """

        if any(x for x in [a, b, c, d] if x < -100 or x > 100):
            raise ValueError("Parameters must be in range (-100;100)")

        return self.send_unsafe(f"rc {a} {b} {c} {d}")

    def set_wifi(self, ssid: str, password: str) -> TelloControlResponse:
        """
        Set Wi-Fi SSID and password.
        """

        return TelloControlResponse(self.send_safe(f"wifi {ssid} {password}"))

    def set_ap(self, ssid: str, password: str) -> TelloControlResponse:
        """
        Set the Tello to station mode and connect to a new access point with the specified SSID and password.
        """

        return TelloControlResponse(self.send_safe(f"ap {ssid} {password}"))

    """
    Read Commands
    """

    def get_speed(self) -> float:
        response = self.send_safe("speed?")

        try:
            return float(response)
        except ValueError:
            raise TelloInvalidResponse("get_speed returned non-float")

    def get_battery(self) -> int:
        response = self.send_safe("battery?")

        try:
            return int(response)
        except ValueError:
            raise TelloInvalidResponse("get_battery returned non-integer")

    def get_flight_time(self) -> int:
        """Gets current flight time in seconds."""

        response = self.send_safe("time?")

        try:
            return int(response)
        except ValueError:
            raise TelloInvalidResponse("get_flight_time returned non-integer")

    def get_wifi(self) -> int:
        """Gets WiFi SNR (signal-to-noise ratio, signal strength)."""

        response = self.send_safe("wifi?")

        try:
            return int(response)
        except ValueError:
            raise TelloInvalidResponse("get_wifi returned non-integer")

    def get_sdk(self) -> str:
        """Gets Tello SDK version."""

        return self.send_safe("sdk?")

    def get_sn(self) -> str:
        """Gets Tello serial number."""

        return self.send_safe("sn?")
