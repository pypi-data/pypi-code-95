import math
import typing

import pygame

import FangEngine.game_object.game_object as game_object

if typing.TYPE_CHECKING:
    import FangEngine.screen_manager.rotatable_screen.rotatable_screen_base as rotatable_screen_base

pygame.font.init()


class RotatableObject(game_object.GameObject):
    def __init__(
            self, screen_parent, x: float, y: float, angle: float, distance: float,
            image: typing.Union[str, pygame.Surface] = None, scale_x: float = 1, scale_y: float = None, *args, **kwargs
    ):
        super().__init__(screen_parent, x, y, *args, **kwargs)

        if isinstance(image, str):
            self.image_name = image
            self.image = self.IMAGE_STORE.get(image)            # type: pygame.Surface

        else:
            self.image_name = None
            self.image = image           # type: pygame.Surface

        if scale_y is None:
            scale_y = scale_x

        self.image = pygame.transform.scale(
            self.image, (int(self.image.get_width() * scale_x), int(self.image.get_height() * scale_y))
        )

        self.original_w, self.original_h = self.image.get_size()
        self.drawable = self.image.copy()

        self.screen_parent = self.screen_parent     # type: rotatable_screen_base.RotatableScreenBase

        self.angle = angle
        self.distance = distance
        self.set_distance(distance)

        self.center_x = self.screen_w / 2

        self.x = self.get_draw_x()

    def set_distance(self, distance: float):
        self.distance = distance
        self.image = pygame.transform.scale(self.image, (
            int(self.original_w / distance), int(self.original_h / distance)
        ))
        self.drawable = self.image.copy()

    def handle_input(self, keys: list, mouse: tuple, delta_t: float):
        pass

    def update(self, delta_t: float):
        pass

    def render(self, buffer: pygame.Surface):
        derivative = math.cos(self.angle - self.screen_parent.angle)
        if derivative >= 0:
            self.drawable = pygame.transform.scale(self.image, (
                int(self.image.get_width() * derivative), self.image.get_height()
            ))
            buffer.blit(self.drawable, (self.get_draw_x(), self.y))
            self.x = self.get_draw_x()

            self.w, self.h = self.drawable.get_size()

        else:
            self.w, self.h = (0, 0)

    def get_draw_x(self) -> float:

        return self.center_x + (
            self.distance * math.sin(self.angle - self.screen_parent.angle) * self.screen_parent.PIXELS_PER_METER
        ) - (self.drawable.get_width() / 2) # - (self.drawable.get_width() - self.image.get_width())
