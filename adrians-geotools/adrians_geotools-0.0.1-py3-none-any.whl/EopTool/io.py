""" Eop I/O 

This modules contains all methods for importing eop-data and exporting results.

The public functions available in this module are

    *load - returns a pandas dataframe with the . Currently supported formats are .fil, .eob and .eop.
    *to_string - returns a nicely formated string with info about the supplied data.
    *export - saves a file with info about the supplied data.
"""

import os 
import pandas as pd
import numpy as np 


def load(fpath: str)-> pd.DataFrame:
    """Loads a eop data file from the file path into a pandas dataframe.
    
    Currently it supports the file formats .fil, .eob and .eop which yield the columns 
        X, X_SIGMA, Y, Y_SIGMA, UT1, UT1_SIGMA 

    and an index given in continous year. This is an approximative value derived from the modified julian date as
        (MJD - MJD_2000)/365.25 + 2000

    where MJD_2000 is the modified julian date of 01/01/2000. 
    """

    name, extension = os.path.splitext(fpath)

    if (extension == ".fil"):
        df = __load_fil(fpath)
    elif (extension == ".eob"):
        df = __load_eob(fpath)
    elif (extension == ".eop"):
        df = __load_eop(fpath)
    elif (extension == ".txt"):
        df = __load_txt(fpath)
    else:
        raise Exception("File format not supported")
    
    return df 

def to_string(df, parameters, sigmas):

    transformation = [name for name in sigmas.keys()]
    values = [parameters[name].get() for name in sigmas.keys()]
    sigmas = [sigmas[name].get() for name in sigmas.keys()]
    parameter_df = pd.DataFrame({"transformation" : transformation, "values" : values, "sigmas" : sigmas})

    string = f"""Begin Transform
{parameter_df.to_string(index=False)}

End Transform
---
Begin Residuals
{df.to_string(index=False)}
End Residuals
"""
    return string

def export():
    pass

def __clean_df(df):
    """Datahandling common to all load functions"""

    mjd_2000 = pd.Timestamp(year=2000, month=1, day=1).to_julian_date() - 2400000.5
    df = df[["X", "X_SIGMA", "Y", "Y_SIGMA", "UT1", "UT1_SIGMA"]]
    df = df.dropna()
    df = df[~df.index.duplicated()]
    df.index = (df.index - mjd_2000)/365.25 + 2000
    df = df.sort_index()
    
    df["UT1"] = df["UT1"]
    df["UT1_SIGMA"] = df["UT1_SIGMA"]

    return df

def __load_txt(fpath: str) -> pd.DataFrame:
    """Load a .txt into a pandas dataframe"""
    TXT_COLUMN_NAMES = ["Date_year", "Date_month", "Date_day", "MJD", "X", "Y", "UT1", "LOD", "dX", "dY", "X_SIGMA", "Y_SIGMA", "UT1_SIGMA", "LOD Err", "dX Err", "dY Err"]  
    df = pd.read_fwf(fpath, names = TXT_COLUMN_NAMES, engine = 'python', skiprows = 14, infer_nrows=300)
    df = df.set_index("MJD")

    leapsecond_df = __load_leapseconds(get_path("ut1ls.dat"))
    df = df.join(leapsecond_df["TAI_UTC"], how="outer")
    df["TAI_UTC"] = df["TAI_UTC"].ffill()
    df["UT1"] = df["UT1"] - df["TAI_UTC"]

    return __clean_df(df)

def __load_fil(fpath : str) -> pd.DataFrame:
    """Load a .fil into a pandas dataframe"""

    leapsecond_df = __load_leapseconds(get_path("ut1ls.dat"))
    FIL_COLUMN_NAMES = ["MJD", "X", "X_SIGMA", "Y", "Y_SIGMA", "UT1_SHORT", "UT1_SIGMA"]
    FIL_COLUMN_SPECS = [(7, 15), (18,27), (28, 36), (36,46), (47,57), (58,69), (70,79)]
    
    df = pd.read_fwf(fpath, colspecs=FIL_COLUMN_SPECS, names = FIL_COLUMN_NAMES, engine='python')
    df = df.set_index("MJD")
    df = df.join(leapsecond_df["TAI_UTC"], how="outer")
    df["TAI_UTC"] = df["TAI_UTC"].ffill()
    df["UT1"] = df["UT1_SHORT"] - df["TAI_UTC"]

    return __clean_df(df)

def __load_eob(fpath: str) -> pd.DataFrame:
    EOB_COLUMN_NAMES = ["MJD", "X","Y", "UT1", "X_NUT", "Y_NUT", "X_RATE", "Y_RATE", "UT1_RATE", "X_SIGMA","Y_SIGMA", "UT1_SIGMA", "X_NUT_SIGMA", "Y_NUT_UNC", "X_RATE_SIGMA", "Y_RATE_SIGMA", "UT1_RATE_SIGMA"]
    EOB_COLUMN_NUMBERS = [0, 2,3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,16, 17]

    df = pd.read_csv(fpath, sep=" +", comment="#", usecols = EOB_COLUMN_NUMBERS, names = EOB_COLUMN_NAMES, engine='python')
    df = df.set_index("MJD")

    return __clean_df(df)

def __load_eop(fpath: str):
    EOP_COLUMN_NAMES = ["EOP_LOC", "EOP_LOC_NUM", "TAG", "USED", "X", "X_SIGMA", "Y", "Y_SIGMA", "UT1", "UT1_SIGMA", "X_RATE", "X_RATE_SIGMA", "Y_RATE", "Y_RATE_SIGMA", "UT1_RATE", "UT1_RATE_SIGMA"] 
    EOP_COLUMN_NUMBERS = [1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]

    df = pd.read_csv(fpath, sep=" +", comment="#", usecols=EOP_COLUMN_NUMBERS, names = EOP_COLUMN_NAMES, engine='python')
    df['TAG'] = pd.to_datetime(df['TAG'], format='%Y.%m.%d-%H:%M')
    df['MJD'] = pd.DatetimeIndex(df['TAG']).to_julian_date() - 2400000.5
    df = df.set_index("MJD")
    
    for column_name in ["X", "Y", "UT1"]:
        df[column_name] = df[column_name].astype(np.float64)
        df[column_name] = df[column_name]/10**3

    for column_name in ["X_SIGMA", "Y_SIGMA", "UT1_SIGMA"]:
        df[column_name] = df[column_name].astype(np.float64)
        df[column_name] = df[column_name]/10**6

    return __clean_df(df)

def __load_leapseconds(file: str) -> pd.DataFrame:
    """Load ut1ls.dat file into a pandas dataframe and calculate TAI_UTC"""

    UT1LS_COLUMN_NAMES = ["YEAR", "MONTH", "JD", "C1", "C2", "C3"]
    UT1LS_COLUMN_NUMBERS = [0, 1, 4, 6, 11, 13]

    ut1ls_df = pd.read_csv(file, sep=" +", comment="#", usecols=UT1LS_COLUMN_NUMBERS, names = UT1LS_COLUMN_NAMES, engine='python')
    ut1ls_df['C2'] = ut1ls_df["C2"].replace("[^0-9.]", "", regex=True).astype("float")
    ut1ls_df['C3'] = ut1ls_df["C3"].replace("[^0-9.]", "", regex=True).astype("float")

    ut1ls_df["MJD"] = ut1ls_df["JD"] - 2400000.5
    ut1ls_df["TAI_UTC"] = ut1ls_df["C1"] + (ut1ls_df["MJD"] - ut1ls_df["C2"] ) *  ut1ls_df["C3"] 
    ut1ls_df = ut1ls_df.set_index("MJD")
    
    return ut1ls_df[["TAI_UTC"]].sort_index()

def get_path(file_name):
    """Checks for the specified file. If it exists in the current working directory it returns that path, else the default path"""
    default_path, _ = os.path.split(__file__)
    default_file = os.path.join(default_path, "resources", file_name)

    working_path = os.getcwd()
    working_file = os.path.join(working_path, file_name)

    if os.path.exists(working_file):
        return working_file
    else:
        return default_file 