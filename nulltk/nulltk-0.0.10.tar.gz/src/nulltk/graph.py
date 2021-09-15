import tkinter as tk
import os

class Graph(tk.Canvas):
    """ tk Canvas with extra methods for dragging, zooming, etc... """
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.origin_rect = self.create_rectangle(0,0,0,0)
        self.zoom = 1
        self.xoff, self.yoff = 0, 0
        def scroll_start(event):
            self.scan_mark(event.x, event.y)

        def scroll_move(event):
            self.scan_dragto(event.x, event.y, gain=1)

        def zoom(event):
            x = self.canvasx(event.x)
            y = self.canvasy(event.y)
            delta = 0
            if os.name == 'nt': # windows
                delta = event.delta
            else: # linux
                if event.num == 5: delta = -120
                elif event.num == 4: delta = 120
                else: raise Exception("Bad event number")
            factor = 1.001 ** delta
            self.zoom *= 1/factor
            self.scale(tk.ALL, x, y, factor, factor)

        # middle-click drag
        self.bind("<ButtonPress-2>", scroll_start)
        self.bind("<B2-Motion>", scroll_move)
        
        # scrollwheel zoom
        if os.name == 'nt': # windows
            self.bind("<MouseWheel>", zoom)
        else: # linux
            self.bind("<Button-4>", zoom)
            self.bind("<Button-5>", zoom)

    def origin(self):
        coords = self.coords(self.origin_rect)
        return coords[0], coords[1]

    def window_to_canvas(self, x, y):
        return self.canvasx(x), self.canvasy(y)

    def window_to_world(self, x, y):
        cx, cy = self.window_to_canvas(x, y)
        return self.canvas_to_world(cx, cy)

    def canvas_to_world(self, cx, cy):
        ox, oy = self.origin()
        return (cx-ox)*self.zoom, (cy-oy)*self.zoom

    def world_to_canvas(self, x, y):
        ox, oy = self.origin()
        return ox + (x/self.zoom), oy + (y/self.zoom)

    def plotpoint(self, x, y, text=True):
        cx, cy = self.world_to_canvas(x, y)
        size = 0.5/self.zoom
        self.create_rectangle(
            cx-size, cy-size, cx+size, cy+size,
            fill='lightgreen',
            outline='',
            tag='pt' )
        if text: self.create_text( cx, cy,
                                   fill='green',
                                   tag='pt text',
                                   text=f"({int(x)},{int(y)})",
                                   anchor=tk.SW )
