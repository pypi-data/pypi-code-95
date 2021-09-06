# -*- coding: utf-8 -*-
"""
Created on Thu Sep  2 11:50:41 2021

@author: chris.kerklaan
"""


def mm_5_min_to_ms(mm_5min_value):
    """Converting values from 'mm/5min' to the 'm/s'."""
    ms_value = (mm_5min_value * 12) / 3600 * 0.001
    return ms_value


def mmtimestep_to_mmh(value, timestep, units="s"):
    """Converting values from 'mm/timestep' to the 'mm/h'."""
    if units == "s":
        timestep_seconds = timestep
    elif units == "mins":
        timestep_seconds = timestep * 60
    elif units == "hrs":
        timestep_seconds = timestep * 3600
    else:
        raise ValueError(f"Unsupported timestep units format ({units})!")
    value_per_second = value / timestep_seconds
    mmh_value = value_per_second * 3600
    return mmh_value
