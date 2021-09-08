import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import inspect
import os
from datetime import datetime

def subplots(nrows=2, ncols=2, size_inches=(10,12), *args):
    fig,axx = plt.subplots(nrows, ncols, *args)
    fig.set_size_inches(size_inches[0], size_inches[1])
    if not isinstance(axx, list):
        axx = np.asarray(axx, dtype=np.object).reshape((nrows, ncols))
    return fig, axx

def get_colors(palette="dark",max_colors=5):
    return sns.color_palette(palette, max_colors)


def watermark_plot(extra="", nback=2, fz_y=10):
    # from slider.thtools_base import watermark_string
    s = watermark_string(nback=nback)
    plt.figtext(0.05, 0.95, s)



def watermark_string(nback=2):


    tm =  datetime.now().strftime('%b-%d-%I:%M%p')
    # for line in traceback.format_stack():
    #     #     print(line.strip())
    v = inspect.stack()
    ss = []
    j = 0
    for i in range(len(v)):
        if "plot_helpers.py" in v[i].filename: continue
        ss.append( os.path.basename( v[i].filename) )
        j = j + 1
        if j > nback: break
    # from thtools import execute_command
    from jinjafy import execute_command
    v, _ = execute_command("git rev-parse --short HEAD".split())

    ss.append(tm)
    return ('/'.join(ss) + f" @{v}").strip()



