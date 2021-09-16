import tkinter as tk 
import tkinter.ttk as ttk

from .FileSelecter import FileSelecter
from .ParameterViewA import ParameterViewA
from .ParameterViewB import ParameterViewB
from .Plot import Plot
from .SelectStations import SelectStationsWindow 

from .InterfaceState import InterfaceState
from ..io import load_src_posn

from ..visualisation import plot_residuals
from ..calc import *

class MainWindow(tk.Tk):
    """Main application class for the helmert transfrom interface"""

    file_formats = [""]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        #Misc configuration
        self.title("Icrf Tool")
        design_mode = False  

        #Data
        self.df_from = None
        self.df_to = None
        self.stations = None
        self.transformed = None 

        self.state = InterfaceState(self)

        #Tkinter widgets
        self.title_label = tk.Label(self, text = "Icrf Tool", font=("Helvetica", 16))

        self.data_frame = tk.Frame(self)
        self.from_file_selecter_label = ttk.Label(self.data_frame, text="Transform from:")
        self.from_file_selecter = FileSelecter(self.data_frame, self.state.transform.from_file_path, self.state.transform.from_epoch, self.file_formats)
        self.to_file_selecter_label = ttk.Label(self.data_frame, text="Transform to:")
        self.to_file_selecter = FileSelecter(self.data_frame, self.state.transform.to_file_path, self.state.transform.to_epoch, self.file_formats)
        self.select_stations_button = ttk.Button(self.data_frame, text="Select stations", state = "disable")
        
        #self.line1 = ttk.Separator(self, orient = "horizontal")

        #self.config_frame = tk.Frame(self)
        self.weighted_button_label = ttk.Label(self.data_frame, text="Weighted")
        self.weighted_button = ttk.Checkbutton(self.data_frame, variable=self.state.transform.weighted, onvalue=True, offvalue=False)
        
        self.transform_type_combo_label = ttk.Label(self.data_frame, text="Transform type")
        self.transform_type_combo = ttk.Combobox(self.data_frame, textvariable=self.state.transform.type, values = ['A', 'B'], width=3)
        
        self.calculate_button = ttk.Button(self.data_frame, text = "Calculate parameter", state = "disable")
        self.transform_button = ttk.Button(self.data_frame, text = "Plot residuals", state = "disable")
        self.reset_button = ttk.Button(self.data_frame, text = "Reset parameters")
        
        #self.line2 = ttk.Separator(self, orient = "horizontal")

        self.parameter_frame = tk.Frame(self)
        self.parameter_view = ParameterViewA(self.parameter_frame)
        
        self.chi2_label = ttk.Label(self.parameter_frame, text = "Chi squared: ")
        self.chi_2_value = ttk.Label(self.parameter_frame, textvariable = self.state.transform.chi_squared) 
        self.wrms_label = ttk.Label(self.parameter_frame, text = "Weighted root mean squared: ")
        self.wrms_value = ttk.Label(self.parameter_frame, textvariable=self.state.transform.weighted_root_mean_squared)

        self.plot_frame = tk.Frame(self)
        self.plot = Plot(self.plot_frame, 1, 1)        
        #self.plot.fig.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9, wspace=0.1, hspace=0.1)
        self.plot.fig.tight_layout(pad=1)

        #Place Tkinter widgets

        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=1)

        self.columnconfigure(0, weight = 0)
        self.columnconfigure(1, weight = 1)

        self.title_label.grid(row = 0, column=0, sticky="w", padx=30, pady=20)

        self.data_frame.grid(row=1, column=0, padx=30, sticky = "news")
        self.from_file_selecter_label.grid(row=0, column=0, sticky="nw")
        self.from_file_selecter.grid(row=1, column=0, sticky="ew", pady=4, columnspan=6)
        self.to_file_selecter_label.grid(row=2, column=0, sticky="nw")
        self.to_file_selecter.grid(row=3, column=0, sticky="ew", pady=4, columnspan=6)
        #self.select_stations_button.grid(row=4, column=0, sticky = "w", pady=10)

        #self.line1.grid(row=4, column=0, sticky="ew")

        #self.config_frame.grid(row=6, column=0, padx=10, pady=10)
        self.weighted_button_label.grid(row=5, column=0)
        self.weighted_button.grid(row=6, column=0)

        self.transform_type_combo_label.grid(row=5, column=1)
        self.transform_type_combo.grid(row=6, column=1)

        self.calculate_button.grid(row=6, column=2, sticky="w")
        self.transform_button.grid(row=6, column=3, sticky="ew")
        self.reset_button.grid(row=6, column=4, sticky="e")

        #self.line2.grid(row=8, column=0, sticky="ew")

        self.parameter_frame.grid(row=2, column=0, padx=30, pady=50, sticky="news")
        self.parameter_view.grid(row=0, column=0, columnspan=4, pady=10, sticky="ew")
        #self.chi2_label.grid(row=1, column=0, sticky="n")
        #self.chi_2_value.grid(row=1, column=1, sticky="n")
        #self.wrms_label.grid(row=1, column=2, sticky="n")
        #self.wrms_value.grid(row=1, column=3, sticky="n")

        self.plot_frame.grid(row=0, column=1, rowspan=3, sticky="news")
        self.plot.pack(expand=True, fill='both')
        self.update_plot()
        
        #Bind actions
        self.state.transform.from_file_path.trace_add("write", self.df_from_change)
        self.state.transform.to_file_path.trace_add("write", self.df_to_change)
        self.select_stations_button.config(command = self.select_stations)

        self.state.transform.type.trace_add("write", self.transformation_type_change)

        self.calculate_button.config(command = self.calculate_parameters)
        self.transform_button.config(command = self.update_transform)
        self.reset_button.config(command = self.reset_parameters)

        if design_mode:
            self.title_label.config(background="red")
            self.parameter_frame.config(background="blue")
            self.data_frame.config(background="red")

    def transformation_type_change(self, *args):
        type = self.state.transform.type.get()
        self.parameter_view.destroy()
        
        if type == "A":
            self.parameter_view = ParameterViewA(self.parameter_frame)
        elif type == "B":
            self.parameter_view = ParameterViewB(self.parameter_frame)
        
        self.parameter_view.grid(row=0, column=0, columnspan=4, pady=10, sticky="ew")

    def select_stations(self, *args):
        """Open station selection window"""
        self.select_stations_window = SelectStationsWindow(self)

    def df_from_change(self, *args):
        """Called on from_file change."""
        if not self.state.transform.from_file_path.get()=="":
            self.df_from = load_src_posn(self.state.transform.from_file_path.get())
            self.set_stations()

    def df_to_change(self, *args):
        """Called on to_file change."""
        if not self.state.transform.to_file_path.get()=="":
            self.df_to = load_src_posn(self.state.transform.to_file_path.get())
            self.set_stations()

    def set_stations(self):
        """Updates the station list as the intersection of stations"""
        self.select_stations_button.config(state = "normal")
        self.transform_button.config(state = "normal")
        self.calculate_button.config(state = "normal")
        # if not self.df_from is None and not self.df_to is None:
        #     station_intersection = self.df_from.Station_Name.isin(self.df_to.Station_Name)
        #     df_from = self.df_from[station_intersection]
        #     df_to = self.df_to[station_intersection]

        #     sigmas = np.sqrt(df_from.X_sigma**2 + df_from.Y_sigma**2 + df_from.Z_sigma**2 + df_to.X_sigma**2 + df_to.Y_sigma**2 + df_to.Z_sigma**2) 
        #     stations = df_from.Station_Name

        #     self.stations = pd.DataFrame({"Station_Name" : stations, "Sigma" : sigmas, "Selected" : True})

    def calculate_parameters(self, *args):
        custom_dict = {}
        type = self.state.transform.type.get()
        
        if type == "A":
            for name, parameter in self.state.parameters_a.get_parameter_dict().items():
                if parameter.is_custom.get():
                    custom_dict[name] = parameter.value.get()
                else:
                    custom_dict[name] = None
        elif type == "B":
            for name, parameter in self.state.parameters_b.get_parameter_dict().items():
                if parameter.is_custom.get():
                    custom_dict[name] = parameter.value.get()
                else:
                    custom_dict[name] = None

        weighted = self.state.transform.weighted.get()

        df_from = self.df_from#[self.stations.Selected]
        df_to = self.df_to#[self.stations.Selected]

        value_dict, sigma_dict = calculate_parameters(df_from, df_to, weighted, custom_dict, type)

        if type == "A": 
            for name, value in value_dict.items():
                self.state.parameters_a.values[name].set(value)

            for name, value in sigma_dict.items():
                self.state.parameters_a.sigmas[name].set(value)
        elif type=="B":
            for name, value in value_dict.items():
                self.state.parameters_b.values[name].set(value)

            for name, value in sigma_dict.items():
                self.state.parameters_b.sigmas[name].set(value)

    def update_transform(self, *args):
        self.calculate_transform()
        self.update_plot()
        self.update_statistics()

    def calculate_transform(self, *args):
        type = self.state.transform.type.get()
        if type == "A":
            parameter_dict = {name : var.get() for name, var in self.state.parameters_a.values.items()}
        elif type == "B":
            parameter_dict = {name : var.get() for name, var in self.state.parameters_b.values.items()}


        df_from = self.df_from
        df_to = self.df_to
        
        type = self.state.transform.type.get()

        self.transformed = icrf_transform(df_from, parameter_dict, type = type)
        self.transformed = calculate_residuals(self.transformed, df_to)

    def update_plot(self, *args):
        self.plot.clear()
        if not self.transformed is None:
            transformed = self.transformed
        else:
            transformed = None
        plot_residuals(transformed, self.plot.axes)
        self.plot.draw()

    def update_statistics(self):
        df_from = self.df_from#[self.stations.Selected]
        df_to = self.df_to#[self.stations.Selected]
        
        standared_errors = df_from.X_sigma**2 + df_from.Y_sigma**2 + df_from.Z_sigma**2 + df_to.X_sigma**2 + df_to.Y_sigma**2 + df_to.Z_sigma**2
        value = sum(self.transformed.dX ** 2 / standared_errors)
        
        #self.state.transform.chi_squared.set(self.value_to_string(value))
        #self.state.transform.weighted_root_mean_squared.set(self.value_to_string(value/sum(1/standared_errors)))

    def reset_parameters(self, *args):
        """Reset all parameter values to zero"""
        type = self.state.transform.type.get()
        if type == "A":
            parameters = self.state.parameters_a.get_parameter_dict().values()
        if type == "B":
            parameters = self.state.parameters_b.get_parameter_dict().values()
        
        for parameter in parameters:
            parameter.value.set(0)
            if self.state.transform.weighted:
                parameter.sigma.set(0)
            else:
                #TODO: No value?
                parameter.sigma.set(0) 
    
    def value_to_string(self, value):
        string = "{:.4f}".format(value)
        return string     