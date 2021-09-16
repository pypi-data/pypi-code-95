""" Eop Calculator 

This module contains all methods used for calculations on the eop-data, using numpy and pandas as backend. The dataframes are expected to 
have the time in year as index and columns with values in "selected_serie" and uncertainties in "selected_serie_SIGMA". 

The public functions available from the module are

    *change_epoch - returns a pandas dataframe with the index resampled to a given epoch index
    *calculate_parameters - returns a dict with the parameters of a least squares fit of the residuals of two series as a function of time 
    *predict_residuals - returns predictions for the residuals given parameters and year
    *get_parameter_dict - returns a dictionary with the keys expected by all parameter dicts, for convenience.
"""

import numpy as np 
import pandas as pd


def change_epoch(df : pd.DataFrame, epoch : pd.Index) -> pd.DataFrame:
    """Returns a dataframe resampled to given index through linear interpolation.

    Standard errors marked by containing "_SIGMA" in the column names are first transformed into variances to be interpolated correctly. 
    The new epoch may extend beyond the limtis of the old one, in which case the measurements are set to zero.
    """

    if isinstance(epoch, pd.Index):
        epoch = epoch.to_series()

    for column_name in df.columns:
        if "_SIGMA" in column_name:
            df[column_name] = df[column_name] ** 2

    df = df.merge(epoch, "outer", left_index=True, right_index=True)
    df = df.sort_index()
    df = df.interpolate("index")
    df = df.loc[epoch]

    for column_name in df.columns:
        if "_SIGMA" in column_name:
            df[column_name] = np.sqrt(df[column_name])

    df = df.fillna(0)

    return df

def calculate_parameters(df_from: pd.DataFrame, df_to: pd.DataFrame, weighted: bool, selected_serie: str, t0 : int = 2000, custom_dict : dict = None) -> tuple[dict, dict]:
    """Calculates a least squares residual fit to the resdiuals of two series as a function of time. Returns the values and sigmas as a tuple of dicts.

    The function to be fitted has constant, linear, annual and biannual components:
        A + B(t-t0) + C1sin((t-t0)2π) + C2cos((t-t0)2π) + D1sin(2*(t-t0)2π) + D1cos(2*(t-t0)2π) 

    and may be either weighted or unweighted. Additionally by supplying a custom_dict with given values for certain parameters, 
    these values are fixed and the rest of the parameters are calculated with respect to that. For example, you may remove all 
    annual components by setting these values to 0. None values indicate parameters to be calculated.
    """

    #Create custom_dict if not specified
    if custom_dict is None:
        custom_dict = get_parameter_dict()

    #Create observations from data
    design_vectors = __get_design_columns(df_from, t0)
    observation_vector = __get_observation_vector(df_from, df_to, selected_serie)

    #Subtract custom variables and delete those columns
    keys_to_delete = []
    for parameter, custom_value in custom_dict.items():
        if not custom_value is None:
            observation_vector = observation_vector - design_vectors[parameter] * custom_value
            keys_to_delete.append(parameter)
    for key in keys_to_delete:
        del design_vectors[key]             

    #If all parameters were given from start, return nothing.
    if len(design_vectors) == 0:
        return {}, {}
    
    #Perform least square regression and return values in a dict
    design_matrix = np.vstack(list(design_vectors.values())).T
    uncertainties = {parameter : np.nan for parameter in custom_dict}
    
    if weighted:
        observation_var_matrix = __get_var_matrix(df_from, df_to, selected_serie)
        parameters, new_uncertainties = __weighted_least_squares(design_matrix, observation_vector, observation_var_matrix)
        new_uncertainties = {parameter : sigma for parameter, sigma in zip(design_vectors, new_uncertainties)}
        uncertainties.update(new_uncertainties)

    else:
        parameters = __ordinary_least_squares(design_matrix, observation_vector)

    parameters = {parameter : value for parameter, value in zip(design_vectors.keys(), parameters)}


    return parameters, uncertainties


def predict_residuals(t : float, t0 : float, parameters : dict) -> float:
    """Predict residuals given time and parameters.

    The function used for prediction has constant, linear, annual and biannual components:
        A + B(t-t0) + C1sin((t-t0)2π) + C2cos((t-t0)2π) + D1sin(2*(t-t0)2π) + D1cos(2*(t-t0)2π) 

    where the parameters dict is expected to conform to the structure given by get_parameter_dict.  
    The argument t may also be supplied as a numpy array or a pandas serie to predict many times at once.
    """
   
    t = t - t0
    return parameters["constant"] + \
           parameters["linear"]*t + \
           parameters["annual (sin)"]* np.sin(2*np.pi*t) + \
           parameters["annual (cos)"] * np.cos(2*np.pi*t) + \
           parameters["bi-annual (sin)"] * np.sin(4*np.pi*t) + \
           parameters["bi-annual (cos)"] * np.cos(4*np.pi*t)


def get_parameter_dict():
    """Returns a dictionary with keys expected by all parameter dicts and values set to None."""
    
    custom_dict = {name : None for name in ["constant", "linear", "annual (sin)", "annual (cos)", "bi-annual (sin)", "bi-annual (cos)"]}
    return custom_dict 

def regresssion_statistics(df_from: pd.DataFrame, df_to: pd.DataFrame, selected_serie: str, t0: int, parameters: dict):
    """Calculates the reduced chi squared and weighted root mean squared values for the given parameters"""
    
    residuals = df_from[selected_serie] - df_to[selected_serie]
    epoch = residuals.index
    predicted_residuals = predict_residuals(epoch, t0, parameters)
    residual_errors = residuals - predicted_residuals

    selected_sigma = selected_serie + "_SIGMA"
    variances = df_from[selected_sigma]**2 + df_to[selected_sigma]**2 #Should include parameter uncertainites?
    value = sum(residual_errors ** 2 / variances)
    
    deg_of_freedom = len(epoch) - 6

    chi_squared = value/deg_of_freedom
    wrms = value/sum(1/variances)

    return chi_squared, wrms



#private functions
def __get_observation_vector(df_from: pd.DataFrame, df_to: pd.DataFrame, selected_serie: str):
    """Returns a observation vector with residuals of the selected serie"""
    
    observation_matrix = df_from[selected_serie] - df_to[selected_serie]
    return observation_matrix
    
def __get_design_columns(df: pd.DataFrame, t0: int):
    """Returns a dictionary with keys for each column in the design matrix"""
    epoch = df.index - t0

    result = {"constant" : np.ones(len(df.index)),
    "linear" : epoch,
    "annual (sin)" : np.sin(2*np.pi*epoch),
    "annual (cos)" : np.cos(2*np.pi*epoch),
    "bi-annual (sin)" : np.sin(4*np.pi*epoch),
    "bi-annual (cos)" : np.cos(4*np.pi*epoch)}

    return result

def __get_var_matrix(df_from: pd.DataFrame, df_to: pd.DataFrame, selected_serie):
    """Creates a diagonal weight matrix for a WLS parameter fitting""" 
    selected_sigma = selected_serie + "_SIGMA"
    var = df_from[selected_sigma]**2 + df_to[selected_sigma]**2
    weight_matrix = np.diag(var)
    
    return weight_matrix

def __ordinary_least_squares(design_matrix, observation_matrix, parameter_names = None):
    """Ordinary least squares fit"""
    parameters = np.linalg.inv(design_matrix.T @ design_matrix) @ design_matrix.T @ observation_matrix

    return parameters

def __weighted_least_squares(design_matrix, observation_matrix, observation_var_matrix, parameter_names = None):
    """Weighted least squares fit under the assumption of uncorrelated measurement errors"""
    weight_matrix = np.linalg.inv(observation_var_matrix)

    parameter_uncertainties = np.linalg.inv(design_matrix.T @ weight_matrix @ design_matrix)
    parameters = parameter_uncertainties @ design_matrix.T @ weight_matrix @ observation_matrix
    parameter_uncertainties = np.sqrt(np.diag(parameter_uncertainties))

    return parameters, parameter_uncertainties