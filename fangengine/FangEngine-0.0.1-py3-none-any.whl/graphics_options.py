import tkinter as tk
from tkinter import N, E, S, W
from screeninfo import get_monitors, Monitor
import tkinter.font as font
import json
import os
import sys

if not os.path.isdir("cache"):
    os.makedirs("cache")

SETTINGS_CACHE = "cache/graphics.json"


def get_options(game_title: str, icon_path: str = None):
    """
    Displays the GUI window for getting the graphics options from the user.
    NOTE: Do not call this method directly! Call the get_graphics_options method of the PyGE class
    :param game_title: the window caption
    :param icon_path: the path to the window icon
    :return: a dictionary of the specified graphics options
    """
    if os.path.isfile(SETTINGS_CACHE):
        with open(SETTINGS_CACHE) as f:
            defaults = json.loads(f.read())
    else:
        defaults = {
            "monitor": 0,
            "fullscreen": 1,
            "framerate": 60
        }

    def generate_options():
        window.destroy()

    def kill_app():
        sys.exit()

    monitors = {}
    default = None
    first = None
    for i, m in enumerate(get_monitors()):        # type: Monitor
        if i == defaults["monitor"]:
            default = "Monitor {} ({}x{})".format(i, m.width, m.height)
        if i == 0:
            first = "Monitor {} ({}x{})".format(i, m.width, m.height)
        monitors["Monitor {} ({}x{})".format(i, m.width, m.height)] = i

    if default is None:
        default = first

    framerates = {"Framerate Cap " + str(i) + "fps": i for i in [120, 60, 50, 30, 24]}

    window = tk.Tk()

    window_height = 200
    window_width = 400

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x_cordinate = int((screen_width / 2) - (window_width / 2))
    y_cordinate = int((screen_height / 2) - (window_height / 2))

    window.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))

    window.protocol("WM_DELETE_WINDOW", kill_app)

    window.title(game_title)
    if icon_path is not None:
        window.tk.call('wm', 'iconphoto', window._w, tk.PhotoImage(file=icon_path))

    monitor = tk.StringVar()
    monitor.set(default)

    framerate = tk.StringVar()
    framerate.set("Framerate Cap {}fps".format(defaults["framerate"]))

    fullscreen = tk.IntVar()
    fullscreen.set(defaults["fullscreen"])

    my_font = tk.font.Font(size=15)

    pad_y = (5, 0)
    pad_x = 10

    greeting = tk.Label(text=game_title, font=my_font)
    greeting.grid(row=1, column=1, sticky=N+E+S+W, padx=pad_x, pady=(10, 0))

    tk.OptionMenu(window, monitor, *monitors).grid(row=2, column=1, sticky=N+E+S+W, padx=pad_x, pady=pad_y)
    tk.Checkbutton(window, text="Fullscreen", variable=fullscreen, onvalue=1, offvalue=0).grid(row=3, column=1, sticky=N+E+S+W, padx=pad_x, pady=pad_y)
    tk.OptionMenu(window, framerate, *framerates).grid(row=4, column=1, sticky=N+E+S+W, padx=pad_x, pady=pad_y)
    tk.Button(window, text="Launch Game", command=generate_options).grid(row=5, column=1, sticky=N+E+S+W, padx=pad_x, pady=pad_y)

    window.resizable(False, False)
    window.grid_columnconfigure(1, weight=1)

    window.mainloop()

    options = {
        "monitor": monitors[monitor.get()],
        "fullscreen": bool(fullscreen.get()),
        "framerate": framerates[framerate.get()]
    }

    with open(SETTINGS_CACHE, 'w') as f:
        f.write(json.dumps(options))

    return options
