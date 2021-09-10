class Library:
    def __init__(self):
        self.name = ""

    def load_script(self):
        return self.js

    def load_link(self):
        return self.css

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    def __add__(self, other):
        return other+self.__str__()

    def __radd__(self, other):
        return other+self.__str__()

    @staticmethod
    def listall(w):
        if w == "css":
            return ("mdb", "mdb5", "bootstrap", "bootstrap5")
        elif w == "js":
            return ("mdb","mdb5","bootstrap","bootstrap5","umbrella","jquery","popper")
        elif w == "fonts":
            return ("FontAwesome","roboto")

from .MDB5 import *
from .MDB import *
from .Bootstrap import *

from .Umbrella import *
from .JQuery import *
from .Popper import *

from .Fonts import *