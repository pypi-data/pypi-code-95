import pandas as pd
import numpy as np 

from HelmertTool.io import calculate_long_lat
from HelmertTool.interface.InterfaceState import InterfaceState

def calculate_parameters(df_from: pd.DataFrame, df_to: pd.DataFrame, weighted: bool, type: str, custom_dict : dict = None):
    """Calculates Helmert parameters with the option of one, two, or three scale variables and a dict specifying values of parameters of which it should not calculate"""

    if not custom_dict:
        custom_dict = {name : None for name in InterfaceState.ParameterState.parameter_names}

    design_vectors = get_design_columns(df_from)
    observation_vector = get_observation_vector(df_from, df_to)

    #Subtract custom variables and delete those columns
    keys_to_delete = []
    for parameter, custom_value in custom_dict.items():
        if not custom_value is None:
            observation_vector = observation_vector - design_vectors[parameter] * custom_value
            keys_to_delete.append(parameter)
    for key in keys_to_delete:
        del design_vectors[key]

    #Merge columns and create final design matrix
    if type == "7" and "scale_x" in design_vectors:
        #Scale_x is really scale_xyz here
        design_vectors["scale_x"] = design_vectors["scale_x"] + design_vectors["scale_y"] + design_vectors["scale_z"]
        del design_vectors["scale_y"]        
        del design_vectors["scale_z"]        
    
    if type == "8" and "scale_x" in design_vectors:
        #Scale_x is really scale_xy here
        design_vectors["scale_x"] = design_vectors["scale_x"] + design_vectors["scale_y"]
        del design_vectors["scale_y"]              

    design_matrix = np.vstack(list(design_vectors.values())).T

    #Perform least square regression and return values in a dict
    uncertainties = {parameter : np.nan for parameter in custom_dict}
    if weighted:
        observation_var_matrix = get_var_matrix(df_from, df_to)
        parameters, new_uncertainties = weighted_least_squares(design_matrix, observation_vector, observation_var_matrix)
        new_uncertainties = {parameter : sigma for parameter, sigma in zip(design_vectors, new_uncertainties)}
        uncertainties.update(new_uncertainties)
   
    else:
        parameters = ordinary_least_squares(design_matrix, observation_vector)

    parameters = {parameter : value for parameter, value in zip(design_vectors.keys(), parameters)}

    return parameters, uncertainties

def get_observation_vector(df_from: pd.DataFrame, df_to: pd.DataFrame):
    """Creates an observation matrix for an OLS parameter fitting of a Helmert-transform"""
    observation_matrix = np.hstack((df_to.X-df_from.X, df_to.Y-df_from.Y, df_to.Z-df_from.Z))
    return observation_matrix
    
def get_design_columns(df: pd.DataFrame):
    """Creates a design matrix for an OLS parameter fitting of a Helmer transform with seven, eight, or nine parameters"""
    n = len(df.index)
    zero = np.zeros(n)
    one = np.ones(n)

    result = {"translation_x" : np.hstack((one, zero, zero)),
    "translation_y" : np.hstack((zero, one, zero)),
    "translation_z" : np.hstack((zero, zero, one)),
    "scale_x" : np.hstack((df.X, zero, zero)),
    "scale_y" : np.hstack((zero, df.Y, zero)),
    "scale_z" : np.hstack((zero, zero, df.Z)),
    "rotation_x" : np.hstack((zero, -df.Z, df.Y)),
    "rotation_y" : np.hstack((df.Z, zero, -df.X)),
    "rotation_z" : np.hstack((-df.Y, df.X, zero))}
        
    return result

def get_var_matrix(df_from: pd.DataFrame, df_to: pd.DataFrame):
    """Creates a weight matrix for a WLS parameter fitting of a Helmer transform""" 
    var1 = df_from.X_sigma**2 + df_to.X_sigma**2
    var2 = df_from.Y_sigma**2 + df_to.Y_sigma**2 
    var3 = df_from.Z_sigma**2 + df_to.Z_sigma**2 
    var = np.hstack([var1, var2, var3])

    # var = np.sqrt(df_from.X_sigma**2 + df_to.X_sigma**2 + df_from.Y_sigma**2 + df_to.Y_sigma**2 + df_from.Z_sigma**2 + df_to.Z_sigma**2) 
    # var = np.hstack([var, var, var])

    weight_matrix = np.diag(var)
    
    return weight_matrix

def helmert_transform(df: pd.DataFrame, parameters):
    """Returns a new dataframe with coordinates transformed according tp the helmert infinitecimal form"""
    X = np.vstack((df.X, df.Y, df.Z)) 
    
    if not "scale_y" in parameters:
        parameters["scale_y"] = parameters["scale_x"]
    if not "scale_z" in parameters:
        parameters["scale_z"] = parameters["scale_x"]
    
    translation = np.array([parameters["translation_x"],parameters["translation_y"],parameters["translation_z"]]).reshape(3,1)
    scale = np.array([parameters["scale_x"],parameters["scale_y"],parameters["scale_z"]]).reshape(3,1)
    rotation = np.array([parameters["rotation_x"],parameters["rotation_y"],parameters["rotation_z"]]).reshape(3,1)

    coords = X + translation + scale * X + np.cross(rotation, X, axis=0)
    transformed_df = pd.DataFrame({"X": coords[0,:], 
                                   "Y" : coords[1,:], 
                                   "Z" : coords[2,:], 
                                   "Station_Name" : df.Station_Name})

    transformed_df = calculate_long_lat(transformed_df)

    return transformed_df

def calculate_residuals(df_from: pd.DataFrame, df_to: pd.DataFrame):
    """Returns the from dataframe with computed residuals"""
    df_from["dX"] = df_from.X-df_to.X
    df_from["dY"] = df_from.Y-df_to.Y
    df_from["dZ"] = df_from.Z-df_to.Z

    return df_from

def decompose_residuals(df):
    """Returns the dataframe with residuals decomposed into U,E,N coordinates"""
    LONG = np.radians(df.LONG)
    LAT = np.radians(df.LAT)
    
    df["dU"] = np.cos(LAT)*np.cos(LONG)*df.dX + \
                np.cos(LAT)*np.sin(LONG)*df.dY + \
                np.sin(LAT)*df.dZ
    df["dE"] = -np.sin(LONG)*df.dX + \
                np.cos(LONG)*df.dY + \
             0
    df["dN"] = -np.sin(LAT)*np.cos(LONG)*df.dX + \
               -np.sin(LAT)*np.sin(LONG)*df.dY + \
               -(-np.cos(LAT)*np.cos(LONG)*np.cos(LONG)-np.cos(LAT)*np.sin(LONG)*np.sin(LONG))*df.dZ
    
    return df

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

