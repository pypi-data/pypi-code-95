from .base_package import Package, find_packages, find_root
from .model import model, start_load


async def init():
    start_load()

__all__ = (
    'Package',
    'find_packages',
    'find_root',
    'init',
    'model',
)
