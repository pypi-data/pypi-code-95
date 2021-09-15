import abc
import typing

import pygame

import FangEngine.game_object.hitbox as hitbox
import FangEngine.store.asset_store.image_asset_store as image_asset_store
import FangEngine.store.asset_store.sound_asset_store as sound_asset_store

if typing.TYPE_CHECKING:
    import FangEngine.screen_manager.dialog_box as dialog_box
    import FangEngine.screen_manager.base_screen as base_screen
    import FangEngine.screen_manager.camera as camera


class GameObject(abc.ABC):
    IMAGE_STORE = image_asset_store.ImageAssetStore()
    SOUND_STORE = sound_asset_store.SoundAssetStore()

    def __init__(self, screen_parent: 'base_screen.BaseScreen', x: float, y: float, *args, **kwargs):
        self.screen_parent = screen_parent

        self.x = x
        self.y = y
        self.last_x = x
        self.last_y = y

        self.w = 0
        self.h = 0

        self.hitbox = hitbox.BoundHitbox(self)

    def on_message_receive(self, message: str, sender):
        pass

    def broadcast_message(self, message: typing.Union[list, tuple, str]):
        self.screen_parent.broadcast_message(message, self)

    def class_name(self) -> str:
        return self.__class__.__name__

    @property
    def camera(self) -> 'camera.Camera':
        return self.screen_parent.camera

    @property
    def screen_w(self) -> int:
        return self.screen_parent.screen_manager.screen_w

    @property
    def screen_h(self) -> int:
        return self.screen_parent.screen_manager.screen_h

    def convert_coords(self, x: float, y: float) -> typing.Tuple[float, float]:
        return self.screen_parent.convert_coords(x, y)

    def on_create(self, *args, **kwargs):
        pass

    def show_dialog_box(self, box: 'dialog_box.DialogBox.__class__', *args, **kwargs):
        self.screen_parent.show_dialog_box(box, *args, **kwargs)

    @abc.abstractmethod
    def handle_input(self, keys: list, mouse: tuple, delta_t: float):
        pass

    @abc.abstractmethod
    def update(self, delta_t: float):
        if self.last_x != self.x or self.last_y != self.y:
            self.on_move(self.x - self.last_x, self.y - self.last_y)

            self.last_x = self.x
            self.last_y = self.y

            self.check_collision()

    def check_collision(self):
        self.screen_parent.check_collisions(self)

    @property
    def class_name(self) -> str:
        return self.__class__.__name__

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

    def on_move(self, dx: float, dy: float):
        pass

    def on_collide(self, other: 'GameObject'):
        pass

    def on_click(self, pos: tuple, button: int):
        pass
