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
        
        parameter_names = ["constant", "linear", "annual (sin)", "annual (cos)", "bi-annual (sin)", "bi-annual (cos)"]

        def __init__(self, master) -> None:
            self.values = {name : tk.DoubleVar(master, value = 0) for name in self.parameter_names}
            self.sigmas = {name : tk.DoubleVar(master, value = nan) for name in self.parameter_names}
            self.is_custom = {name : tk.BooleanVar(master, value = True) for name in self.parameter_names}
            
            self.is_custom["constant"].set(False)
            self.is_custom["linear"].set(False)

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
            self.fpath_a = tk.StringVar(master, value = "")
            self.fpath_b = tk.StringVar(master, value = "")
            self.interpolation_type = tk.StringVar(master, value= "Linear")

            self.weighted = tk.BooleanVar(master, value = False)
    
            self.chi_squared = tk.DoubleVar()
            self.weighted_root_mean_squared = tk.DoubleVar()

            self.t0 = tk.DoubleVar(master, value = 2000)            
            self.t_min = tk.DoubleVar(master, value = 0)
            self.t_max = tk.DoubleVar(master, value = 0)
            self.max_sigma = tk.DoubleVar(master, value = 0)


    class DisplayState:
        
        def __init__(self, master) -> None:
            self.t_min_bound = tk.DoubleVar(master, value = 0)
            self.t_max_bound = tk.DoubleVar(master, value = 0)
            self.max_sigma_bound = tk.DoubleVar(master, value = 0)

            self.selected_serie = tk.StringVar(master, value = "X")
            self.selected_sigma = tk.StringVar(master, value = "X_SIGMA")
            self.master = tk.StringVar(master, value = "a")

            self.plot_type = tk.StringVar(master, "Residuals")