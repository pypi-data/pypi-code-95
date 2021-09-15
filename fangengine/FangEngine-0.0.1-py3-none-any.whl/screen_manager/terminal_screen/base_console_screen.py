import abc
import typing

import pygame

import FangEngine.screen_manager.terminal_screen.base_terminal_screen as base_terminal_screen

pygame.font.init()


class BaseConsoleScreen(base_terminal_screen.BaseTerminalScreen, abc.ABC):
    def __init__(self, name: str, manager, font: pygame.font.Font):
        self.prompt = ""
        self.commands = []
        self.input_line = []

        super().__init__(name, manager, font)

        self.set_prompt("> ")

    def set_prompt(self, prompt: str):
        self.prompt = prompt
        self.add_string(0, self.height - 1, " " * self.width)
        self.add_string(0, self.height - 1, self.prompt)

    @abc.abstractmethod
    def on_input(self, command: str):
        pass

    def add_text(self, text: str):
        self.commands.insert(0, text)
        self.redraw_text()

    def add_blank_line(self):
        self.commands.insert(0, "")
        self.redraw_text()

    def redraw_text(self):
        super(BaseConsoleScreen, self).clear_console()
        for line, cmd in enumerate(self.commands):
            try:
                self.add_string(0, self.height - (line + 2), cmd)
            except pygame.error:
                pass

        self.add_string(0, self.height - 1, self.prompt)

    def clear_console(self, color: typing.Tuple[int, int, int] = None):
        super(BaseConsoleScreen, self).clear_console(color)
        self.commands.clear()
        self.add_string(0, self.height - 1, self.prompt)

    def handle_input(self, keys: list, mouse: tuple, delta_t: float):
        pass

    def update(self, delta_t: float):
        pass

    def on_key_down(self, unicode, key, mod):
        if key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
            cmd = "".join(self.input_line)
            self.add_text(self.prompt + cmd)
            self.input_line.clear()
            self.on_input(cmd)
            self.add_string(0, self.height - 1, self.prompt)

        elif key == pygame.K_TAB:
            self.input_line += [" "] * 4

        elif key == pygame.K_BACKSPACE:
            try:
                del self.input_line[-1]
                self.add_character(len(self.input_line) + len(self.prompt), self.height - 1, " ")
            except IndexError:
                pass

        elif key >= pygame.K_SPACE:
            try:
                self.add_character(len(self.input_line) + len(self.prompt), self.height - 1, unicode)
                self.input_line.append(unicode)
            except ValueError:
                pass
