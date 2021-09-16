import os
import tkinter as tk
import tkinter.ttk as ttk 
import numpy as np 

from EopTool.interface.InterfaceState import InterfaceState
from EopTool.interface.BoundedEntry import BoundedEntry
from EopTool.interface.FileSelecter import FileSelecter
from EopTool.interface.ParameterView import ParameterView 
from EopTool.interface.Plot import Plot
from EopTool.interface.SigmaEntry import SigmaEntry

import EopTool.units as units
import EopTool.calc as calc
import EopTool.io as io 
import EopTool.visualise as visualise

class MainWindow(tk.Tk):
    """Main applcation class for the eop tool interface"""
    
    file_formats = [".eob", ".eop", ".fil", ".txt"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #Data objects
        self.eop_data_a = EopData(self)
        self.eop_data_b = EopData(self)
        self.df_residuals = None
        self.state = InterfaceState(self)

        #Tkinter widgets
        self.create_elements()
        self.place_elements()
        self.update_plots()

        #Bind actions (functions are called last in first out)
        self.state.display.selected_serie.trace_add("write", lambda *args : self.state.display.selected_sigma.set(self.state.display.selected_serie.get() + "_SIGMA"))
        self.state.transform.fpath_a.trace_add("write", lambda *args : self.a_master_button.config(state = "normal"))
        self.state.transform.fpath_b.trace_add("write", lambda *args : self.b_master_button.config(state = "normal"))
        for var in [self.state.transform.fpath_a, self.state.transform.fpath_b, self.state.display.master, self.state.transform.weighted]:
            var.trace('w', self.update_statistics)
            var.trace("w", self.update_plots)
            var.trace("w", self.update_regression)
            var.trace("w", self.equalize_data)
            var.trace("w", self.update_bounds)
        
        for element in [self.t_min_entry, self.t_max_entry, self.max_sigma_entry]:
            element.trace(self.update_statistics)
            element.trace(self.equalize_data)
            element.trace(self.update_regression)
            element.trace(self.update_plots)

        for var in [self.state.transform.t0, self.state.display.selected_serie]:
            var.trace('w', self.update_statistics)
            var.trace("w", self.update_plots)
            var.trace("w", self.update_regression)

        self.state.transform.fpath_a.trace_add("write", lambda *args : self.eop_data_a.load(self.state.transform.fpath_a.get()))
        self.state.transform.fpath_b.trace_add("write", lambda *args : self.eop_data_b.load(self.state.transform.fpath_b.get()))

        self.state.display.plot_type.trace_add("write", self.update_plots)
        self.export_button.configure(command = self.export)

    def create_elements(self):
        """Create all tkinter elements"""

        self.result_frame = tk.Frame(self)
        self.a_plot = Plot(self.result_frame, 2, 1)
        self.residual_plot = Plot(self.result_frame, 2, 1)
        self.b_plot = Plot(self.result_frame, 2, 1)


        self.control_frame = tk.Frame(self)
        self.title_label = ttk.Label(self, text = "Eop Tool", font=("Helvetica", 16))

        self.fpath_a_label = ttk.Label(self.control_frame, text = "Data A:")
        self.fpath_a_selecter = FileSelecter(self.control_frame, self.state.transform.fpath_a, self.file_formats)
        self.a_master_button = ttk.Radiobutton(self.control_frame, variable = self.state.display.master, value = "a", state="disabled")
        self.fpath_b_label = ttk.Label(self.control_frame, text = "Data B:")
        self.fpath_b_selecter = FileSelecter(self.control_frame, self.state.transform.fpath_b, self.file_formats)
        self.b_master_button = ttk.Radiobutton(self.control_frame, variable = self.state.display.master, value = "b", state="disabled")
        
        self.t_min_entry_label = tk.Label(self.control_frame, text="Year min")
        self.t_min_entry = BoundedEntry(self.control_frame, self.state.transform.t_min, self.state.display.t_min_bound, self.state.transform.t_max, "down")
        self.t_max_entry_label = tk.Label(self.control_frame, text="Year max")
        self.t_max_entry = BoundedEntry(self.control_frame, self.state.transform.t_max, self.state.transform.t_min, self.state.display.t_max_bound, "up")
        self.max_sigma_entry_label = tk.Label(self.control_frame, text="σ max")
        self.max_sigma_entry = SigmaEntry(self.control_frame, self.state.transform.max_sigma, self.state.display.max_sigma_bound)

        self.text_display = ParameterView(self)

        self.t0_label = tk.Label(self.control_frame, text="Year offset")
        self.t0_entry = ttk.Entry(self.control_frame, textvariable=self.state.transform.t0, width=5)
        #self.interpolation_type_combo_label = tk.Label(self.control_frame, text = "Interpolation type")
        #self.interpolation_type_combo = ttk.Combobox(self.control_frame, textvariable=self.state.transform.interpolation_type, values=["Linear"])
        self.selected_serie_combo_label = tk.Label(self.control_frame, text = "Selected serie")
        self.selected_serie_combo = ttk.Combobox(self.control_frame, textvariable=self.state.display.selected_serie, values=["X", "Y", "UT1"], width=4)

        self.weighted_label = tk.Label(self.control_frame, text="Weighted")
        self.weighted_checkbox = ttk.Checkbutton(self.control_frame, variable=self.state.transform.weighted, onvalue=True, offvalue=False)

        self.plot_label = tk.Label(self.control_frame, text="Remove trend")
        self.plot_checkbox = ttk.Checkbutton(self.control_frame, variable=self.state.display.plot_type, onvalue="Transformed", offvalue="Residuals")

        self.statistic_frame = tk.Frame(self)
        self.chi_square_label = ttk.Label(self.statistic_frame, text = "Chi-squared: ")
        self.chi_square_display = ttk.Label(self.statistic_frame, textvariable=self.state.transform.chi_squared)
        self.wrms_label = ttk.Label(self.statistic_frame, text = "WRMS: ")
        self.wrms_display = ttk.Label(self.statistic_frame, textvariable=self.state.transform.weighted_root_mean_squared)

        self.export_button = ttk.Button(self.text_display, text = "Export")

        #Design
        if False:
            self.statistic_frame.config(background="red")
            self.control_frame.config(background="blue")
            self.result_frame.config(background="red")
            self.text_display.config(background="red")


    def place_elements(self):
        """Geometry management"""
        self.a_plot.grid(row=0, column=0, sticky="news")
        self.residual_plot.grid(row=0, column=1, sticky="news")
        self.b_plot.grid(row=0, column=2, sticky="news")
        self.result_frame.columnconfigure(0, weight=1)
        self.result_frame.columnconfigure(1, weight=1)
        self.result_frame.columnconfigure(2, weight=1)
        self.result_frame.rowconfigure(0, weight=1)

        self.fpath_a_label.grid(row=1, column = 0, sticky="w")
        self.fpath_a_selecter.grid(row=2, column=0, sticky="ew", columnspan=8)
        self.a_master_button.grid(row=2, column=8)
        self.fpath_b_label.grid(row=3, column=0, sticky="w")
        self.fpath_b_selecter.grid(row=4, column=0, sticky="ew", columnspan=8)
        self.b_master_button.grid(row=4, column=8)
        
        self.t_min_entry_label.grid(row=5, column=0, sticky="ew", padx=4, pady=(0,0))
        self.t_min_entry.grid(row=6, column=0, padx=4)
        self.t_max_entry_label.grid(row=5, column=1, sticky="ew", padx=4)
        self.t_max_entry.grid(row=6, column=1, padx=4)
        self.max_sigma_entry_label.grid(row=5, column=2, sticky="ew", padx=4)
        self.max_sigma_entry.grid(row=6, column=2, sticky="ew", padx=4)
        self.t0_label.grid(row=5, column=3, padx=4)
        self.t0_entry.grid(row=6, column=3, padx=4)
        self.selected_serie_combo_label.grid(row=5, column=4, padx=4)
        self.selected_serie_combo.grid(row=6, column=4, padx=4)
        self.weighted_label.grid(row=5, column=5, padx=4)
        self.weighted_checkbox.grid(row=6, column=5, padx=4)
        self.plot_label.grid(row=5, column=6, padx=4)
        self.plot_checkbox.grid(row=6, column=6, padx=4)

        self.chi_square_label.grid(row=0, column=0)
        self.chi_square_display.grid(row=0, column=1)
        self.wrms_label.grid(row=0, column=2)
        self.wrms_display.grid(row=0, column=3)

        self.result_frame.grid(row=0, column=0, columnspan=2, sticky = "news", pady=(0,20))
        self.title_label.grid(row=1, column=0, sticky="ws", padx = 30, pady=0)
        self.control_frame.grid(row=2, column=0, padx=30, sticky="w")
        self.text_display.grid(row=2, column=1, padx=30, sticky="w")
        self.statistic_frame.grid(row=3,column=0, columnspan = 2, ipady = 20)

        self.export_button.grid(row=4, column=1,pady=30)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)


    def equalize_data(self, *args):
        """Apply the same filtering to both datasets and interpolate the data of the slave to the master epoch"""
        if self.eop_data_a.loaded and self.eop_data_b.loaded:
            eop_master = self.get_master()
            eop_slave = self.get_slave()
            
            t_min = self.state.transform.t_min.get()
            t_max = self.state.transform.t_max.get()
            sigma_max = self.state.transform.max_sigma.get()
            selected_sigma = self.state.display.selected_sigma.get()

            eop_master.filter_df(t_min, t_max, sigma_max, selected_sigma)
            eop_slave.filter_df(0, 3000, sigma_max, selected_sigma)
            master_epoch = eop_master.get_epoch()
            eop_slave.change_epoch(master_epoch)

    def get_master(self):
        """Returns the currently selected master eop data object"""
        if self.state.display.master.get()=="a":
            return self.eop_data_a
        else:
            return self.eop_data_b

    def get_slave(self):
        """Returns the currently selected slave eop data object"""
        if self.state.display.master.get()=="a":
            return self.eop_data_b
        else:
            return self.eop_data_a

    def update_bounds(self, *args):
        """Update the bounds of the time and sigma filters from the intersection of both datasets"""
        self.state.display.max_sigma_bound.set(self.get_master().get_max_sigma(self.state.display.selected_sigma.get()))
        self.state.transform.max_sigma.set(self.state.display.max_sigma_bound.get())
        self.max_sigma_entry.set(self.state.display.max_sigma_bound.get())

        self.state.display.t_min_bound.set(max(self.eop_data_a.get_t_min(), self.eop_data_b.get_t_min()))
        self.state.transform.t_min.set(self.state.display.t_min_bound.get())
        self.t_min_entry.set(self.state.display.t_min_bound.get())
        
        self.state.display.t_max_bound.set(min(self.eop_data_a.get_t_max(), self.eop_data_b.get_t_max()))
        self.state.transform.t_max.set(self.state.display.t_max_bound.get())
        self.t_max_entry.set(self.state.display.t_max_bound.get())

    def update_regression(self, *args):
        """Make a new regression of the residuals"""
        if self.eop_data_a.loaded and self.eop_data_b.loaded:
            custom_dict = {}
            for name, parameter in self.state.parameters.get_parameter_dict().items():
                if parameter.is_custom.get():
                    custom_dict[name] = parameter.value.get()
                else:
                    custom_dict[name] = None
    
            weighted = self.state.transform.weighted.get()            
            t0 = self.state.transform.t0.get()
            selected_serie = self.state.display.selected_serie.get()

            value_dict, sigma_dict = calc.calculate_parameters(self.get_master().df, self.get_slave().df, weighted, selected_serie, t0, custom_dict)
            for name, value in value_dict.items():
                self.state.parameters.values[name].set(value)

            for name, value in sigma_dict.items():
                self.state.parameters.sigmas[name].set(value)

    def update_statistics(self, *args):
        if self.eop_data_a.loaded and self.eop_data_b.loaded:
            df_from = self.get_master().df
            df_to = self.get_slave().df
            selected_serie = self.state.display.selected_serie.get()
            t0 = self.state.transform.t0.get()
            parameters = {name : var.get() for name, var in self.state.parameters.values.items()}

            chi_squared, wrms = calc.regresssion_statistics(df_from, df_to, selected_serie, t0, parameters)
            self.state.transform.chi_squared.set(self.value_to_string(chi_squared))
            self.state.transform.weighted_root_mean_squared.set(self.value_to_string(wrms))    

    def update_plots(self, *args):
        """Replots all plots"""
        self.a_plot.clear()
        self.eop_data_a.plot(self.state.display.selected_serie.get(), self.a_plot.axes)
        self.a_plot.draw()

        self.residual_plot.clear()
        params = {name : var.get() for name, var in self.state.parameters.values.items()}
        
        if self.state.display.selected_serie.get() in ["X", "Y"]:
            value_unit, sigma_unit = units.micro_arcsecond, units.micro_arcsecond
        else:
            value_unit, sigma_unit = units.micro_second, units.micro_second

        if self.state.display.plot_type.get() == "Residuals":
            visualise.plot_residuals_to_ax(self.get_master().df, self.get_slave().df, self.state.display.selected_serie.get(), self.state.transform.t0.get(), params, self.residual_plot.axes, value_unit, sigma_unit)
        else:
            visualise.plot_transformed_residuals_to_ax(self.get_master().df, self.get_slave().df, self.state.display.selected_serie.get(), self.state.transform.t0.get(), params, self.residual_plot.axes, value_unit, sigma_unit)
        
        self.residual_plot.axes[0].set_title("Residuals")
        self.residual_plot.draw()

        self.b_plot.clear()
        self.eop_data_b.plot(self.state.display.selected_serie.get(), self.b_plot.axes)
        self.b_plot.draw()

#         self.text_display.set(f"""params: {self.residual_data.parameters}
# sigma: {self.residual_data.measures}""")

    def microsigma_to_percent(self, value):
        return self.get_master().microsigma_to_percent(value, self.state.display.selected_sigma.get())

    def percent_to_microsigma(self, value):
        return self.get_master().percent_to_microsigma(value, self.state.display.selected_sigma.get())

    def value_to_string(self, value):
        #string = value
        string = "{:.4f}".format(value)
        return string   

    def export(self, *args):
        
        f = tk.filedialog.asksaveasfile(mode='w', defaultextension=".txt")
        
        if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
            return
        
        parameters = self.state.parameters.values
        sigmas = self.state.parameters.sigmas
        
        selected_serie = self.state.display.selected_serie.get()
        df = self.get_master().df[selected_serie] - self.get_slave().df[selected_serie]
        df["sigmas"] = np.sqrt(self.get_master().df[selected_serie + "_SIGMA"]**2 + self.get_slave().df[selected_serie + "_SIGMA"]**2)
        string = io.to_string(df, parameters, sigmas)
        f.write(string)
        f.close()

class EopData():
    
    def __init__(self, interface):
        self.df_original = None
        self.df = None
        self.loaded = False 
        self.title = "No data"
        self.extenstion = ""
        self.interface = interface

    def get_max_sigma(self, column):
        return self.df_original[column].max() if self.loaded else np.inf
    
    def get_t_max(self):
        return round(self.df_original.index.max() - 0.05, ndigits=1) if self.loaded else np.inf
    
    def get_t_min(self):
        return round(self.df_original.index.min() + 0.05, ndigits=1) if self.loaded else -np.inf
    
    def get_epoch(self):
        if self.loaded:
            return self.df.index

    def load(self, fpath):
        self.df_original = io.load(fpath)
        self.df = self.df_original
        self.loaded = True 
        self.title = os.path.basename(fpath)

    def filter_df(self, t_min, t_max, max_sigma, sigma_column):
        if self.loaded:
            df = self.filter_time(self.df_original, t_min, t_max)
            df = self.filter_sigma(df, max_sigma, sigma_column)
            self.df = df

    def change_epoch(self, epoch):
        if self.loaded:
            self.df = calc.change_epoch(self.df, epoch)
            
    def plot(self, selected_serie, axes):
        if self.loaded:

            if selected_serie in ["X", "Y"]:
                value_unit, sigma_unit = units.milli_arcsecond, units.micro_arcsecond
            else:
                value_unit, sigma_unit = units.second, units.micro_second

            visualise.plot_serie_to_ax(self.df, selected_serie, axes, value_unit, sigma_unit)
            

            if self.interface.get_master() is self:
                axes[0].set_title(f"{self.title} {selected_serie} (Primary)")
            else:
                axes[0].set_title(f"{self.title} {selected_serie} (Secondary)")
        else:
            axes[0].set_title("No data")

    def percent_to_microsigma(self, percent_value, selected_serie):
        if self.loaded:
            serie = self.df_original[selected_serie]

            if percent_value == 0:
                return 0
            else:
                n_selected = round((percent_value/100)*len(serie.index))
                sigma = serie.nsmallest(n_selected).max()
                microsigma = sigma * 10**6

                return microsigma
        
        else: 
            return 0 

    def microsigma_to_percent(self, microsigma_value, selected_serie):
        if self.loaded:
            serie = self.df_original[selected_serie]

            n_less_than_sigma = sum(serie <= microsigma_value/10**6)
            n_total = len(serie.index)

            percent_value =  100 * (n_less_than_sigma/n_total)
            return round(percent_value, ndigits=3)
        else:
            return 0

    @staticmethod
    def filter_time(df, t_min, t_max):
        min_limit = t_min <= df.index
        max_limit = df.index <= t_max

        return df[min_limit & max_limit]

    @staticmethod
    def filter_sigma(df, max_sigma, sigma_column):
        return df[df[sigma_column]<=max_sigma]
