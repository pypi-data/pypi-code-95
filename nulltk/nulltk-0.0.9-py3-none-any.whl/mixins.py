import tkinter as tk

def Reactive(obj):
    activebg = obj.option_get('activeBackground', '')
    activefg = obj.option_get('activeForeground', '')
    obj._reactive_prevBG = obj['background']
    try: obj._reactive_prevFG = obj['foreground']
    except tk.TclError: pass

    def on_enter(e):
        obj._reactive_prevBG = obj['background']
        obj['background'] = activebg
        if hasattr(obj,'prevFG'):
            obj._reactive_prevFG = obj['foreground']
            obj['foreground'] = activefg

    def on_leave(e):
        obj['background'] = obj._reactive_prevBG
        if hasattr(obj,'prevFG'):
            obj['foreground'] = obj._reactive_prevFG

    obj.bind("<Enter>", on_enter)
    obj.bind("<Leave>", on_leave)

    return obj
