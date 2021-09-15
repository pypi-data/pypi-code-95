import typing

import pygame

import FangEngine.game_object.premade.rotatable_object as rotatable_object

pygame.font.init()


class RotatableText(rotatable_object.RotatableObject):
    def __init__(
            self, screen_parent, x: float, y: float, angle: float, distance: float, text: str,
            font: pygame.font.Font, color: typing.Tuple[int, int, int] = (255, 255, 255),
            background: typing.Tuple[int, int, int] = None, antialias: bool = True, bold: bool = False,
            italic: bool = False, underline: bool = False, *args, **kwargs
    ):
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

        super().__init__(screen_parent, x, y, angle, distance, self.rendered_text, *args, **kwargs)

    def set_text(self, text: str):
        self.text = text
        self.rendered_text = self.font.render(self.text, True, self.color, self.background)
