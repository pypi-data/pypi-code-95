class BotInfo:
    __slots__ = ('_name', '_data',)

    def __init__(self, name: str = '', **kwargs):
        self._name = name
        self._data = kwargs

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value
