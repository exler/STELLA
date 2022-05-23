import os

from stella.tello.stream import TelloStream

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
from stella.gui.controls import KeyboardHandler


class Window:
    def __init__(self, title: str = "STELLA", resolution: tuple[int, int] = (960, 720)) -> None:
        pygame.init()

        self.display = pygame.display.set_mode(resolution)
        pygame.display.set_caption(title)

        self.event_handler = KeyboardHandler()

    def run(self, stream: TelloStream) -> None:
        while True:
            try:
                for e in pygame.event.get():
                    self.event_handler.handle(e)

                surf = pygame.surfarray.make_surface(stream.frame)
                self.display.blit(surf, (0, 0))
                pygame.display.update()
            except KeyboardInterrupt:
                return
