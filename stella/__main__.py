import argparse
import logging

from stella.gui.window import Window
from stella.tello.exceptions import TelloNoConnection
from stella.utils.logging import set_logging

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    set_logging(level=logging.DEBUG)

    try:
        window = Window()
        window.run()
    except TelloNoConnection:
        logging.debug("Cannot enable SDK, is Tello turned on?")
