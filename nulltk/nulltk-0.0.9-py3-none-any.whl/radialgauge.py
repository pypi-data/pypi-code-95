import tkinter as tk
from .abstract.gauge import Gauge
from .color import Color
from PIL.ImageTk import PhotoImage
from PIL import Image, ImageFont, ImageDraw

# styled after
# https://github.com/israel-dryer/ttkbootstrap/issues/34#issuecomment-830833271
class RadialGauge(tk.Label, Gauge):
    def __init__(self, master, *args, arcrange=270, arcoffset=-225, **kwargs):
        tk.Label.__init__(self, master)
        Gauge.__init__(self, *args, **kwargs)

        self.base_image = None
        self.towardsmaximum = True
        self.arcrange = arcrange
        self.arcoffset = arcoffset

        self.meterforeground = Color.from_hex(self.option_get('foreground', 'Foreground'))
        self.meterbackground = Color.from_hex(self.option_get('background', 'Background')).darker(0.25)

        self.stripethickness = 2 if self.stripethickness == 1 else self.stripethickness

        self._draw_base()

    def meter_value(self):
        return int((self.amountused / self.amounttotal) * self.arcrange + self.arcoffset)

    def _draw_base(self):
        self.base_image = Image.new('RGBA', (self.metersize*self.drawresolution, self.metersize*self.drawresolution))
        draw = ImageDraw.Draw(self.base_image)

        # striped
        if self.stripethickness > 0:
            for theta in range(self.arcoffset, self.arcrange + self.arcoffset, self.stripethickness):
                draw.arc((20, 20, self.metersize*self.drawresolution - 20, self.metersize*self.drawresolution - 20),
                        theta, theta + self.stripethickness - 1, self.meterbackground.as_hex(), self.meterthickness*self.drawresolution)
        # solid
        else:
            draw.arc((20, 20, self.metersize*self.drawresolution - 20, self.metersize*self.drawresolution - 20),
                    self.arcoffset, self.arcrange + self.arcoffset, self.meterbackground.as_hex(), self.meterthickness*self.drawresolution)

    def draw_meter(self, *args):
        im = self.base_image.copy()
        draw = ImageDraw.Draw(im)

        if self.stripethickness > 0:
            self._draw_meter_striped(draw)
        else:
            self._draw_meter_solid(draw)
        
        draw.text((self.metersize*self.drawresolution*0.55, self.metersize*self.drawresolution*0.5),
                  f"{self.amountused}", anchor='rs', font=self.valuefont, fill=self.meterforeground.as_hex())
        draw.text((self.metersize*self.drawresolution*0.55, self.metersize*self.drawresolution*0.5),
                  f"{self.unitstext}", anchor='ls', font=self.unitsfont, fill=self.meterforeground.darker(0.25).as_hex())
        draw.text((self.metersize*self.drawresolution*0.5, self.metersize*self.drawresolution*0.5),
                  f"{self.labeltext}", anchor='ma', font=self.labelfont, fill=self.meterforeground.darker(0.25).as_hex())

        self.meterimage = PhotoImage(im.resize((self.metersize, self.metersize), Image.CUBIC))
        self.configure(image=self.meterimage)

    def _draw_meter_solid(self, draw):
        meter_value = self.meter_value()
        if self.wedgesize > 0:
            draw.arc((20, 20, self.metersize*self.drawresolution - 20, self.metersize*self.drawresolution - 20),
                     meter_value - self.wedgesize, meter_value + self.wedgesize,
                     self.meterforeground.as_hex(), self.meterthickness*self.drawresolution)
        else:
            draw.arc((20, 20, self.metersize*self.drawresolution - 20, self.metersize*self.drawresolution - 20),
                    self.arcoffset, self.meter_value(), self.meterforeground.as_hex(), self.meterthickness*self.drawresolution)
    
    def _draw_meter_striped(self, draw):
        meter_value = self.meter_value()
        if self.wedgesize > 0:
            draw.arc((20, 20, self.metersize*self.drawresolution - 20, self.metersize*self.drawresolution - 20),
                     meter_value - self.wedgesize, meter_value + self.wedgesize,
                     self.meterforeground.as_hex(), self.meterthickness*self.drawresolution)
        else:
            for theta in range(self.arcoffset, self.meter_value() - 1, self.stripethickness):
                draw.arc((20, 20, self.metersize*self.drawresolution - 20, self.metersize*self.drawresolution - 20),
                         theta, theta + self.stripethickness - 1, self.meterforeground.as_hex(), self.meterthickness*self.drawresolution)
