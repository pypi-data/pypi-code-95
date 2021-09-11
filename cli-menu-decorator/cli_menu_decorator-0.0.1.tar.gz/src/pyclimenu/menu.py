from collections import OrderedDict


class Menu:
    def __init__(self):
        self._menu = OrderedDict()

    def __getitem__(self, item):
        return self._menu[item]

    def add(self, other):
        self._menu[other.option] = other

    def show(self):
        for i in self._menu.keys():
            print(self._menu[i])
        return self._menu

    def get_dict(self):
        return self._menu
