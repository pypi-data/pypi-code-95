import math

import pygame
import typing

import FangEngine.display_methods.sprite_sheet as sprite_sheet
import FangEngine.game_object.premade.rotatable_object as rotatable_object

pygame.font.init()
WIDTH = 150


class RotatableSpriteSheet(rotatable_object.RotatableObject):
    def __init__(
            self, screen_parent, x: float, y: float, angle: float, distance: float,
            image: str, tiles_wide: int, tiles_high: int, frames: int, speed: float = 0.1,
            scale_w: float = 1, scale_h: float = 1, color_key: typing.Tuple[int, int, int] = (255, 0, 255),
            *args, **kwargs
    ):

        self.sprite_sheet = sprite_sheet.SpriteSheet(
            image, tiles_wide, tiles_high, frames, speed, scale_w, scale_h, color_key=color_key
        )

        self.image_name = image
        self.image = self.IMAGE_STORE.get(image)            # type: pygame.Surface

        super().__init__(screen_parent, x, y, angle, distance, image, *args, **kwargs)

    def handle_input(self, keys: list, mouse: tuple, delta_t: float):
        pass

    def update(self, delta_t: float):
        pass

    def render(self, buffer: pygame.Surface):
        img = self.sprite_sheet.get_current_image()

        derivative = math.cos(self.angle - self.screen_parent.angle)
        if derivative >= 0:
            self.drawable = pygame.transform.scale(img, (
                int(img.get_width() * derivative), img.get_height()
            ))
            buffer.blit(self.drawable, (self.get_draw_x(), self.y))
            self.x = self.get_draw_x()

            self.w, self.h = self.drawable.get_size()

        else:
            self.w, self.h = (0, 0)
