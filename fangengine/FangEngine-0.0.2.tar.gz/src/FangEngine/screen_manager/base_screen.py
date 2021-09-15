import abc
import typing

import pygame

import FangEngine.screen_manager.camera as camera

if typing.TYPE_CHECKING:
    import FangEngine.screen_manager.dialog_box as dialog_box
    import FangEngine.screen_manager.screen_manager as screen_manager


class BaseScreen(abc.ABC):
    def __init__(self, name: str, manager, *args, **kwargs):
        self.name = name                        # type: str
        self.screen_manager = manager           # type: screen_manager.ScreenManager
        self.dialog_boxes = []                  # type: typing.List[dialog_box.DialogBox]
        self.PIXELS_PER_METER = 100
        self.camera = camera.Camera()

    def on_create(self):
        pass

    @property
    def screen_w(self) -> int:
        return self.screen_manager.screen_w

    def center_mouse(self):
        pygame.mouse.set_pos(
            int(self.screen_w / 2), int(self.screen_h / 2)
        )
        pygame.event.clear(pygame.MOUSEMOTION, pump=False)
        pygame.mouse.get_rel()

    def center_mouse_x(self):
        curr = pygame.mouse.get_pos()
        pygame.mouse.set_pos(
            int(self.screen_w / 2), curr[1]
        )
        pygame.event.clear(pygame.MOUSEMOTION, pump=False)
        pygame.mouse.get_rel()

    def center_mouse_y(self):
        curr = pygame.mouse.get_pos()
        pygame.mouse.set_pos(
            curr[0], int(self.screen_h / 2)
        )
        pygame.event.clear(pygame.MOUSEMOTION, pump=False)
        pygame.mouse.get_rel()

    def hide_mouse(self):
        pygame.mouse.set_visible(False)

    def show_mouse(self):
        pygame.mouse.set_visible(True)

    @property
    def screen_h(self) -> int:
        return self.screen_manager.screen_h

    def is_showing_dialog_box(self) -> bool:
        return len(self.dialog_boxes) > 0

    def show_dialog_box(self, box: 'dialog_box.DialogBox.__class__', *args, **kwargs):
        self.dialog_boxes.insert(0, box(self, *args, **kwargs))

    def convert_coords(self, x: float, y: float) -> typing.Tuple[float, float]:
        return x - self.camera.x, y - self.camera.y

    def play_sound(self, sound: pygame.mixer.Sound, loops: int = 0, left: float = 1.0, right: float = 1.0):
        channel = pygame.mixer.Sound.play(sound, loops=loops)
        channel.set_volume(left, right)

    def get_cursor_pos(self) -> typing.Tuple[float, float]:
        return self.screen_manager.scale_coords(pygame.mouse.get_pos())

    def on_message_receive(self, message: str, sender):
        pass

    def broadcast_message(self, message: typing.Union[list, tuple, str], sender=None):
        if sender is None:
            sender = self

        if self != sender:
            self.on_message_receive(message, sender)

    @abc.abstractmethod
    def handle_input(self, keys: list, mouse: tuple, delta_t: float):
        pass

    @abc.abstractmethod
    def update(self, delta_t: float):
        pass

    @abc.abstractmethod
    def render(self, buffer: pygame.Surface):
        pass

    def on_key_down(self, unicode, key, mod):
        pass

    def on_key_up(self, key, mod):
        pass

    def on_mouse_motion(self, pos, rel, buttons):
        pass

    def on_mouse_button_up(self, pos, button):
        pass

    def on_mouse_button_down(self, pos, button):
        pass

    def on_joystick_axis_motion(self, joystick, axis, value):
        pass

    def on_joystick_ball_motion(self, joystick, ball, rel):
        pass

    def on_joystick_hat_motion(self, joystick, hat, value):
        pass

    def on_joystick_button_up(self, joystick, button):
        pass

    def on_joystick_button_down(self, joystick, button):
        pass

    def on_screen_enter(self, previous_screen: str):
        pass

    def on_screen_leave(self, next_screen: str):
        pass
