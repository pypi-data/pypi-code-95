from typing import Generator

from palett.flopper import palett_flopper
from palett.structs import Preset

from pyspare.deco.deco_str import deco_str
from .pal import Pal


class Says:
    __flopper: Generator
    __effects: tuple
    __roster: dict = {}

    def __init__(self, *effects):
        self.__flopper = palett_flopper(to=Preset.rand)
        self.__effects = effects

    def __call__(self, name, preset=None):
        if name in self.__roster: return self.__roster[name]
        preset = preset or next(self.__flopper)
        dyed_name = deco_str(name, presets=(preset, preset), effects=self.__effects)
        pal = Pal(dyed_name)
        self.__roster[name] = pal
        return pal

    def __getitem__(self, name):
        return self.__call__(name)

    def __getattr__(self, name):
        return self.__call__(name)

    def roster(self, name=None):
        if name: return self.__call__(name).name
        return {name: pal.name for name, pal in self.__roster.items()}
