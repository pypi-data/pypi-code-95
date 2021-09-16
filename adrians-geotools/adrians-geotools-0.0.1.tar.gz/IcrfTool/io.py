import pandas as pd 
import numpy as np

def load_src_posn(fpath: str, epoch: float = 0):
    """Load a .sta ICRF file to a pandas dataframe"""
    columns = ["ICRF", "ICRF_Designation", "IERS_Destignation", "Defining_source", "Right_Ascension_h", "Right_Ascension_m", "Right_Ascension_s", "Declination_o", "Declination_prime", "Declination_bis", "Right_Ascention_Uncertainty_s", "Declination_Uncertainty_bis", "Correction", "Mean_MJD", "First_MJD", "Last_MJD", "Nb_sess", "Nb_del", "Nb_rat"]
    df = pd.read_fwf(fpath, skiprows = 23, header = None, names = columns)
    df = df[~df.Defining_source.isna()]
    
    index = df.IERS_Destignation
    df = pd.DataFrame(
    data =  {"alpha" : df.Right_Ascension_h * 2*np.pi/24 + df.Right_Ascension_m * 2*np.pi/(24*60) + df.Right_Ascension_s * 2*np.pi/(24*60*60), #radians
                "alpha_sigma" : df.Right_Ascention_Uncertainty_s * 360/(24*60*60),                                                                #degrees
                "delta" : df.Declination_o * 2*np.pi/360 + df.Declination_prime * 2*np.pi/(360*60) + df.Declination_bis * 2*np.pi/(360*60*60),    #radians
                "delta_sigma" : df.Declination_Uncertainty_bis * 1/(60*60)})                                                                      #degrees
    df.index = index    

    df = calculate_long_lat(df)
    return df

def calculate_long_lat(df: pd.DataFrame):
    df["LAT"] = np.mod(np.degrees(df.alpha) + 180, 360) - 180
    df["LONG"] = np.degrees(df.delta)

    return df 

def timestamp_to_year(timestamp):
    jd = pd.DatetimeIndex(timestamp).to_julian_date()
    jd2000 = pd.Timestamp(year=2000, month=1, day=1).to_julian_date()
    year = (jd - jd2000)/365.25 + 2000

    return year