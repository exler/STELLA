import logging
import os
import time

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
from stella.gui.controls import KeyboardHandler
from stella.tello.client import TelloClient


class Window:
    CHECK_BATTERY = pygame.USEREVENT + 1

    def __init__(self, title: str = "STELLA", resolution: tuple[int, int] = (960, 720), fps: int = 60) -> None:
        self.fps = fps

        pygame.init()

        icon = pygame.image.load("stella/gui/assets/favicon.png")

        self.display = pygame.display.set_mode(resolution)
        pygame.display.set_caption(title)
        pygame.display.set_icon(icon)

        self.prepare_assets()

        self.tello = TelloClient()
        self.tello.connect()

        self.event_handler = KeyboardHandler(self.tello)

        self.battery_level = self.tello.get_battery()

        pygame.time.set_timer(self.CHECK_BATTERY, 15000)

    @property
    def resolution(self) -> tuple[int, int]:
        display_info = pygame.display.Info()
        return display_info.current_w, display_info.current_h

    def prepare_assets(self) -> None:
        self.font = pygame.font.SysFont("Arial", 16)

        self.logo_image = pygame.image.load("stella/gui/assets/logo.png")
        self.logo_image = pygame.transform.scale(self.logo_image, (160, 40))
        self.logo_image.convert_alpha()
        self.logo_image.set_alpha(180)
        self.logo_rect = self.logo_image.get_rect(center=(96, 32))

        self.battery_image = pygame.image.load("stella/gui/assets/battery.png")
        self.battery_image.convert_alpha()
        self.battery_rect = self.battery_image.get_rect(center=(self.resolution[0] - 72, 32))

    def draw_battery_level(self) -> None:
        battery_level_text = self.font.render(f"{self.battery_level}%", True, (255, 255, 255, 255))
        battery_level_rect = battery_level_text.get_rect(center=(self.resolution[0] - 56, 32))
        self.display.blit(self.battery_image, self.battery_rect)
        self.display.blit(battery_level_text, battery_level_rect)

    def draw_controls(self) -> None:
        width, height = self.resolution
        self.W_rect = pygame.draw.rect(self.display, (25, 25, 25), pygame.Rect(40, height - 80, 24, 24), width=2)
        self.S_rect = pygame.draw.rect(self.display, (25, 25, 25), pygame.Rect(40, height - 32, 24, 24), width=2)
        self.A_rect = pygame.draw.rect(self.display, (25, 25, 25), pygame.Rect(16, height - 56, 24, 24), width=2)
        self.D_rect = pygame.draw.rect(self.display, (25, 25, 25), pygame.Rect(64, height - 56, 24, 24), width=2)

        self.up_rect = pygame.draw.rect(
            self.display, (25, 25, 25), pygame.Rect(width - 66, height - 80, 24, 24), width=2
        )
        self.down_rect = pygame.draw.rect(
            self.display, (25, 25, 25), pygame.Rect(width - 66, height - 32, 24, 24), width=2
        )
        self.left_rect = pygame.draw.rect(
            self.display, (25, 25, 25), pygame.Rect(width - 90, height - 56, 24, 24), width=2
        )
        self.right_rect = pygame.draw.rect(
            self.display, (25, 25, 25), pygame.Rect(width - 42, height - 56, 24, 24), width=2
        )

    def run(self) -> None:
        def fill_control(rect: pygame.Rect) -> None:
            self.display.fill((255, 255, 102), rect, special_flags=pygame.BLEND_MAX)

        self.tello.enable_stream()
        stream = self.tello.stream

        if stream.frame is None:
            time.sleep(0.1)

        while True:
            try:
                surf = pygame.surfarray.make_surface(stream.frame)
                self.display.blit(surf, (0, 0))

                for e in pygame.event.get():
                    self.event_handler.handle(e)
                    if e.type == pygame.KEYDOWN:
                        if e.key == pygame.K_w:
                            fill_control(self.W_rect)
                        elif e.key == pygame.K_s:
                            fill_control(self.S_rect)
                        elif e.key == pygame.K_a:
                            fill_control(self.A_rect)
                        elif e.key == pygame.K_d:
                            fill_control(self.D_rect)
                        elif e.key == pygame.K_UP:
                            fill_control(self.up_rect)
                        elif e.key == pygame.K_DOWN:
                            fill_control(self.down_rect)
                        elif e.key == pygame.K_LEFT:
                            fill_control(self.left_rect)
                        elif e.key == pygame.K_RIGHT:
                            fill_control(self.right_rect)
                    elif e.type == self.CHECK_BATTERY:
                        self.tello.get_battery()

                self.display.blit(self.logo_image, self.logo_rect)
                self.draw_controls()
                self.draw_battery_level()
                pygame.display.update()

                time.sleep(1 / self.fps)
            except KeyboardInterrupt:
                logging.debug("Program terminated by user")
                break
