import os

import pygame

import FangEngine.store.asset_store.asset_store as asset_store

pygame.mixer.init()


class SoundAssetStore(asset_store.AssetStore):
    """
    Supported formats:
    OGG, MP3, XM, MOD

    NOTE: OGG is preferred
    """
    asset_path = os.path.join("assets", "sounds")

    def load_asset(self, path: str):
        return pygame.mixer.Sound(path)
