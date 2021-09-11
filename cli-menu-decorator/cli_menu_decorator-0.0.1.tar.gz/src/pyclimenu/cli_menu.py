from collections import ChainMap

from src.pyclimenu.menu import Menu
from src.pyclimenu.menu_item import MenuItem


class CliMenu:
    def __init__(self):
        self.home_option = Menu()
        self.home_option.add(self.home)
        self.home_option.add(self.back)
        self.home_option.add(self.exit)

        self.options = Menu()
        self._isActive = False
        self._available_options = ChainMap(self.home_option.get_dict())

    def start(self):
        self._isActive = True
        self._available_options = self._available_options.new_child(self.options.get_dict())

    def is_active(self):
        return self._isActive

    def is_home(self):
        return len(self._available_options.maps) <= 2

    def show_available_options(self):
        for o in self._available_options.keys():
            self._available_options[o].show()

    def select(self, selected_option):
        selected = self._available_options.get(selected_option)
        if selected:
            return selected.action(self)
        else:
            raise KeyError(f"Selected option {selected_option} not found")

    def add_sub_menu(self, sub_menu: Menu):
        self._available_options = self._available_options.new_child(sub_menu.get_dict())

    @MenuItem('h', 'Home')
    def home(self):
        self._available_options.maps.clear()
        self._available_options = self._available_options.new_child(self.home_option.get_dict())
        self._available_options = self._available_options.new_child(self.options.get_dict())
        return 'Home'

    @MenuItem('b', 'Back')
    def back(self):
        if not self.is_home():
            self._available_options = self._available_options.parents
            return 'Back'
        else:
            return self.select('h')

    @MenuItem('x', 'Exit')
    def exit(self):
        if input("Are you sure you want to exit?") in ['Y', 'y', 'yes', 'Yes']:
            self._isActive = False
            return 'OK. Bye!'
        else:
            return 'No problem. carry on .. '
