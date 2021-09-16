import tkinter as tk 
import tkinter.ttk as ttk 

from .ParameterEntry import ParameterEntry
from ..units import *

class ParameterView(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.state = master.master.state 
        self.entry_dict = {name : ParameterEntry(self, par) for name, par in self.state.parameters.get_parameter_dict().items()}

        parameters = self.state.parameters.get_parameter_dict()
        self.entry_dict["scale_y"].master_parameter = parameters["scale_x"]
        self.entry_dict["scale_z"].master_parameter = parameters["scale_x"]

        ttk.Label(self, text = "Translation").grid(row=0, column=0, pady=5)
        for i, name in enumerate(self.state.parameters.translation_names,1):
            self.entry_dict[name].set_unit(milli_meter)
            self.entry_dict[name].grid(row = i, column = 0)

        ttk.Label(self, text = "Scale").grid(row=0, column=1, pady=5)
        for i, name in enumerate(self.state.parameters.scale_names,1):
            self.entry_dict[name].set_unit(milli)
            self.entry_dict[name].grid(row = i, column = 1)

        ttk.Label(self, text = "Rotation").grid(row=0, column=2, pady=5)
        for i, name in enumerate(self.state.parameters.rotation_names,1):
            self.entry_dict[name].set_unit(nano_radian)
            self.entry_dict[name].grid(row = i, column = 2)

        self.scale_type_change()
        ttk.Checkbutton(self, variable=self.state.display.scale_unit, onvalue="micro", offvalue="milli", text="Change scale").grid(row=4, column=1, pady=7)
        ttk.Checkbutton(self, variable=self.state.display.rotation_unit, onvalue="classic", offvalue="si", text="Change scale").grid(row=4, column=2, pady=7)

        self.state.display.scale_unit.trace_add("write", self.scale_unit_change)
        self.state.display.rotation_unit.trace_add("write", self.rotation_unit_change)

    def scale_unit_change(self, *args):
        if self.state.display.scale_unit.get() == "milli":
            self.entry_dict["scale_x"].set_unit(milli)
            self.entry_dict["scale_y"].set_unit(milli)
            self.entry_dict["scale_z"].set_unit(milli)
        elif self.state.display.scale_unit.get() == "micro":
            self.entry_dict["scale_x"].set_unit(micro)
            self.entry_dict["scale_y"].set_unit(micro)
            self.entry_dict["scale_z"].set_unit(micro)

    def rotation_unit_change(self, *args):
        if self.state.display.rotation_unit.get() == "si":
            self.entry_dict["rotation_x"].set_unit(nano_radian)
            self.entry_dict["rotation_y"].set_unit(nano_radian)
            self.entry_dict["rotation_z"].set_unit(nano_radian)

        elif self.state.display.rotation_unit.get() == "classic":
            self.entry_dict["rotation_x"].set_unit(micro_arcsecond)
            self.entry_dict["rotation_y"].set_unit(micro_arcsecond)
            self.entry_dict["rotation_z"].set_unit(timesecond)

    def scale_type_change(self, *args):    
        """"""
        if self.state.transform.type.get() == "7":
            self.entry_dict["scale_y"].toggle_slave(True)
            self.entry_dict["scale_z"].toggle_slave(True)
        if self.state.transform.type.get() == "8":
            self.entry_dict["scale_y"].toggle_slave(True)
            self.entry_dict["scale_z"].toggle_slave(False)
        if self.state.transform.type.get() == "9":
            self.entry_dict["scale_y"].toggle_slave(False)
            self.entry_dict["scale_z"].toggle_slave(False)

    
