import math
import typing
from abc import ABC

import FangEngine.converter.angle as angle_converter
import FangEngine.game_object.premade.rotatable_object as rotatable_object
import FangEngine.game_object.premade.rotatable_sprite_sheet as rotatable_sprite_sheet
import FangEngine.screen_manager.object_screen as object_screen
import FangEngine.store.asset_store.image_asset_store as image_asset_store
import FangEngine.store.asset_store.sound_asset_store as sound_asset_store

FULL_ROTATION = 2 * math.pi


class RotatableScreenBase(object_screen.ObjectScreen, ABC):
    IMAGE_STORE = image_asset_store.ImageAssetStore()
    SOUND_STORE = sound_asset_store.SoundAssetStore()

    def __init__(self, name: str, manager):
        super().__init__(name, manager)
        self.fov = angle_converter.degrees(90)
        self.angle = 0
        self.PIXELS_PER_METER = self.screen_w / 2

        self.center_x = self.screen_w / 2

    def spawn_rotatable_object(
            self, object_class_ref: 'rotatable_object.RotatableObject.__class__',
            angle: float, distance: float, y: float = 0, scale_x: float = 1, scale_y: float = None, *args, **kwargs
    ):
        return self.spawn_object(object_class_ref, 0, y, angle, distance, scale_x=scale_x, scale_y=scale_y, *args, **kwargs)

    def spawn_rotatable_image(
            self, image: str, angle: float, distance: float, y: float = 0,
            scale_x: float = 1, scale_y: float = None, *args, **kwargs
    ):
        return self.spawn_object(
            rotatable_object.RotatableObject, angle, y, angle, distance, image=image,
            scale_x=scale_x, scale_y=scale_y, *args, **kwargs
        )

    def spawn_rotatable_sprite_sheet(
            self, image: str, angle: float, distance: float, tiles_wide: int, tiles_high: int, frames: int,
            speed: float = 0.1, scale_w: float = 1, scale_h: float = None,
            color_key: typing.Tuple[int, int, int] = (255, 0, 255), y: float = 0, *args, **kwargs
    ):
        return self.spawn_object(
            rotatable_sprite_sheet.RotatableSpriteSheet, 0, y, angle, distance, frames=frames,
            image=image, tiles_wide=tiles_wide, tiles_high=tiles_high, speed=speed, scale_w=scale_w, scale_h=scale_h,
            color_key=color_key, *args, **kwargs
        )
