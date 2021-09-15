import time
import typing

import pygame

import FangEngine.store as store

image_store = store.ImageAssetStore()
sound_store = store.SoundAssetStore()


class SpriteSheet:
    def __init__(
            self, image: str, tiles_wide: int, tiles_high: int, frames: int, speed: float = 0.1,
            scale_w: float = 1, scale_h: float = 1, color_key: typing.Tuple[int, int, int] = (255, 0, 255)
    ):
        if scale_h is None:
            scale_h = scale_w

        self.image_name = image
        self.image = image_store.get(image)            # type: pygame.Surface

        self.tiles_wide = tiles_wide
        self.tiles_high = tiles_high
        self.speed = speed
        self.scale_w = scale_w
        self.scale_h = scale_h
        self.frame_count = frames
        self.color_key = color_key

        self.frame = 0
        self.next_change = 0

        self.image = pygame.transform.scale(
            self.image, (
                int(self.image.get_width() * self.scale_w), int(self.image.get_height() * self.scale_h)
            )
        )

        self.tile_w = self.image.get_width() / self.tiles_wide
        self.tile_h = self.image.get_height() / self.tiles_high

    def render(self, buffer: pygame.Surface, x: float, y: float):
        buffer.blit(self.image, (x, y))

    def get_current_image(self) -> pygame.Surface:
        if time.time() >= self.next_change:
            self.next_change = time.time() + self.speed
            self.frame += 1
            if self.frame >= self.frame_count:
                self.frame = 0

        x = self.frame % self.tiles_wide
        y = self.frame // self.tiles_wide

        return self.image_at(x * self.tile_w, y * self.tile_h, self.tile_w, self.tile_h)

    def image_at(self, x: float, y: float, w: float, h: float, color_key=None) -> pygame.Surface:
        if color_key is None:
            color_key = self.color_key

        rect = pygame.Rect((x, y, w, h))
        image = pygame.Surface(rect.size).convert()
        image.fill(color_key)
        image.blit(self.image, (0, 0), rect)
        image.set_colorkey(color_key, pygame.RLEACCEL)

        return image
