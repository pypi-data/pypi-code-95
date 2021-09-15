import tkinter as tk
from .color import Color

class TimePlot(tk.Canvas):
    def __init__(self, *args, width=128, height=64, min=0, max=100, label=None, **kwargs):
        tk.Canvas.__init__(self, *args, width=width, height=height, **kwargs)
        self.width, self.height = width, height
        if min == max: min -= 1

        self.values = [i for i in range(width)]
        self.min, self.max = min, max

        self.fg_color = Color.from_hex(self.option_get('foreground','Foreground'))
        self.bg_color = Color.from_hex(self.option_get('background','Background'))

        if label:
            self.create_text(width//2,0, anchor=tk.N,
            fill=self.bg_color.lighter().as_hex(), text=label)

        self.textmax = self.create_text(0, 0, anchor=tk.NW,
            fill=self.bg_color.lighter(0.66).as_hex(), text=f'{self.max}')
        self.textmin = self.create_text(0, self.height, anchor=tk.SW,
            fill=self.bg_color.lighter(0.66).as_hex(), text=f'{self.min}')
        self.draw()

    def draw(self):
        self.delete('line')
        xs = [w for w in range(self.width)]
        ys = [(self.height-1) - (self.height-1)*max(min((v-self.min)/(self.max-self.min),1),0) for v in self.values]

        pts = [(x,y) for x,y in zip(xs,ys)]
        line = self.create_line(*pts, fill=self.fg_color.as_hex(), tags='line')
        self.tag_lower(line, 'all')

        self.itemconfig(self.textmax, text=f'{self.max:.0f}')
        self.itemconfig(self.textmin, text=f'{self.min:.0f}')

    def set(self, v):
        self.values.append(v)
        if len(self.values) > self.width: self.values.pop(0)
        self.draw()

    def set_min(self, m):
        self.min = m
        if self.max == self.min: self.min -=1
        self.draw()

    def set_max(self, m):
        self.max = m
        if self.max == self.min: self.max +=1
        self.draw()
