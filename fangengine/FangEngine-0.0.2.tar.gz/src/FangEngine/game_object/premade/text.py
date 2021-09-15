import typing

import pygame

import FangEngine.game_object.game_object as game_object

pygame.font.init()


class Text(game_object.GameObject):
    def __init__(
            self, screen_parent, x: float, y: float, text: str,
            font: pygame.font.Font, color: typing.Tuple[int, int, int] = (255, 255, 255),
            background: typing.Tuple[int, int, int] = None, antialias: bool = True, bold: bool = False,
            italic: bool = False, underline: bool = False, *args, **kwargs
    ):
        super().__init__(screen_parent, x, y, *args, **kwargs)

        self.font = font
        self.text = text
        self.color = color
        self.background = background
        self.antialias = antialias
        self.bold = bold
        self.italic = italic
        self.underline = underline

        self.font.set_bold(self.bold)
        self.font.set_italic(self.italic)
        self.font.set_underline(self.underline)

        self.rendered_text = None       # type: pygame.Surface

        self.set_text(self.text)

    def handle_input(self, keys: list, mouse: tuple, delta_t: float):
        pass

    def update(self, delta_t: float):
        pass

    def render(self, buffer: pygame.Surface):
        buffer.blit(self.rendered_text, (self.x, self.y))

    def set_text(self, text: str):
        self.text = text
        self.rendered_text = self.font.render(self.text, True, self.color, self.background)
        self.w, self.h = self.rendered_text.get_size()
