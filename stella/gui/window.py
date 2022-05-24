import logging
import os
import time

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
from stella.gui.controls import KeyboardHandler
from stella.tello.client import TelloClient


class Window:
    def __init__(self, title: str = "STELLA", resolution: tuple[int, int] = (960, 720), fps: int = 120) -> None:
        self.fps = fps

        pygame.init()

        icon = pygame.image.load("stella/gui/assets/favicon.png")

        self.display = pygame.display.set_mode(resolution)
        pygame.display.set_caption(title)
        pygame.display.set_icon(icon)

        self.tello = TelloClient()
        self.tello.connect()

        self.event_handler = KeyboardHandler(self.tello)

        logging.info(f"Tello battery level: {self.tello.get_battery()}")

    def run(self) -> None:
        self.tello.enable_stream()
        stream = self.tello.stream

        if stream.frame is None:
            time.sleep(0.1)

        while True:
            try:
                for e in pygame.event.get():
                    self.event_handler.handle(e)

                surf = pygame.surfarray.make_surface(stream.frame)
                self.display.blit(surf, (0, 0))
                pygame.display.update()

                time.sleep(1 / self.fps)
            except KeyboardInterrupt:
                logging.debug("Program terminated by user")
                break
