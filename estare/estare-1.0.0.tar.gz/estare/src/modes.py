"""This module should be imported by the entry-point script.

It implements the functions scan() and assemble(). The former 
is used for detecting features that are suitable for aligning 
two images. The latter proceeds to the alignment and stacking 
steps.
"""

from estare.src.align import align
from estare.src.init import examine, setup

from matplotlib import pyplot as plt
from skimage.io import imsave

import os
import numpy as np


def scan(args):
    """Finds features that are suitable for aligning two images.

    This function shows the input image in a graph first. It then 
    goes through every pixel of it and compares its brightness with 
    a given threshold (kapa) specified by the user. If the pixel's 
    brightness is higher than or equal to the threshold, a marker 
    will be shown on that location in the graph and the user can 
    accept it as a feature by pressing any key. The pixel can 
    alternatively be discarded by a left click.

    Args:
        args : user inputs parsed by argparse
    """
    
    # handle input arguments
    image1_path = args.img1
    image2_path = args.img2
    
    info_only = args.info_only   # just check image properties and skip feature detection
    save_pixs = args.save_pxs    # save also the pixel values
    save_gifs = args.save_gif    # save the features as PNG too
    
    if (info_only):   #TODO: this feature should have a separate argument subparser
        img_as_array, x_range, y_range = examine(image1_path, verbose=True, graphics=False)
        img_as_array, x_range, y_range = examine(image2_path, verbose=True, graphics=False)
        return 
    else:
        setup()   # setup the program directory structure
        img1_as_array, x_range, y_range = examine(image1_path, verbose=False, graphics=False)
        img2_as_array, x_range, y_range = examine(image2_path, verbose=False, graphics=False)
    # Replace with:
    # img_as_array = FloatImage(imagePath)
    # img_as_array.print_info()
    # img_as_array.save()
    # x_range, y_range = img_as_array.size()

    img1_gray = img1_as_array @ [0.2126, 0.7152, 0.0722]  # image in grayscale
    img2_gray = img2_as_array @ [0.2126, 0.7152, 0.0722]  
        
    # Replace with (makes FloatImage redundant):
    # imgGray = GrayImage(imagePath)
    # imgGray.print_info()
    # imgGray.save()
    # x_range, y_range = imgGray.size()

    fig2, (frame1,frame2) = plt.subplots(1, 2)
    image_features = frame1.imshow(img1_gray, cmap='gray')
    image_features = frame2.imshow(img2_gray, cmap='gray')
    selection_guide = '''Please first select two features from the left panel via left-click, and then pick their 
    counterparts (in the same order) from the right panel. Right-click to drop the latest selection. To interrupt 
    feature selection, use the middle mouse button.'''
    selection_warning='''Warning: zooming in can increase the accuracy of selection, but by doing this an 
    unwanted feature may be picked due to the mouse click action. In this case, right-click immediately after 
    zooming in to remove the unwanted selection.'''
    
    frame1.set_title(selection_guide)    
    frame2.set_title(selection_warning)
    
    plt.waitforbuttonpress(-1)
    coordinates = plt.ginput(n=4, timeout=-1, show_clicks=True)
    if len(coordinates) != 4:
        print('Feature detection incomplete. Please retry.')
    else:
        pivot_1 = [coordinates[0], coordinates[1]]
        pivot_2 = [coordinates[2], coordinates[3]]
        np.save('./estare_data/features/coordinates/pivot_1.npy', pivot_1)
        np.save('./estare_data/features/coordinates/pivot_2.npy', pivot_2)
        print('Feature detection completed.')



def assemble(args):
    """unpacks input arguments, then passes them to align() 

    This function prepares the input arguments to be passed to align() 
    for the algorithm to proceed to alignment and then stacking steps.

    Args:
        args : input arguments parsed by argparse
    """

    # TODO: design a stack-only mode that bypasses alignment
    
    # unpack the arguments
    img_1 = args.layer_1
    img_2 = args.layer_2
    pivot_1 = args.feature_1
    pivot_2 = args.feature_2

    # align and stack the two input frames
    stacked_frame = align(img_1, img_2, pivot_1, pivot_2, save=True)
    
