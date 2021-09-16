import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt

import numpy as np 

class Plot(tk.Frame):
    """Custom tkinter widget for using matplotlib with the interface"""

    def __init__(self, master, subplot_rows, subplot_cols, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.fig, self.axes = plt.subplots(subplot_rows, subplot_cols, figsize=(6,4))

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)    
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(expand=True, fill='both', side = "top")

    def clear(self):
        """Clear all axes"""
        if isinstance(self.axes, np.ndarray):
            for ax in self.axes:
                ax.clear()
        else:      
            self.axes.clear()

    def draw(self):
        """Show plot"""
        self.canvas.draw()
    