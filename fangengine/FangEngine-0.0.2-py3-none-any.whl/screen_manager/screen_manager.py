import pygame
import screeninfo
import os
import typing

import FangEngine.status_codes as status_codes
import FangEngine.store.asset_store.image_asset_store as image_asset_store
import FangEngine.store.asset_store.sound_asset_store as sound_asset_store
import FangEngine.graphics_options as graphics_options

if typing.TYPE_CHECKING:
    import FangEngine.screen_manager.base_screen as screen

pygame.init()
pygame.mixer.init()


class ScreenManager:
    def __init__(
            self, screen_w: int = 800, screen_h: int = 450, fullscreen: bool = False, monitor: int = 0,
            show_cursor: bool = True, caption: str = "FangEngine Application", framerate_cap: int = 60,
            icon_path: str = None
    ):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.fullscreen = fullscreen
        self.monitor = monitor
        self.show_cursor = show_cursor
        self.caption = caption
        self.icon_path = icon_path
        self.framerate_cap = framerate_cap

        self.scale_factor = 1
        self.showing_screen = False
        self.surface = None                 # type: pygame.Surface
        self.buffer = None                  # type: pygame.Surface
        self.fps = 0                        # type: float
        self.screens = {}                   # type: typing.Dict[str, screen.BaseScreen]
        self.selected_screen = None         # type: screen.BaseScreen

        self.buff_draw_x = 0
        self.buff_draw_y = 0

        sound_asset_store.SoundAssetStore()
        image_asset_store.ImageAssetStore()

    def show_graphics_options(self, caption: str = None, icon_path: str = None) -> 'ScreenManager':
        if caption is None:
            caption = self.caption

        if icon_path is None:
            icon_path = self.icon_path

        opt = graphics_options.get_options(caption, icon_path)

        self.fullscreen = opt["fullscreen"]
        self.monitor = opt["monitor"]
        self.framerate_cap = opt["framerate"]

        return self

    def add_screen(self, name: str, screen_cls: 'screen.BaseScreen.__class__', *args, **kwargs) -> 'ScreenManager':
        new_screen = screen_cls(name, self, *args, **kwargs)        # type: screen.BaseScreen
        self.screens[name] = new_screen

        new_screen.on_create()

        return self

    def add_instantiated_screen(self, screen_obj: 'screen.BaseScreen') -> 'ScreenManager':
        self.screens[screen_obj.name] = screen_obj

        return self

    def change_screen(self, name: str) -> 'ScreenManager':
        if self.selected_screen is not None:
            previous_screen = self.selected_screen.name
            self.selected_screen.on_screen_leave(name)
        else:
            previous_screen = None

        self.selected_screen = self.screens[name]
        self.selected_screen.on_screen_enter(previous_screen)

        return self

    def show_screen(self, initial_screen: str = None) -> 'ScreenManager':
        if initial_screen is not None:
            self.change_screen(initial_screen)

        if self.showing_screen:
            return self

        pygame.display.set_caption(self.caption)

        if self.icon_path is not None:
            pygame.display.set_icon(pygame.image.load(self.icon_path))

        self.showing_screen = True

        mode = pygame.RESIZABLE
        w, h = self.screen_w, self.screen_h

        self.buffer = pygame.Surface((w, h))

        if self.fullscreen:
            mode = pygame.NOFRAME
            m = screeninfo.get_monitors()[self.monitor]  # type: screeninfo.Monitor
            w, h = m.width, m.height
            os.environ['SDL_VIDEO_WINDOW_POS'] = "{},{}".format(m.x, m.y)

        self.surface = pygame.display.set_mode((w, h), mode)

        self.update_scale_factor()

        pygame.mouse.set_visible(self.show_cursor)

        return self

    def update_scale_factor(self):
        self.scale_factor = min(
            [self.surface.get_width() / self.screen_w, self.surface.get_height() / self.screen_h]
        )
        self.buff_draw_x = self.surface.get_width() / 2 - (self.screen_w * self.scale_factor) / 2
        self.buff_draw_y = self.surface.get_height() / 2 - (self.screen_h * self.scale_factor) / 2

    def draw_buffer(self):
        if self.scale_factor == 1:
            buff = self.buffer
        else:
            buff = pygame.transform.scale(self.buffer, (
                int(self.screen_w * self.scale_factor),
                int(self.screen_h * self.scale_factor)
            ))

        self.surface.blit(buff, (self.buff_draw_x, self.buff_draw_y))
        pygame.display.update()

    @staticmethod
    def clear_event_queue():
        pygame.event.clear()

    def scale_coords(self, pos: typing.Tuple[float, float]) -> typing.Tuple[float, float]:
        return (pos[0] - self.buff_draw_x) / self.scale_factor, (pos[1] - self.buff_draw_y) / self.scale_factor

    def start(self, initial_screen: str = None) -> status_codes.StatusCodes:
        try:
            if not self.showing_screen:
                self.show_screen(initial_screen=initial_screen)

            clock = pygame.time.Clock()

            delta_t = 0

            while True:
                if self.selected_screen.is_showing_dialog_box():
                    send_events = self.selected_screen.dialog_boxes[0]
                else:
                    send_events = self.selected_screen

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return status_codes.StatusCodes.USER_QUIT

                    elif event.type == pygame.WINDOWRESIZED:
                        self.update_scale_factor()

                    elif event.type == pygame.KEYDOWN:
                        send_events.on_key_down(event.unicode, event.key, event.mod)

                    elif event.type == pygame.KEYUP:
                        send_events.on_key_up(event.key, event.mod)

                    elif event.type == pygame.MOUSEMOTION:
                        send_events.on_mouse_motion(
                            send_events.convert_coords(*self.scale_coords(event.pos)), event.rel, event.buttons
                        )

                    elif event.type == pygame.MOUSEBUTTONUP:
                        send_events.on_mouse_button_up(
                            send_events.convert_coords(*self.scale_coords(event.pos)), event.button
                        )

                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        send_events.on_mouse_button_down(
                            send_events.convert_coords(*self.scale_coords(event.pos)), event.button
                        )

                    elif event.type == pygame.JOYAXISMOTION:
                        send_events.on_joystick_axis_motion(event.joy, event.axis, event.value)

                    elif event.type == pygame.JOYBALLMOTION:
                        send_events.on_joystick_ball_motion(event.joy, event.ball, event.rel)

                    elif event.type == pygame.JOYHATMOTION:
                        send_events.on_joystick_hat_motion(event.joy, event.hat, event.value)

                    elif event.type == pygame.JOYBUTTONUP:
                        send_events.on_joystick_button_up(event.joy, event.button)

                    elif event.type == pygame.JOYBUTTONDOWN:
                        send_events.on_joystick_button_down(event.joy, event.button)

                send_events.handle_input(pygame.key.get_pressed(), pygame.mouse.get_pressed(5), delta_t)

                send_events.update(delta_t)

                self.selected_screen.render(self.buffer)

                for dlg in reversed(self.selected_screen.dialog_boxes):
                    dlg.render(self.buffer)

                self.draw_buffer()

                clock.tick(self.framerate_cap)
                self.fps = clock.get_fps()

                if self.fps != 0:
                    delta_t = 1 / self.fps

        except KeyboardInterrupt:
            return status_codes.StatusCodes.USER_QUIT
