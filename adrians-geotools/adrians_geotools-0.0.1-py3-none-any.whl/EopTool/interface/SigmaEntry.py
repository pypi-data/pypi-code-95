import tkinter as tk 
import tkinter.ttk as ttk

class SigmaEntry(tk.Frame):
    """Custom tkinter widget for entering a sigma value through a slider or through text, as a percentage or absolute"""
    
    def __init__(self, master, external_var, bound_var, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        
        self.master = master 
        self.external_var = external_var
        self.bound_var = bound_var
        self.callbacks = []

        self.internal_var = tk.StringVar(self, value = external_var.get())
        self.input_type = tk.StringVar(self, value = "%")
        self.input_type.trace("w", self.input_type_change)

        self.scale = tk.Scale(self, variable=self.internal_var, from_ = 0, to = 100, orient = "horizontal", showvalue=False, resolution = 0.001)
        self.scale.bind("<ButtonRelease-1>", self.internal_var_change)

        self.entry = ttk.Entry(self, textvariable=self.internal_var, width=7)
        self.entry.bind("<Tab>", self.internal_var_change, add="+")
        self.entry.bind("<Return>", self.internal_var_change, add="+")
        self.entry.bind("<FocusOut>", self.internal_var_change, add="+")

        self.input_type_combo = ttk.Combobox(self, textvariable=self.input_type, values=["%", "µσ"], width=3)
        self.place_elements()

    def place_elements(self):
        """Geometry mangement"""
        self.scale.grid(row=0, column=0)
        self.entry.grid(row=0, column=1)
        self.input_type_combo.grid(row=0, column=2, padx=2)

    def set(self, sigma_value):
        if self.input_type.get() == "%":
            percent_value = self.master.master.microsigma_to_percent(sigma_value*10**6)
            self.internal_var.set(percent_value) 
        
        elif self.input_type.get() == "µσ":
            sigma_value = sigma_value * 10**6
            self.internal_var.set(str(sigma_value))

    def internal_var_change(self, *args):
        """Convert value to sigma if needed, validate, and set external value. Revert to external value if not valid"""
        try:
            value = float(self.internal_var.get())
            if self.input_type.get() == "%":
                value = self.master.master.percent_to_microsigma(value)

            assert self.validate(value)
            self.external_var.set(value*10**-6)
            for callback in self.callbacks:
                callback()
        except:
            self.internal_var.set(str(self.external_var.get()*10**6))            

    def input_type_change(self, *args):
        """Change scale limits, resolution and internal value"""
        if self.input_type.get() == "%":
            sigma_value = float(self.internal_var.get())
            percent_value = self.master.master.microsigma_to_percent(sigma_value)
            self.scale.configure(to=100, resolution=0.001)
            self.internal_var.set(str(percent_value)) 
        
        elif self.input_type.get() == "µσ":
            percent_value = float(self.internal_var.get())
            sigma_value = self.master.master.percent_to_microsigma(percent_value)
            self.scale.configure(to=self.bound_var.get()*10**6, resolution=0.001)
            self.internal_var.set(str(sigma_value))      

    def validate(self, value):
        return 0 <= value <= self.bound_var.get()*10**6

    def trace(self, callback):
        self.callbacks.append(callback)