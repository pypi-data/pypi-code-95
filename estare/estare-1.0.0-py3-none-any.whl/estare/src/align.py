from skimage import io
from skimage import img_as_float as imfloat
import numpy as np
from matplotlib import pyplot as plt

from estare.src.init import examine
from estare.src.rotate import rotate, rotate_vectorized
from estare.src.stack import stack

# +++++++++++++
# For profiling
import time


# Fine-tuning
# - pick features from scattered regions
# - characterize error: does it vary if one goes towards the edges or far from the origin?
# - compare light curves and make adjustments if the stacked feature deviates too much


def detrans(x_array, y_array, x_range, y_range, del_x, del_y):

    """Corrects the effect of translation by removing the extent by which each point 
    had been shifted, i.e. del_x, and del_y.

    Args:
    x_array
    y_array
    x_range
    y_range
    del_x
    del_y

    Returns:
    x_array
    y_array

    """
    
    for i in range(x_range):
        x_array[i, :] = i-del_x

    for j in range(y_range):
        y_array[:, j] = j-del_y
   
    
    return x_array, y_array



def detrans_scalar(x_array, y_array, x_range, y_range, del_x, del_y):
    
    for i in range(x_range):
        for j in range(y_range):
            x_array[i, j] = i-del_x
            y_array[i, j] = j-del_y
            
    
    return x_array, y_array



def find_offset(pivot_1, pivot_2):
    # two reference points for alignment
    coord_1 = np.load(pivot_1)
    a_1 = coord_1[0]
    b_1 = coord_1[1]
    
    # two target points that should match the reference points after alignment
    coord_2 = np.load(pivot_2)  
    a_2 = coord_2[0]
    b_2 = coord_2[1]

    # Use the two points to back calculate the angle of rotation
    slope_bef = ( b_1[1] - a_1[1] )/( b_1[0] - a_1[0] )
    
    slope_aft = ( b_2[1] - a_2[1] )/( b_2[0] - a_2[0] )

    deflection = ( ((np.arctan(slope_aft))*180/np.pi) -
              ( (np.arctan(slope_bef))*180/np.pi ) )

    a2_derot = rotate(a_2, -deflection, discrete=False)   # set discrete=False to get an exact value

    # compare the derotated one from its origin to calculate the relative translation magnitude 
    dxp = a2_derot[0] - a_1[0]
    dyp = a2_derot[1] - a_1[1]

    # Using the formulae, compute the absolute translation magnitude
    deflection_rad = -deflection * np.pi / 180   # radians

    del_y = ( dyp - dxp*np.tan(deflection_rad) ) / \
            (np.sin(deflection_rad)*np.tan(deflection_rad) + np.cos(deflection_rad))

    del_x = (dxp + del_y*np.sin(deflection_rad)) / np.cos(deflection_rad)


    return del_x, del_y, deflection, deflection_rad



def derotate(x_array, y_array, theta, roundup=False):
    """Removes the effect of rotation
    """

    x_range_1 = np.shape(x_array)[0]
    y_range_1 = np.shape(x_array)[1]
    
    for i in range(x_range_1):
        for j in range(y_range_1):
            uncorrected_coor = [x_array[i, j], y_array[i, j]]
            corrected_coor = rotate(uncorrected_coor, -theta, discrete=roundup)
            
            x_array[i, j] = corrected_coor[0]
            y_array[i, j] = corrected_coor[1]

    return x_array, y_array

                
def align(image_1, image_2, pivot_1, pivot_2, save=False):
    print('Working... this can take several minutes')
    #TODO: remove the save option. You always wanna save the result!
    img_1, x_range_1, y_range_1 = examine(image_1)  
    img_2, x_range_2, y_range_2 = examine(image_2)

    # if (x_range_1 != x_range_2) or (y_range_1 != y_range_2):
    #     #TODO: raise error and exit


    # calculate offsets (del_x, del_y) and rotation angle theta
    del_x, del_y, theta, theta_rad = find_offset(pivot_1, pivot_2)
    
    # Allocate x- and y-array for holding the new coordinates after offseting
    x_array = np.zeros((x_range_1, y_range_1, 1), dtype=int)
    y_array = np.zeros((x_range_1, y_range_1, 1), dtype=int)

    # For the two following time-consuming loops, we need unit tests to ensure the correctness after each optimization:
    # Now we can detranslate all points
    t_1 = time.time()

    x_array, y_array = detrans(x_array, y_array, x_range_1, y_range_1, del_x, del_y)

    t_2 = time.time()
    # and now we can derotate them using the vectorized version:
    stack(img_1, img_2, x_array, y_array, x_range_1, y_range_1, theta, discrete=True)
    t_3 = time.time()
    #TODO: configure profiling run separately from production
    #print('De-translation took %s sec.'%(t_2-t_1))
    #print('Stacking took %s sec.'%(t_3-t_2))    

    if save:
        io.imsave('./estare_data/stacked_images/estare_stacked_result.jpg', img_1)
        print('Finished. The result is saved as estare_stacked_result.jpg under ./estare_data/stacked_images/')
    
    return img_1
    




if __name__ == '__main__':

    x_range = 400; y_range = 600
    
    x_array = np.zeros((x_range, y_range, 1), dtype=float)
    y_array = np.zeros((x_range, y_range, 1), dtype=float)

    del_x = 0.1; del_y = 0.2

    
    t_1 = time.time()
    for t in range(10):
        x_array, y_array = detrans(x_array, y_array, x_range, y_range, del_x, del_y)
            
    t_2 = time.time()

    print('De-translation took %s sec.'%(t_2-t_1))

    
    t_1 = time.time()
    for t in range(10):
        x_array, y_array = detrans_scalar(x_array, y_array, x_range, y_range, del_x, del_y)
            
    t_2 = time.time()

    print('De-translation (scal. version) took %s sec.'%(t_2-t_1))


    
