import abc
import typing
import pygame

import FangEngine.screen_manager.dialog_box as dialog_box


class ImageDialogBox(dialog_box.DialogBox, abc.ABC):
    def __init__(self, screen_parent, background_image: pygame.Surface, *args, **kwargs):
        super().__init__(screen_parent, *args, **kwargs)
        self.fill_background = False
        self.background_image = pygame.transform.scale(background_image, [int(i) for i in self.size])

    def render(self, buffer: pygame.Surface):
        self.buffer.blit(self.background_image, (0, 0))

        if self.show_close_button:
            self.buffer.blit(self.close_button, (self.close_button_x, self.close_button_y))

        self.dialog_render(self.buffer)

        buffer.blit(self.buffer, (self.x, self.y))

    @abc.abstractmethod
    def dialog_render(self, buffer: pygame.Surface):
        pass

    def close(self):
        self.__del__()

    def on_mouse_button_down(self, pos, button):
        if self.close_button_x <= pos[0] <= self.close_button_x + self.close_button_w and \
                self.close_button_y <= pos[1] <= self.close_button_y + self.close_button_h:
            self.close()

        super(ImageDialogBox, self).on_mouse_button_down(pos, button)

    def convert_coords(self, x: float, y: float) -> typing.Tuple[float, float]:
        return x - self.x, y - self.y
