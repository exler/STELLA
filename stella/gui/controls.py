import pygame


class KeyboardHandler:
    def handle(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            pass
