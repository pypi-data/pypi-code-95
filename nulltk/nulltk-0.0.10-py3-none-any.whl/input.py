import tkinter as tk
import math
from .color import Color

class Slider(tk.Canvas):
    def __init__(self, *args, width=16, height=128, min=0, max=100, value=None, step=1, arc_width=None, **kwargs):
        tk.Canvas.__init__(self, *args, width=width, height=height, **kwargs)
        self.fg_color = Color.from_hex(self.option_get('foreground','Foreground'))
        self.bg_color = Color.from_hex(self.option_get('background','Background'))
        self.width, self.height = width, height
        self.step    = step
        self.min    = min
        self.max    = max
        self.value    = value

        self.create_rectangle(0,0,self.width,self.height,
            outline='',
            fill=self.fg_color.as_hex()
        )

class Dial(tk.Canvas):
    def __init__(self, *args, size=48, min=0, max=100, value=None, step=1, arc_width=None, **kwargs):
        tk.Canvas.__init__(self, *args, width=size, height=size, **kwargs)
        self.height, self.width, self.size = size, size, size

        self.bind("<MouseWheel>",        self.on_mousewheel)
        self.bind("<Button-4>",            self.on_mousewheel)
        self.bind("<Button-5>",            self.on_mousewheel)
        self.bind("<ButtonPress-1>",    self.on_dragstart)
        self.bind("<B1-Motion>",        self.on_drag)

        self.fg_color = Color.from_hex(self.option_get('foreground','Foreground'))
        self.bg_color = Color.from_hex(self.option_get('background','Background'))

        if arc_width == None: arc_width = size//10
        if value == None: value = min

        self.step    = step
        self.min    = min
        self.max    = max
        self.value    = value

        self.create_oval(0, 0, size, size, fill=self.bg_color.darker().as_hex())
        self.create_oval(
            arc_width, arc_width,
            size-arc_width, size-arc_width,
            fill = self.bg_color.as_hex()
        )
        self.subarc_id = self.create_arc(*(arc_width//2, arc_width//2), *(size-arc_width//2, size-arc_width//2),
            outline = self.fg_color.darker().as_hex(),
            style    = tk.ARC,
            width    = arc_width
        )
        self.arc_id = self.create_arc(*(arc_width//2, arc_width//2), *(size-arc_width//2, size-arc_width//2),
            outline = self.fg_color.as_hex(),
            style    = tk.ARC,
            width    = arc_width
        )
        self.text_id = self.create_text(*(size//2, size//2),
            anchor    = tk.CENTER,
            justify = tk.CENTER,
            fill    = self.fg_color.as_hex()
        )

        self.listeners = []
        self.draw()
        #self.after(20, self.think)

    def think(self):
        self.draw()
        self.after(20, self.think)

    def set_min(self, min):
        self.min = min
        if self.min == self.max: self.min -= 1
        self.set_value(self.value)
        self.draw()

    def set_max(self, max):
        self.max = max
        if self.min == self.max: self.max += 1
        self.set_value(self.value)
        self.draw()

    def set_value(self, value):
        if value > self.max: value = self.max
        if value < self.min: value = self.min
        self.value = value
        self.draw()

    def on_dragstart(self, event):
        self.lastx, self.lasty = event.x, event.y
        self.draw()

    def on_drag(self, event):
        x, y = event.x, event.y
        dx, dy = x - self.lastx, y - self.lasty
        cx, cy = self.width/2, self.height/2
        if x-cx > 0: dy*=-1
        if y-cy < 0: dx*=-1
        self.lastx, self.lasty = x, y
        self.value += -((dy+dx)/math.dist((0,0),(dx,dy)))*(self.max-self.min)/360
        self.draw()

    def on_mousewheel(self, event):
        if event.delta == 0:
            if event.num == 4: event.delta = 120
            elif event.num == 5: event.delta = -120

        self.value += math.copysign(self.step, event.delta)
        self.value = max(min(self.value, self.max), self.min)
        self.draw()

    def draw(self):
        self.value = max(min(self.value, self.max), self.min)
        self.itemconfig(self.arc_id,
            extent=6,
            start=267-min(360*(self.value - self.min)/(self.max - self.min),359)
        )
        self.itemconfig(self.subarc_id,
            extent=max(-360*(self.value - self.min)/(self.max - self.min),-359),
            start=267
        )
        self.itemconfig(self.text_id, text = f'{self.value:.0f}')

        for listener in self.listeners: listener(self.value)

    def register_callback(self, cb: callable):
        self.listeners.append(cb)
