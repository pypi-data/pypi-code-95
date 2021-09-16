import tkinter as tk 
import tkinter.ttk as ttk 
import numpy as np 

from ..units import *

class ParameterEntry(tk.Frame):
    
    def __init__(self, master, parameter, master_parameter = None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.parameter = parameter
        self.master_parameter = master_parameter
        self.is_slave = False
        self.trace_ids = {}

        self.parameter.value.trace("w", self.set_value_from_external)
        self.parameter.sigma.trace("w", self.set_sigma_from_external)
        self.parameter.is_custom.trace("w", self.set_state)

        self.internal_var = tk.StringVar(self, value = "")
        self.state_var = self.parameter.is_custom
        
        self.sigma_var = tk.StringVar(self, value = "")
        self.unit_text_var = tk.StringVar(self, "")

        self.set_unit(meter)
        self.set_value_from_external()
        self.set_sigma_from_external()

        self.edit_check = ttk.Checkbutton(self, variable=self.state_var, onvalue=True, offvalue=False)
        self.entry = ttk.Entry(self, textvariable=self.internal_var, state = "disabled", width=10)
        self.plus_minus_sign = ttk.Label(self, text = "±")
        self.sigma_entry = ttk.Label(self, textvariable=self.sigma_var, width = 6)

        self.entry.bind("<Return>", self.set_from_internal)
        self.entry.bind("<Tab>", self.set_from_internal)
        self.entry.bind("<FocusOut>", self.set_from_internal)

        self.unit_label = ttk.Label(self, textvariable=self.unit_text_var, width=4)
    
        self.edit_check.grid(row=0, column=0)
        self.entry.grid(row=0, column=1)
        self.plus_minus_sign.grid(row=0, column=2)
        self.sigma_entry.grid(row=0, column=3)
        self.unit_label.grid(row=0, column=4)

    def set_unit(self, unit):
        """Change unit of the displayed value"""
        self.unit = unit
        self.unit_text_var.set(unit.symbol)

        value = self.parameter.value.get() * unit.convertion_factor
        self.internal_var.set(self.value_to_string(value))

        sigma = self.parameter.sigma.get()
        if np.isnan(sigma):
            self.sigma_var.set("N/A")
        else:
            sigma = sigma * self.unit.convertion_factor
            self.sigma_var.set(self.value_to_string(sigma))

    def set_value_from_external(self, *args):
        """Set displayed value from external value"""
        value = self.parameter.value.get()
        if np.isnan(value):
            self.internal_var.set("N/A")
        else:
            value = value * self.unit.convertion_factor
            self.internal_var.set(self.value_to_string(value))

    def set_sigma_from_external(self, *args):
        sigma = self.parameter.sigma.get()
        if np.isnan(sigma):
            self.sigma_var.set("N/A")
        else:
            sigma = sigma * self.unit.convertion_factor
            self.sigma_var.set(self.value_to_string(sigma))

    def set_from_internal(self, *args):
        """Set external value from entered internal value, reset on failure"""
        new_value = self.internal_var.get()
        
        try: 
            new_value = float(new_value)/self.unit.convertion_factor
            assert self.validate(new_value)
            self.parameter.value.set(new_value)

        except:
            if new_value == "":
                self.parameter.value.set(0)

        self.set_value_from_external()
        self.set_sigma_from_external()

    def validate(self, value):
        """Validation, (currently not in use)"""
        return True

    def set_state(self, *args):
        """Enable/ disable entry field based on the state variable"""
        state = "normal" if self.state_var.get() and not self.is_slave else "disabled"
        
        self.entry.config(state=state)
        #self.sigma_entry.config(state=state)

    def set_from_master_is_custom(self, *args):
        """Set own state variable by an external master_variable"""
        value = self.master_parameter.is_custom.get()
        self.parameter.is_custom.set(value)

    def set_from_master_value(self, *args):
        value = self.master_parameter.value.get()
        self.parameter.value.set(value)
        self.set_value_from_external()

    def set_from_master_sigma(self, *args):
        value = self.master_parameter.sigma.get()
        self.parameter.sigma.set(value)
        self.set_sigma_from_external()

    def toggle_slave(self, is_slave : bool):
        """The widget may operate in two states, enabled and following its own state, or disabled and following another master_variable"""

        if is_slave and not self.is_slave:
            self.is_slave = True
            self.edit_check.config(state = "disabled")
            
            self.trace_ids["value"] = self.master_parameter.value.trace_add("write", self.set_from_master_value) 
            self.trace_ids["sigma"] = self.master_parameter.sigma.trace_add("write", self.set_from_master_sigma) 
            self.trace_ids["is_custom"] = self.master_parameter.is_custom.trace_add("write", self.set_from_master_is_custom) 

            self.set_from_master_value()
            self.set_from_master_sigma()
            self.set_from_master_is_custom()

        elif not is_slave and self.is_slave:
            self.is_slave = False
            self.edit_check.config(state = "normal")

            self.master_parameter.value.trace_remove("write", self.trace_ids["value"])
            self.master_parameter.sigma.trace_remove("write", self.trace_ids["sigma"])
            self.master_parameter.is_custom.trace_remove("write", self.trace_ids["is_custom"])

            self.set_state()
        
    def value_to_string(self, value):
        string = "{:.4f}".format(value)
        return string     