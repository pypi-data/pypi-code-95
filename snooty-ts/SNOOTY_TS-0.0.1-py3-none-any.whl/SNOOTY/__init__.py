"""
Python package `SNOOTY`: smoothing and evaluation for data analysis.

"""

import rpy2.robjects.numpy2ri as numpy2ri
import rpy2.robjects. pandas2ri as pandas2ri
from rpy2.robjects.packages import STAP
import rpy2.robjects as ro
import pandas as pd

def smooth(data, smooth_size, before, after):
    """
    
    Each column is used to calculate a smooth value using the slide_index_dbl from R language. After that it's made a time dependent linear interpolation applied to all columns
    
    Parameters
    ----------
    data --> dataframe which needs a time column and at least another column to be smoothed.
    

    before, afeter --> represents the number of values before or after the current cell to include in the sliding window.

    smooth size --> it's the interval's size between two consecutive cells. This value refers to some variable chosen as a reference, in this case, we've chosen time.


    """
    r_function_str = """

    smooth <- function(data, smooth_size, before, after) {

        suppressMessages(library(tidyverse))
        suppressMessages(library(slider))

        ntime <- seq(min(data$time), max(data$time), by = smooth_size)
        ndata <- tibble(time = ntime)
        names <- colnames(data)
        names <- names[names != 'time']


        for(name in names){
        #Smooth the data:
            smooth <- slide_index_dbl(data[[name]], data$time, mean, .before = before, .after = after)
            ndata <- ndata %>% mutate( "{name}" := approx(data$time, smooth, ntime)$y)
        }

     
        colnames(ndata) <- c("time", names)

        return(ndata)
}


"""
    r_pkg = STAP(r_function_str, "r_pkg")
    pandas2ri.activate()
    datapandas = r_pkg.smooth(data, smooth_size, before, after)

    return datapandas

def mean_squared_error(pd_series, reference_value):
    ''' 
    This function calculates the mean squared error of the pandas.Series
    data 'pd_series' and returns a float as result. The calculation is 
    sum((pd_series[i] - reference_value)^2)/pd_series.size. If 'pd_series' is
    empty, this function returns None. The type of the elements of pd_series must be
    int or float. If pd_series is empty, this function returns None.
    
    Input:
        pd_series       --> pd.Series
        reference_value --> float
    
    Output:
        result --> float
    '''
    error_result = {'pd_series':False, 'reference_value':False}
    #Check if pd_series has type pd.Series:
    if not isinstance(pd_series, (pd.core.series.Series)):
        error_result['pd_series'] = True

    #Check if reference_value is float or integer:
    if not (isinstance(reference_value, (float, int))):
        error_result['reference_value'] = True

    #Raise exception if necessary:
    if all(error_result.values()):
        raise TypeError("'pd_series' must be a pandas.Series, and reference_value must be a float or an int")
    elif error_result['pd_series']:
        raise TypeError("'pd_series' must be a pandas.Series")
    elif error_result['reference_value']:
        raise TypeError("reference_value must be a float or an int")

    #Check if pd_series is empty:
    if pd_series.size == 0:
        return None

    #Calculate the mean squared error:
    error         = pd_series - reference_value
    squared_error = pow(error, 2)
    mean_squared_error_value = sum(squared_error)/pd_series.size

    #Return the result:
    return mean_squared_error_value

def mean(row, rolling_array, window_in, *kwargs):
    row['mean'.format(window_in)] = rolling_array.mean()

def median(row, rolling_array, window_in, *args):
    row['median'.format(window_in)] = rolling_array.quantile(0.5)

def first_quartile(row, rolling_array, window_in, *args):
    row['1rst_quartile'.format(window_in)] = rolling_array.quantile(0.25)

def third_quartile(row, rolling_array, window_in, *args):
    row['3rd_quartile'.format(window_in)] = rolling_array.quantile(0.75)

def max_function(row, rolling_array, window_in, *args):
    row['max'.format(window_in)]  = rolling_array.max()

def min_function(row, rolling_array, window_in, *args):
    row['min'.format(window_in)]  = rolling_array.min()

def mse_value(row, rolling_array, window_in, mean_squared_error_value):
    row['mean_squared_error'] = mean_squared_error_value

def evaluate(pd_series, reference_value, window_in, evaluate_op):
    """
        evaluate(pd_series (Data Series), reference_value (float), window_in (float), evaluate_op (float))

        The function receives a Data Series, a reference value for calculate the mean square error and a windowing size. Then you can select what operation it is desired to be returned.

        pd_series = Pandas Series
        reverence_value = a reference float value for mean square error and others operations

        window_in = windowing float size

        evaluate_op = list that selects which operation should be returned
                possible values: 
                                mean, 1q, 3q, max, min, mse
                                1q = first quartile
                                3q = third quartile
                                mse = mean square error
    """



    mean_squared_error_value = mean_squared_error(pd_series, reference_value) #np_array, reference_value)
    rolling_array = pd_series.rolling(window_in).apply(mean_squared_error, raw=False, args=(reference_value,))

    row = {}
    functions_dic = {
        'mean': mean,
        '1q'  : first_quartile,
        '3q'  : third_quartile,
        'max' : max_function,
        'min' : min_function,
        'mse' : mse_value
    }

    for op in evaluate_op:
        functions_dic[op](row, rolling_array, window_in, mean_squared_error_value)

    return row
