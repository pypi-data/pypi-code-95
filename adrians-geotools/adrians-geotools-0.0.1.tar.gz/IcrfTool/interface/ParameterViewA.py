import tkinter as tk 

from .ParameterEntry import ParameterEntry
from ..units import *

class ParameterViewA(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.state = master.master.state 
        self.entry_dict = {}
        frames = []
        
        parameter_dict = self.state.parameters_a.get_parameter_dict()

        tk.Label(self, text = "R")
        for j, name_list in enumerate([["R1", "R2", "R3"], 
                            ["D1", "D2", "D3"], 
                            ["M20"], ["E20"], 
                            ["E21 Re", "E21 Im"],
                            ["M21 Re", "M21 Im"], 
                            ["E22 Re", "E22 Im"], 
                            [ "M22 Re", "M22 Im"]]):

            frames.append(tk.Frame(self))

            for i, name in enumerate(name_list):
                #tk.Label(frames[j], text=name).grid(row=0, column=2*i, pady=5, padx=3, sticky="w")
                self.entry_dict[name] = ParameterEntry(frames[j], parameter_dict[name])
                self.entry_dict[name].set_unit(nano)
                self.entry_dict[name].grid(row = 0, column = 2*i+1)


        for i, (frame, name) in enumerate(zip(frames, ["R", "D", "M20", "E20", "E21","M21", "E22", "M22"])):
            tk.Label(self, text=name).grid(row=i, column=0, sticky="w")
            frame.grid(row=i, column=1)

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

    
