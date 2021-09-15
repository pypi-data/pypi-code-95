from abc import ABC

import pygame
import typing

import FangEngine.screen_manager.object_screen as object_screen


class BaseGridScreen(object_screen.ObjectScreen, ABC):
    def __init__(self, name: str, manager):
        super().__init__(name, manager)

        self.grid_w = 32
        self.grid_h = 32

        self.tile_w = 10
        self.tile_h = 32

        self.show_grid = True
        self.grid_color = (255, 255, 255)
        self.grid_thickness = 2

    def convert_coords(self, x: float, y: float) -> typing.Tuple[float, float]:
        coords = super().convert_coords(x, y)

        return coords[0] * self.grid_w, coords[1] * self.grid_h

    def render(self, buffer: pygame.Surface):
        if self.show_grid:
            self.draw_grid(buffer)

        super().render(buffer)

    def draw_grid(self, buffer: pygame.Surface):
        for i in range(self.tile_w + 1):
            pygame.draw.line(
                buffer, (255, 255, 255), self.convert_coords(i, 0),
                self.convert_coords(i, self.tile_h), self.grid_thickness
            )

        for i in range(self.tile_h + 1):
            pygame.draw.line(
                buffer, (255, 255, 255), self.convert_coords(0, i),
                self.convert_coords(self.tile_w, i), self.grid_thickness
            )

