from symbol import parameters
import tkinter as tk 
from collections import namedtuple
from numpy import nan

class InterfaceState:
    """Seperation layer between interface and logic, keeps information of currently """

    def __init__(self, master) -> None:
        self.parameters = self.ParameterState(master)
        self.transform = self.TransformState(master)
        self.display = self.DisplayState(master)

    class ParameterState:
        
        translation_names = ["translation_x", "translation_y", "translation_z"]
        scale_names = ["scale_x", "scale_y", "scale_z"]
        rotation_names =  ["rotation_x", "rotation_y", "rotation_z"]
        parameter_names = [*translation_names, *scale_names, *rotation_names]

        def __init__(self, master) -> None:
            self.values = {name : tk.DoubleVar(master, value = 0) for name in self.parameter_names}
            self.sigmas = {name : tk.DoubleVar(master, value = nan) for name in self.parameter_names}
            self.is_custom = {name : tk.BooleanVar(master, value = False) for name in self.parameter_names}

        def get_parameter_dict(self):
            """Return all vars as Parameter tuples"""
            Parameter = namedtuple("Parameter", ["value", "sigma", "is_custom"])         
            result = {}

            for name, value, sigma, is_custom in zip(self.parameter_names, 
                                                    self.values.values(), 
                                                    self.sigmas.values(), 
                                                    self.is_custom.values()):
                result[name] = Parameter(value, sigma, is_custom)

            return result    

    class TransformState:
        
        def __init__(self, master) -> None:
            self.to_file_path = tk.StringVar(master, value = "")
            self.from_file_path = tk.StringVar(master, value = "")
            self.to_epoch = tk.DoubleVar(master, value = 2000)
            self.from_epoch = tk.DoubleVar(master, value = 2000)
            self.weighted = tk.BooleanVar(master, value = False)
            self.type = tk.StringVar(master, value = "7")
    
            self.chi_squared = tk.DoubleVar()
            self.weighted_root_mean_squared = tk.DoubleVar()

    class DisplayState:
        
        def __init__(self, master) -> None:
            self.translation_unit = tk.StringVar(master, value = "")
            self.scale_unit = tk.StringVar(master, value = "")
            self.rotation_unit = tk.StringVar(master, value= "")