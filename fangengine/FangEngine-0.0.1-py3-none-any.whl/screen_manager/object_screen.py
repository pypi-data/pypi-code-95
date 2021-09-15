import typing

import pygame

import FangEngine.screen_manager.base_screen as base_screen

if typing.TYPE_CHECKING:
    import FangEngine.game_object.game_object as game_object


class ObjectScreen(base_screen.BaseScreen):
    def __init__(self, name: str, manager):
        super().__init__(name, manager)
        self.game_objects = []                  # type: typing.List[game_object.GameObject]

    def clear_game_objects(self):
        self.game_objects.clear()

    def spawn_object(
            self, object_class_ref: 'game_object.GameObject.__class__', x: float, y: float, *args, **kwargs
    ) -> 'game_object.GameObject':
        obj = object_class_ref(self, x, y, *args, **kwargs)     # type: game_object.GameObject
        obj.on_create(*args, **kwargs)

        self.game_objects.append(obj)
        return obj

    def check_collisions(self, child: 'game_object.GameObject'):
        for c in self.game_objects:
            if c == child:
                continue

            if c.hitbox.is_hitbox_colliding(child.hitbox):
                child.on_collide(c)
                c.on_collide(child)

    def handle_input(self, keys: list, mouse: tuple, delta_t: float):
        for child in self.game_objects:
            child.handle_input(keys, mouse, delta_t)

    def update(self, delta_t: float):
        for child in self.game_objects:
            child.update(delta_t)

    def render(self, buffer: pygame.Surface):
        for child in self.game_objects:
            child.render(buffer)

    def on_key_down(self, unicode, key, mod):
        for child in self.game_objects:
            child.on_key_down(unicode, key, mod)

    def on_key_up(self, key, mod):
        for child in self.game_objects:
            child.on_key_up(key, mod)

    def on_mouse_motion(self, pos, rel, buttons):
        for child in self.game_objects:
            child.on_mouse_motion(pos, rel, buttons)

    def on_mouse_button_up(self, pos, button):
        for child in self.game_objects:
            child.on_mouse_button_up(pos, button)

    def on_mouse_button_down(self, pos, button):
        obj = self.game_objects[:]
        obj.reverse()

        for child in obj:
            child.on_mouse_button_down(pos, button)

            if child.hitbox.is_point_colliding(*pos):
                if child.on_click(pos, button) is not True:
                    break

    def on_joystick_axis_motion(self, joystick, axis, value):
        for child in self.game_objects:
            child.on_joystick_axis_motion(joystick, axis, value)

    def on_joystick_ball_motion(self, joystick, ball, rel):
        for child in self.game_objects:
            child.on_joystick_ball_motion(joystick, ball, rel)

    def on_joystick_hat_motion(self, joystick, hat, value):
        for child in self.game_objects:
            child.on_joystick_hat_motion(joystick, hat, value)

    def on_joystick_button_up(self, joystick, button):
        for child in self.game_objects:
            child.on_joystick_button_up(joystick, button)

    def on_joystick_button_down(self, joystick, button):
        for child in self.game_objects:
            child.on_joystick_button_down(joystick, button)

    def on_screen_enter(self, previous_screen: str):
        for child in self.game_objects:
            child.on_screen_enter(previous_screen)

    def on_screen_leave(self, next_screen: str):
        for child in self.game_objects:
            child.on_screen_leave(next_screen)

    def broadcast_message(self, message: typing.Union[list, tuple, str], sender=None):
        if sender is None:
            sender = self

        for child in self.game_objects:
            child.on_message_receive(message, sender)

        super(ObjectScreen, self).broadcast_message(message, sender)
