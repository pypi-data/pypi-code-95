import tkinter as tk 
import tkinter.ttk as ttk 

from .ParameterEntry import ParameterEntry
import EopTool.units as units

class ParameterView(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.master = master
        self.state = master.state 
        self.entry_dict = {}        
        parameter_dict = self.state.parameters.get_parameter_dict()

        ttk.Label(self, text = "Constant").grid(row=0, column=0, pady=(20,5), sticky="s")
        self.entry_dict["constant"] = ParameterEntry(self, parameter_dict["constant"])
        self.entry_dict["constant"].set_unit(units.micro)
        self.entry_dict["constant"].grid(row=1, column=0)

        ttk.Label(self, text = "Linear").grid(row=2, column=0)
        self.entry_dict["linear"] = ParameterEntry(self, parameter_dict["linear"])
        self.entry_dict["linear"].set_unit(units.micro)
        self.entry_dict["linear"].grid(row=3, column=0)
    
        ttk.Label(self, text = "Annual (sin)").grid(row=0, column=1, sticky="s", pady=5)
        self.entry_dict["annual (sin)"] = ParameterEntry(self, parameter_dict["annual (sin)"])
        self.entry_dict["annual (sin)"].set_unit(units.micro)
        self.entry_dict["annual (sin)"].grid(row=1, column=1)
    
        ttk.Label(self, text = "Annual (cos)").grid(row=2, column=1, pady=5)
        self.entry_dict["annual (cos)"] = ParameterEntry(self, parameter_dict["annual (cos)"])
        self.entry_dict["annual (cos)"].set_unit(units.micro)
        self.entry_dict["annual (cos)"].grid(row=3, column=1)
    
        ttk.Label(self, text = "Bi-annual (sin)").grid(row=0, column=2, sticky="s", pady=5)
        self.entry_dict["bi-annual (sin)"] = ParameterEntry(self, parameter_dict["bi-annual (sin)"])
        self.entry_dict["bi-annual (sin)"].set_unit(units.micro)
        self.entry_dict["bi-annual (sin)"].grid(row=1, column=2)

        ttk.Label(self, text = "Bi.annual (cos)").grid(row=2, column=2)
        self.entry_dict["bi-annual (cos)"] = ParameterEntry(self, parameter_dict["bi-annual (cos)"])
        self.entry_dict["bi-annual (cos)"].set_unit(units.micro)
        self.entry_dict["bi-annual (cos)"].grid(row=3, column=2)
