""" Eop visualisation.

This module contains all methods used for visualising Eop series and their residuals, using numpy and matplotlib as backend. 

The public methods availabe in this module are:

    *plot_serie, plots a data serie and its uncertainty
    *plot_residuals, plots residuals between two data series and their combined uncertainties.
    *plot_serie_to_ax, plots a data serie and its uncertainty to given axes objects
    *plot_residuals_to_ax, plots residuals between two data series and their combined uncertainties togiven axes objects.
    
"""

import matplotlib.pyplot as plt 
import numpy as np 
import EopTool.units as units

from EopTool.calc import predict_residuals

def plot_serie(df, selected_serie, ax, value_unit = units.one, sigma_unit = units.one):
    ax = plt.subplot()
    plot_serie_to_ax(df, selected_serie, ax, value_unit , sigma_unit)
    plt.show()

def plot_residuals():
    pass

def plot_serie_to_ax(df, selected_serie, ax, value_unit = units.one, sigma_unit = units.one):
    
    serie = df[selected_serie]
    ax[0].scatter(serie.index, serie*value_unit.convertion_factor, s=4)    
    ax[0].set_xlabel(f"year")
    ax[0].set_ylabel(value_unit.symbol)
    ax[0].grid()

    sigma = df[selected_serie + "_SIGMA"]
    ax[1].scatter(sigma.index, sigma*sigma_unit.convertion_factor, s=4)    
    ax[1].set_xlabel(f"year")
    ax[1].set_ylabel(sigma_unit.symbol)
    ax[1].grid()

    plt.tight_layout()

def plot_residuals_to_ax(df_from, df_to, selected_serie, t0, parameters, axes, value_unit = units.one, sigma_unit = units.one):
    
    if not df_from is None and not df_to is None:

        min_x = min(df_from.index)
        max_x = max(df_to.index)

        regression_x = np.linspace(min_x, max_x, 400)
        regression_y = predict_residuals(regression_x, t0, parameters)
        
        axes[0].plot(regression_x, regression_y*value_unit.convertion_factor, c="k")
        axes[0].scatter(df_from.index, (df_from[selected_serie] - df_to[selected_serie])*value_unit.convertion_factor, 2)
        axes[0].set_xlabel(f"year")
        axes[0].set_ylabel(value_unit.symbol)
        axes[0].grid()

        axes[1].scatter(df_from.index, np.sqrt(df_from[selected_serie + "_SIGMA"]**2 + df_to[selected_serie + "_SIGMA"]**2)*sigma_unit.convertion_factor, 2)
        axes[1].set_xlabel(f"year")
        axes[1].set_ylabel(sigma_unit.symbol)
        axes[1].grid()

        plt.tight_layout()

def plot_transformed_residuals_to_ax(df_from, df_to, selected_serie, t0, parameters, axes, value_unit = units.one, sigma_unit = units.one):
    if not df_from is None and not df_to is None:

        predicted_residuals = predict_residuals(df_from.index, t0, parameters)
        axes[0].scatter(df_from.index, (df_from[selected_serie] - df_to[selected_serie] - predicted_residuals)*value_unit.convertion_factor, 2)
        axes[0].set_xlabel(f"year")
        axes[0].set_ylabel(value_unit.symbol)
        axes[0].grid()

        axes[1].scatter(df_from.index, np.sqrt(df_from[selected_serie + "_SIGMA"]**2 + df_to[selected_serie + "_SIGMA"]**2)*sigma_unit.convertion_factor, 2)
        axes[1].set_xlabel(f"year")
        axes[1].set_ylabel(sigma_unit.symbol)
        axes[1].grid()