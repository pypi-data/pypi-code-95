import abc
import typing

import pygame
import time

import FangEngine.game_object.game_object as game_object
import FangEngine.store.asset_store.image_asset_store as image_asset_store

cs = image_asset_store.ImageAssetStore()

pygame.font.init()


class HUDBase(game_object.GameObject, abc.ABC):
    def __init__(
            self, screen_parent, x: float, y: float, w: float, h: float, font=pygame.font.Font,
            background_color: tuple = (255, 255, 255), left_padding: int = 5, middle_padding: int = 10
    ):
        super().__init__(screen_parent, x, y)

        self.w = w
        self.h = h
        self.font = font
        self.background_color = background_color
        self.left_padding = left_padding
        self.middle_padding = middle_padding

        self.draw_y = self.y + ((self.h - self.font.get_height()) / 2)

        self.text = {}          # type: typing.Dict[str, pygame.Surface]

    def add_text(self, text: str, color=(0, 0, 0), ref_name: str = None):
        if ref_name is None:
            ref_name = time.time_ns()

        self.text[ref_name] = self.font.render(text, True, color)

    def add_surface(self, surf: pygame.Surface, ref_name: str = None):
        if ref_name is None:
            ref_name = time.time_ns()

        surf = pygame.transform.scale(surf, (int(surf.get_width() * (self.font.get_height() / surf.get_height() )), self.font.get_height()))
        self.text[ref_name] = surf

    def add_image(self, name: str, ref_name: str = None):
        if ref_name is None:
            ref_name = time.time_ns()

        self.add_surface(cs.get(name), ref_name=ref_name)

    def render(self, buffer: pygame.Surface):
        super(HUDBase, self).render(buffer)
        pygame.draw.rect(buffer, self.background_color, (self.x, self.y, self.w, self.h))

        x = self.left_padding
        for text in self.text.values():
            buffer.blit(text, (x, self.draw_y))
            x += text.get_width() + self.middle_padding

    def on_click(self, pos: tuple, button: int):
        cx, cy = pos

        x = self.left_padding
        for name, surf in self.text.items():
            if x <= cx <= x + surf.get_width() and self.draw_y <= cy <= self.draw_y + surf.get_height():
                self.on_hud_item_click(str(name))

            x += surf.get_width() + self.middle_padding

    def on_hud_item_click(self, ref_name: str):
        pass

    def remove_item(self, ref_name: str) -> pygame.Surface:
        return self.text.pop(ref_name)
