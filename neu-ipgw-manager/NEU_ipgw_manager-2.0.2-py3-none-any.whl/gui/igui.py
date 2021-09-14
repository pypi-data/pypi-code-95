import os
import tkinter as tk
import tkinter.ttk as ttk
from tabulate import tabulate

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
PROJECT_UI = os.path.join(PROJECT_PATH, "design.ui")


class DesignApp:
    def __init__(self, master=None):
        # build ui
        self.root = tk.Tk() if master is None else tk.Toplevel(master)
        s = ['这是一个', '另一个', '好东西！', '序号a']
        b = [['abc', '123什么', '科学13a4444', 'ddd'], ['abc', '123什么', '科', '123']]
        l = ttk.Label(text=tabulate(b, headers=s), font='{Microsoft YaHei} 12 {}')
        l.pack()
        # Main widget
        self.mainwindow = self.root

    def run(self):
        self.mainwindow.mainloop()


if __name__ == '__main__':
    app = DesignApp()
    app.run()
