from symbol import parameters
import tkinter as tk 
from collections import namedtuple
from numpy import nan

class InterfaceState:
    """Seperation layer between interface and logic, keeps information of currently """

    def __init__(self, master) -> None:
        self.parameters_a = self.ParameterStateA(master)
        self.parameters_b = self.ParameterStateB(master)
        self.transform = self.TransformState(master)
        self.display = self.DisplayState(master)

    class ParameterStateA:
        
        parameter_names = ["R1", "R2", "R3", 
                            "D1", "D2", "D3", 
                            "M20", "E20", 
                            "E21 Re", "E21 Im",
                             "M21 Re", "M21 Im", 
                             "E22 Re", "E22 Im", 
                             "M22 Re", "M22 Im"]

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

    class ParameterStateB:
        
        parameter_names = ["A1", "A2", "A3", "D_alpha", "D_delta", "B_delta"]

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
            self.type = tk.StringVar(master, value = "A")
    
            self.chi_squared = tk.DoubleVar()
            self.weighted_root_mean_squared = tk.DoubleVar()

    class DisplayState:
        
        def __init__(self, master) -> None:
            self.translation_unit = tk.StringVar(master, value = "")
            self.scale_unit = tk.StringVar(master, value = "")
            self.rotation_unit = tk.StringVar(master, value= "")