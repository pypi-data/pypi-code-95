
import numpy as np



'''
We have:
- a function to calculate angle recieves a reference(default 0, 0) and a feature coordinate
- a function that takes an angle and a pair of coordinates and rotates the point (below)
- a function that takes [del_x, del_y] and a pair of coordinates and translates the point (below)

--------------->  Y
|*
| *
|  *
|   *
|
v

X

'''

# @profile
# def arc(position, origo=np.array([0., 0.]), radians=False):
#     '''
# Returns the angle between the input coordinate and the vertical axis Y
# '''
#     rho = np.sqrt( (position[0]-origo[0])**2 + (position[1]-origo[1])**2 )
#     angle = np.arccos( (position[0]-origo[0]) / rho )
    
#     if radians==False:
#         angle = angle*180.0/np.pi
        
#     return angle

def arc(position, origo=np.array([0., 0.]), radians=False):
    """Returns the angle between the input coordinate and the vertical 
       axis Y using the projection principle
    """

    #TODO: position[0,0] or generally position=origin should raise error
    # in fact division by rho = 0 should raise error
    position_norm = np.sqrt((position[0]-origo[0])**2 + (position[1]-origo[1])**2)
    # computing norm via np.linalg.norm(position) is much slower
    if radians==False:
        return position_norm, 180.0 * (np.arccos( (position[0]-origo[0]) / position_norm )) / np.pi
    else:
        return position_norm, np.arccos( (position[0]-origo[0]) / position_norm )

    
#@profile
def arc_vectorized(x_array, y_array, origo=np.array([0., 0.]), radians=False):
    """Returns the angle between the input coordinate and the vertical 
       axis Y using the projection principle
    """

    #TODO: position[0,0] or generally position=origin should raise error
    # in fact division by rho = 0 should raise error
    position_norm = np.sqrt((x_array-origo[0])**2 + (y_array-origo[1])**2)
    # computing norm via np.linalg.norm(position) is much slower
    if radians==False:
        return position_norm, ( (180.0/np.pi) * (np.arccos( (x_array-origo[0]) / position_norm )) )
    else:
        return position_norm, np.arccos( (x_array-origo[0]) / position_norm )

    
# apply rotation
#@profile
def rotate_vectorized(x_array, y_array, deflection, origo=np.array([0., 0.]), radians=False, discrete=True):
   """
   #TODO: position [0,0] cannot be rotated
   Change log:

   28/03/2021
   rho (which stands for 2-norm of the position vector) now comes directly from arc()
    
   02/04/2021
   rho and deflection are pre-stored in a look-up table, which means that they just need to
   be loaded

   11/09/2021 A vectorized version of arc() and rotate() is implemented
   """
   rho, theta = arc_vectorized(x_array, y_array, radians=radians)
   theta += deflection
   #theta = deflection + arc(position, radians=radians)

   # Use the compiled version of arc():
   # theta = deflection + calculate.get_angle(position, radians=radians)

   if radians==False:
       theta = theta*(np.pi/180.0)   

       # rho now comes directly from arc()
       #rho = np.sqrt((position[0]-origo[0])**2 + (position[1]-origo[1])**2)
    
   x = rho*np.cos(theta)
   y = rho*np.sin(theta)

   if discrete:
       rotated_x = np.rint(x)
       rotated_y = np.rint(y)     
       #        return  int(rotated_x), int(rotated_y)
       return  rotated_x, rotated_y
   else:
       return  x, y

    

def rotate(position, deflection, origo=np.array([0., 0.]), radians=False, discrete=True):
    """
    #TODO: position [0,0] cannot be rotated
    Change log:
    28/03/2021
    rho (which stands for 2-norm of the position vector) now comes directly from arc()
    
    02/04/2021
    rho and deflection are pre-stored in a look-up table, which means that they just need to
    be loaded
    """
    rho, theta = arc(position, radians=radians)
    theta += deflection
    #theta = deflection + arc(position, radians=radians)

    # Use the compiled version of arc():
    # theta = deflection + calculate.get_angle(position, radians=radians)

    if radians==False:
        theta = theta*(np.pi/180.0)   

    # rho now comes directly from arc()
    #rho = np.sqrt((position[0]-origo[0])**2 + (position[1]-origo[1])**2)
    
    x = rho*np.cos(theta)
    y = rho*np.sin(theta)

    if discrete:
        rotated_position = np.rint([x, y])     
        return np.array( [int(rotated_position[0]), int(rotated_position[1])] )
    else:
        return np.array( [x, y] )
    



