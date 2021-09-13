import numpy as np

def mean_squared_error(y_real, y_pred):
    y_real = np.array(y_real)
    y_pred = np.array(y_pred)
    
    return np.mean((y_real - y_pred)**2)