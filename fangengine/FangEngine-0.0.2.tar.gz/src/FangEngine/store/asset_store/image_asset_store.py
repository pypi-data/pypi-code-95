import os

import pygame
import logging

import FangEngine.store.asset_store.asset_store as asset_store


class ImageAssetStore(asset_store.AssetStore):
    """
    Supported Formats:
    PNG, JPG, GIF, BMP
    """
    asset_path = os.path.join("assets", "images")

    def load_asset(self, path: str):
        try:
            return pygame.image.load(path)
        except pygame.error as e:
            logging.error("Failed to load asset '{}'. {}".format(path, e))
