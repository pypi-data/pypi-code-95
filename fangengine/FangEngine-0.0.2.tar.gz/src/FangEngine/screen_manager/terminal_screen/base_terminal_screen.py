import typing
from abc import ABC

import pygame

import FangEngine.game_object.premade.character as character
import FangEngine.screen_manager.object_screen as object_screen

pygame.font.init()


class BaseTerminalScreen(object_screen.ObjectScreen, ABC):
    BLACK = (0, 0, 0)
    DARK_BLUE = (0, 0, 128)
    DARK_GREEN = (0, 128, 0)
    DARK_CYAN = (0, 128, 128)
    DARK_RED = (128, 0, 0)
    DARK_MAGENTA = (128, 0, 128)
    DARK_YELLOW = (128, 128, 0)
    DARK_WHITE = (192, 192, 192)
    BRIGHT_BLACK = (128, 128, 128)
    BRIGHT_BLUE = (0, 0, 255)
    BRIGHT_GREEN = (0, 255, 0)
    BRIGHT_CYAN = (0, 255, 255)
    BRIGHT_RED = (255, 0, 0)
    BRIGHT_MAGENTA = (255, 0, 255)
    BRIGHT_YELLOW = (255, 255, 0)
    WHITE = (255, 255, 255)

    def __init__(
            self, name: str, manager, font: pygame.font.Font, default_text_color: typing.Tuple[int, int, int] = None,
            default_background_color: typing.Tuple[int, int, int] = None
    ):
        super().__init__(name, manager)

        if default_text_color is None:
            default_text_color = self.WHITE

        if default_background_color is None:
            default_background_color = self.BLACK

        self.font = font
        self.fill_console = None
        self.default_text_color = default_text_color
        self.background_color = default_background_color

        self.char_w, self.char_h = self.font.size("M")

        self.height = int(self.screen_h / self.char_h)
        self.width = int(self.screen_w / self.char_w)

        self.clear_console()

    def render(self, buffer: pygame.Surface):
        if self.fill_console is not None:
            buffer.fill(self.fill_console)
            self.fill_console = None

        super(BaseTerminalScreen, self).render(buffer)

    def add_string(
            self, x: int, y: int, text: str, color: typing.Tuple[int, int, int] = None,
            background: typing.Tuple[int, int, int] = None, antialias: bool = True, bold: bool = False,
            italic: bool = False, underline: bool = False
    ):
        for i, char in enumerate(text):
            self.add_character(
                x + i, y, char, color, background, antialias, bold, italic, underline
            )

    def add_character(
            self, x: int, y: int, text: str, color: typing.Tuple[int, int, int] = None,
            background: typing.Tuple[int, int, int] = None, antialias: bool = True, bold: bool = False,
            italic: bool = False, underline: bool = False
    ):
        if color is None:
            color = self.default_text_color

        if background is None:
            background = self.background_color

        self.spawn_object(
            character.Character, x * self.char_w, y * self.char_h, text, self.font, color, background, antialias, bold,
            italic, underline
        )

    def clear_console(self, color: typing.Tuple[int, int, int] = None):
        self.clear_game_objects()

        if color is None:
            color = self.BLACK

        self.background_color = color
        self.fill_console = color
