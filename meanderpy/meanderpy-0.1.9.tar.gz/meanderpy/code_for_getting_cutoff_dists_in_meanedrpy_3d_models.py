
cutoff_dists_all = np.nan * np.zeros((iheight,iwidth,n_steps))

 # setting sand thickness to zero at cutoff locations (fluvial):
if len(cutoff_ind)>0:
    cutoff_dists = 1e10*np.ones(np.shape(th)) #initialize cutoff_dists with a large number
    for j in range(len(cutoff_ind)):
        for k in range(len(cutoffs[int(cutoff_ind[j])].x)): # sometimes there is more than one cutoff in the same 'cutoffs' object
            cutoff_dist, cfx_pix, cfy_pix = cl_dist_map(cutoffs[int(cutoff_ind[j])].x[k], cutoffs[int(cutoff_ind[j])].y[k], 
                cutoffs[int(cutoff_ind[j])].z[k], xmin, xmax, ymin, ymax, dx)
            cutoff_dists = np.minimum(cutoff_dists,cutoff_dist)
    th[cutoff_dists < 0.9 * w/dx] = 0 # set point bar thickness to zero inside of oxbows
    if np.min(cutoff_dists) == 0:
        cutoff_dists_all[:,:,i] = cutoff_dists
        cutoff_levels[i] = np.min(z)

# setting sand thickness to zero at cutoff locations (submarine):
if len(cutoff_ind) > 0:
    cutoff_dists = 1e10 * np.ones(np.shape(th)) #initialize cutoff_dists with a large number
    for j in range(len(cutoff_ind)):
        for k in range(len(cutoffs[int(cutoff_ind[j])].x)): # sometimes there is more than one cutoff in the same 'cutoffs' object
            cutoff_dist, cfx_pix, cfy_pix = cl_dist_map(cutoffs[int(cutoff_ind[j])].x[k], cutoffs[int(cutoff_ind[j])].y[k], 
                cutoffs[int(cutoff_ind[j])].z[k], xmin, xmax, ymin, ymax, dx)
            cutoff_dists = np.minimum(cutoff_dists,cutoff_dist)
    # th[cutoff_dists < 0.9 * ws/dx] = 0 # set channel deposit thickness to zero inside of oxbows
    if np.min(cutoff_dists) == 0:
        cutoff_dists_all[:,:,i] = cutoff_dists
        cutoff_levels[i] = np.min(z)


def cl_dist_map(x,y,z,xmin,xmax,ymin,ymax,dx):
    """function for centerline rasterization and distance map calculation (does not return zmap)
    used for cutoffs only 
    inputs:
    x,y,z - coordinates of centerline
    xmin, xmax, ymin, ymax - x and y coordinates that define the area of interest
    dx - gridcell size (m)
    returns:
    cl_dist - distance map (distance from centerline)
    x_pix, y_pix, - x and y pixel coordinates of the centerline
    """
    y = y[(x>xmin) & (x<xmax)]
    z = z[(x>xmin) & (x<xmax)]
    x = x[(x>xmin) & (x<xmax)]    
    xdist = xmax - xmin
    ydist = ymax - ymin
    iwidth = int((xmax-xmin)/dx)
    iheight = int((ymax-ymin)/dx)
    xratio = iwidth/xdist
    # create list with pixel coordinates:
    pixels = []
    for i in range(0,len(x)):
        px = int(iwidth - (xmax - x[i]) * xratio)
        py = int(iheight - (ymax - y[i]) * xratio)
        pixels.append((px,py))
    # create image and numpy array:
    img = Image.new("RGB", (iwidth, iheight), "white")
    draw = ImageDraw.Draw(img)
    draw.line(pixels, fill="rgb(0, 0, 0)") # draw centerline as black line
    pix = np.array(img)
    cl = pix[:,:,0]
    cl[cl==255] = 1 # set background to 1 (centerline is 0)
    # calculate Euclidean distance map:
    cl_dist, inds = ndimage.distance_transform_edt(cl, return_indices=True)
    y_pix,x_pix = np.where(cl==0)
    return cl_dist, x_pix, y_pix