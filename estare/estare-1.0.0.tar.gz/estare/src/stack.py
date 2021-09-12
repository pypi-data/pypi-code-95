
import numpy as np
from estare.src.rotate import rotate_vectorized


def stack(img_1, img_2, x_array, y_array, x_range, y_range, deflection, discrete=True):
    """ theta was changed to deflection
    """
    
    ###angle_matrix = np.load('../aux/angle_table.npy')
    ###norm_matrix  = np.load('../aux/norm_matrix.npy')
    ###rho = norm_matrix[i, j]
    ###theta = angle_matrix[i, j]
    
    x_corrected, y_corrected = rotate_vectorized(x_array, y_array, -deflection, origo=np.array([0., 0.]), radians=False, discrete=discrete)
    
    for i in range(x_range):
        for j in range(y_range):
            # stack needs unittesting if the stacking algorithm is to be changed+
            #if x_array[i, j] > 0 and x_array[i, j] < x_range and y_array[i, j] > 0 and y_array[i, j] < y_range:
            #    img_1[x_array[i, j], y_array[i, j]] += img_2[i, j]   # Broadcasting to all three channels is implicit
            # Can this be vectorized too?    
            if (x_corrected[i,j] > 0) and (x_corrected[i,j] < x_range) and (y_corrected[i,j] > 0) and (y_corrected[i,j] < y_range):
                img_1[int(x_corrected[i,j]), int(y_corrected[i,j])] += img_2[i, j]   # Broadcasting to all three channels is implicit

    return img_1
                
            
