import logging

import pygame
from stella.tello.client import TelloClient
from stella.utils.files import save_photo


class KeyboardHandler:
    def __init__(self, tello: TelloClient) -> None:
        self.tello = tello

        self.S = 50

        self.forward_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0
        self.speed = 10

        self.send_rc_command = False

    def change_speed(self, change: int) -> None:
        if 0 < self.S + change <= 100:
            self.S += change

    def handle(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            self.keydown(event.key)
        elif event.type == pygame.KEYUP:
            self.keyup(event.key)
        elif event.type == pygame.QUIT:
            # self.tello.emergency()
            raise KeyboardInterrupt

        if self.send_rc_command:
            self.tello.set_rc(
                self.left_right_velocity,
                self.forward_back_velocity,
                self.up_down_velocity,
                self.yaw_velocity,
            )

    def keydown(self, key: int) -> None:
        if key == pygame.K_w:
            logging.debug("FORWARD")
            self.forward_back_velocity = self.S
        elif key == pygame.K_s:
            logging.debug("BACKWARD")
            self.forward_back_velocity = -self.S
        elif key == pygame.K_a:
            logging.debug("LEFT")
            self.left_right_velocity = -self.S
        elif key == pygame.K_d:
            logging.debug("RIGHT")
            self.left_right_velocity = self.S
        elif key == pygame.K_UP:
            logging.debug("UP")
            self.up_down_velocity = self.S
        elif key == pygame.K_DOWN:
            logging.debug("DOWN")
            self.up_down_velocity = -self.S
        elif key == pygame.K_LEFT:
            logging.debug("ROTATE LEFT")
            self.yaw_velocity = -self.S
        elif key == pygame.K_RIGHT:
            logging.debug("ROTATE RIGHT")
            self.yaw_velocity = self.S
        elif key == pygame.K_p:
            logging.debug("INCREASE SPEED")
            self.change_speed(10)
        elif key == pygame.K_o:
            logging.debug("DECREASE SPEED")
            self.change_speed(-10)
        elif key == pygame.K_SPACE:
            logging.debug("TAKEOFF")
            self.tello.takeoff()
            self.send_rc_command = True
        elif key == pygame.K_RETURN:
            logging.debug("LAND")
            self.tello.land()
            self.send_rc_command = False
        elif key == pygame.K_F12:
            logging.debug("TAKE PHOTO")
            if self.tello.stream.frame is not None:
                save_photo(self.tello.stream.frame)

    def keyup(self, key: int) -> None:
        if key == pygame.K_w or key == pygame.K_s:
            self.forward_back_velocity = 0
        elif key == pygame.K_a or key == pygame.K_d:
            self.left_right_velocity = 0
        elif key == pygame.K_UP or key == pygame.K_DOWN:
            self.up_down_velocity = 0
        elif key == pygame.K_LEFT or key == pygame.K_RIGHT:
            self.yaw_velocity = 0
