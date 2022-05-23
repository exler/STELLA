import argparse
import logging

from stella.gui.window import Window
from stella.tello.client import TelloClient
from stella.utils.logging import set_logging

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    set_logging(level=logging.DEBUG)

    window = Window()

    tello = TelloClient()
    tello.connect()

    print(tello.get_battery())
    print(tello.enable_stream())

    try:
        while True:
            if tello.stream.frame is not None:
                window.run(tello.stream)
    except KeyboardInterrupt:
        pass
