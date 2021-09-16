import pandas as pd
import numpy as np 

from IcrfTool.interface.InterfaceState import InterfaceState

def calculate_parameters(df_from: pd.DataFrame, df_to: pd.DataFrame, weighted: bool, custom_dict : dict = None, type : str = "A"):
    """Calculates Icrf parameters and a dict specifying values of parameters of which it should not calculate"""

    df_combined = pd.merge(df_from, df_to, how = "inner", left_index=True, right_index=True, suffixes = ("_from", "_to"))

    if not custom_dict:
        custom_dict = {name : None for name in InterfaceState.ParameterState.parameter_names}

    design_vectors = get_design_columns(df_combined.alpha_from, df_combined.delta_from, type)
    observation_vector = get_observation_vector(df_combined)

    #Subtract custom variables and delete those columns
    keys_to_delete = []
    for parameter, custom_value in custom_dict.items():
        if not custom_value is None:
            observation_vector = observation_vector - design_vectors[parameter] * custom_value
            keys_to_delete.append(parameter)
    for key in keys_to_delete:
        del design_vectors[key]         

    design_matrix = np.vstack(list(design_vectors.values())).T

    #Perform least square regression and return values in a dict
    uncertainties = {parameter : np.nan for parameter in custom_dict}
    if weighted:
        observation_var_matrix = get_var_matrix(df_combined)
        parameters, new_uncertainties = weighted_least_squares(design_matrix, observation_vector, observation_var_matrix)
        new_uncertainties = {parameter : sigma for parameter, sigma in zip(design_vectors, new_uncertainties)}
        uncertainties.update(new_uncertainties)
   
    else:
        parameters = ordinary_least_squares(design_matrix, observation_vector)

    parameters = {parameter : value for parameter, value in zip(design_vectors.keys(), parameters)}

    return parameters, uncertainties

def get_observation_vector(df: pd.DataFrame):
    """Creates an observation matrix for an OLS parameter fitting of a Icrf-transform"""
    observation_matrix = np.hstack(((df.alpha_from-df.alpha_to)*np.cos(df.delta_from), (df.delta_from-df.delta_to)))
    return observation_matrix
    
def get_design_columns(alpha, beta, type = "A"):
    if type == "A":
        return get_design_columns_A(alpha, beta)
    elif type == "B":
        return get_design_columns_B(alpha, beta)
    else:
        raise Exception("Unknown transform type")

def get_design_columns_A(alpha : pd.Series, delta: pd.Series):
    """Creates a design matrix for an OLS parameter fitting"""

    result = {"R1" : np.hstack((np.sin(delta)*np.cos(alpha),-np.sin(alpha))),
    "R2" : np.hstack((np.sin(delta) * np.sin(alpha),np.cos(alpha))),
    "R3" : np.hstack((-np.cos(delta),np.zeros(len(alpha.index)))),
    "D1" : np.hstack((-np.sin(alpha),-np.cos(alpha)*np.sin(delta))),
    "D2" : np.hstack((np.cos(alpha),-np.sin(alpha)*np.sin(delta))),
    "D3" : np.hstack((np.zeros(len(alpha.index)),np.cos(delta))),
    "M20" : np.hstack((np.sin(2*delta),np.zeros(len(alpha.index)))),
    "E20" : np.hstack((np.zeros(len(alpha.index)),np.sin(2*delta))),
    "E21 Re" : np.hstack((np.sin(alpha)*np.sin(delta),-np.cos(alpha)*np.cos(2*delta))),
    "E21 Im" : np.hstack((np.cos(alpha)*np.sin(delta),np.sin(alpha)*np.cos(2*delta))),
    "M21 Re" : np.hstack((-np.cos(alpha)*np.cos(2*delta),-np.sin(alpha)*np.sin(delta))),
    "M21 Im" : np.hstack((np.sin(alpha)*np.cos(2*delta),-np.cos(alpha)*np.sin(delta))),
    "E22 Re" : np.hstack((-2*np.sin(2*alpha)*np.cos(delta),-np.cos(2*alpha)*np.sin(2*delta))),
    "E22 Im" : np.hstack((-2*np.cos(2*alpha)*np.cos(delta),np.sin(2*alpha)*np.sin(2*delta))),
    "M22 Re" : np.hstack((-np.cos(2*alpha)*np.sin(2*delta),2*np.sin(2*alpha)*np.cos(delta))),
    "M22 Im" : np.hstack((np.sin(2*alpha)*np.sin(2*delta), 2*np.cos(2*alpha)*np.cos(delta)))}

    return result

def get_design_columns_B(alpha : pd.Series, delta: pd.Series):
    """Creates a design matrix for an OLS parameter fitting"""
    zero = np.zeros(len(alpha))
    one = np.ones(len(alpha))

    result = {"A1" : np.hstack((np.cos(alpha)*np.sin(delta), -np.sin(alpha))),
              "A2" : np.hstack((np.sin(alpha)*np.sin(delta), np.cos(alpha))),
              "A3" : np.hstack((-np.cos(delta), zero)),
              "D_alpha" : np.hstack((delta, zero)),
              "D_delta" : np.hstack((zero, delta)),
              "B_delta" : np.hstack((zero, one))}

    return result


def get_var_matrix(df: pd.DataFrame):
    """Creates a weight matrix for a WLS parameter fitting of a Helmert transform""" 
    var1 = df.alpha_sigma_from**2 + df.alpha_sigma_to**2
    var2 = df.delta_sigma_from**2 + df.delta_sigma_to**2 
    var = np.hstack([var1, var2])
    weight_matrix = np.diag(var)

    return weight_matrix

def icrf_transform(df: pd.DataFrame, parameters, type = "A"):
    """Returns a new dataframe with coordinates transformed according tp the Icrf transform"""
    design_columns = get_design_columns(df.alpha, df.delta, type)
    design_matrix = np.vstack(list(design_columns.values())).T
    parameters = np.array(list(parameters.values())).T
    n = len(df.alpha)
    
    alpha = df.alpha + (design_matrix[:n] @ parameters)/ np.cos(df.delta)    
    delta = df.delta + design_matrix[n:] @ parameters

    transformed_df = pd.DataFrame({"alpha": alpha, 
                                   "delta" : delta,
                                   "LONG" : df.LONG,
                                   "LAT" : df.LAT})

    return transformed_df

#RESIDUAL HANDLING FUNCTIONS-------------------------------------------------------------------------------------------------
def calculate_residuals(df_from: pd.DataFrame, df_to: pd.DataFrame):
    """Returns the from dataframe with computed residuals"""
    df_combined = pd.merge(df_from, df_to, how = "inner", left_index=True, right_index=True, suffixes = ("_from", "_to"))
    
    df_from["dAlpha"] = (df_combined.alpha_to-df_combined.alpha_from)*10**9
    df_from["dDelta"] = (df_combined.delta_to-df_combined.delta_from)*10**9

    return df_from


def ordinary_least_squares(design_matrix, observation_matrix, parameter_names = None):
    """Ordinary least squares fit"""
    parameters = np.linalg.inv(design_matrix.T @ design_matrix) @ design_matrix.T @ observation_matrix

    return parameters

def weighted_least_squares(design_matrix, observation_matrix, observation_var_matrix, parameter_names = None):
    """Weighted least squares fit under the assumption of uncorrelated measurement errors"""
    weight_matrix = np.linalg.inv(observation_var_matrix)

    parameter_uncertainties = np.linalg.inv(design_matrix.T @ weight_matrix @ design_matrix)
    parameters = parameter_uncertainties @ design_matrix.T @ weight_matrix @ observation_matrix
    parameter_uncertainties = np.sqrt(np.diag(parameter_uncertainties))

    return parameters, parameter_uncertainties

def r_squared(x, y, prediction_model):
    """R squared value of a fit of x to y with given parameters"""
    residuals = y - prediction_model(x) 
    y_mean = np.mean(y)
    ss_tot = sum(y - y_mean)
    ss_res = sum(residuals**2)
    r_squared = 1-ss_res/ss_tot

    return r_squared

def weighted_rms(x, y, y_var, prediction_model):
    """Weighted root mean squared of residuals of fit of x to y with given parameters and uncertainties"""
    residuals = y - prediction_model(x)
    weighted_sum = sum(residuals**2/y_var**2)
    weighted_normalisation = sum(1/y_var**2)
    weighted_rms = np.sqrt(weighted_sum/weighted_normalisation)

    return weighted_rms
