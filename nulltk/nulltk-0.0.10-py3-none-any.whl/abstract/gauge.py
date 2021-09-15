from PIL import ImageFont
import tkinter as tk
from ..util import font

# determine if we can use 'arialbd' as a default font:
DEFAULT_FONTS = [
    'arialbd.ttf',
    'DroidSansMono.ttf',
]
DEFAULT_FONTS.extend(font.find_system_fonts())
for font in DEFAULT_FONTS:
    default_font = font
    try:
        ImageFont.truetype(default_font, 14)
        break
    except OSError: continue

class Gauge:
    drawresolution = 3
    def __init__(self,
        amountused: float = 0,
        amounttotal: float = 100,
        showvalue: bool = True,
        valuefont: ImageFont = ImageFont.truetype(default_font, 40 * drawresolution),
        unitsfont: ImageFont = ImageFont.truetype(default_font, 15 * drawresolution),
        labelfont: ImageFont = ImageFont.truetype(default_font, 20 * drawresolution),
        unitstext: str = '',
        labeltext: str = '',
        metersize: int = 200,
        wedgesize: int = 0,
        meterthickness: int = 10,
        stripethickness: int = 0):

        self.amountusedvariable = tk.IntVar(value = amountused)
        self.amounttotalvariable = tk.IntVar(value = amounttotal)

        self.amountusedvariable.trace_add('write', self.draw_meter)

        self.showvalue = showvalue
        self.metersize = metersize
        self.meterthickness = meterthickness
        self.stripethickness = stripethickness
        self.unitsfont = unitsfont
        self.labelfont = labelfont
        self.valuefont = valuefont
        self.unitstext = unitstext
        self.labeltext = labeltext
        self.wedgesize = wedgesize

    def draw_meter(self, *args):
        raise Exception("Not yet implemented.")

    @property
    def amountused(self):
        return self.amountusedvariable.get()

    @amountused.setter
    def amountused(self, value):
        self.amountusedvariable.set(value)

    @property
    def amounttotal(self):
        return self.amounttotalvariable.get()

    @amounttotal.setter
    def amounttotal(self, value):
        self.amounttotalvariable.set(value)

    def step(self, delta=1):
        if self.amountused >= self.amounttotal:
            self.towardsmaximum = True
            self.amountused = self.amounttotal - delta
        elif self.amountused <= 0:
            self.towardsmaximum = False
            self.amountused = self.amountused + delta
        elif self.towardsmaximum:
            self.amountused = self.amountused - delta
        else:
            self.amountused = self.amountused + delta
