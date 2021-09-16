import tkinter as tk
import tkinter.ttk as ttk

class BoundedEntry(tk.Frame):
    """Custom tkinter widget for entering a bounded value with validation"""
    
    def __init__(self, master, external_var, lower_bound_var, upper_bound_var, reset_behaviour,*args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.reset_behaviour = reset_behaviour
        self.callbacks = []
        self.external_var = external_var
        self.lower_bound_var = lower_bound_var
        self.upper_bound_var = upper_bound_var
        self.internal_var = tk.StringVar(self, external_var.get())

        self.entry = ttk.Entry(self, textvariable=self.internal_var, width=7)
        self.entry.bind("<Tab>", self.internal_var_change, add="+")
        self.entry.bind("<Return>", self.internal_var_change, add="+")
        self.entry.bind("<FocusOut>", self.internal_var_change, add="+")
        self.place_elements()

    def set(self, value):
        self.internal_var.set(value)

    def place_elements(self):
        """Geometry management"""
        self.entry.grid(row=0, column=0)

    def internal_var_change(self, *args):
        """Tries converting to float and validating value, else resets"""
        try:
            value = float(self.internal_var.get())
            assert self.validate(value)
            self.external_var.set(value)
            for callback in self.callbacks:
                callback()
        except:
            if self.reset_behaviour == "up":
                self.internal_var.set(self.upper_bound_var.get())
            elif self.reset_behaviour == "down":
                self.internal_var.set(self.lower_bound_var.get())
            elif self.reset_behaviour == "reset":
                self.internal_var.set(self.external_var.get())

    def validate(self, value):
        """Check bounds"""
        return self.lower_bound_var.get() <= value <= self.upper_bound_var.get()

    def trace(self, callback):
        self.callbacks.append(callback)