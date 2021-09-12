import numpy as np


def reference_markers():

    """Returns two pairs of coordinates: 
          targets: these are two reference points
          markers: these are in fact the targets that have been 
                   shifted and rotated. The aim would be to 
                   reverse the effect of the shift and rotation
                   and bring the marker coordinates back to the 
                   target coordinates.
    """
    
    # targets are the original coordinates
    targets = np.array([[1953, 1270],
                       [2087, 1289]])

    # markers include offsets and rotation 
    markers = np.array([[1969, 1281],
                       [2102, 1301]])

    return targets, markers
