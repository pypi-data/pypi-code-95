# Copyright (c) 2016 Barcelona Supercomputing Center

# @license: https://www.gnu.org/licenses/gpl-3.0.html
# @author: see AUTHORS file

# OPTIONS

"""
### GENERAL ###
srcfile: source file(s) (mandatory)
srcvar: source variable(s) (mandatory)
indir: input directoty (default '.')
outdir: output directory (default '.')
srcgap: source time gap(s) (default empty)
title: parametric title (default empty)
dpi: dot per inch (default system)
img_template: template for the output images
joint_template: template for the output joint image
aspect: if False do not keep original proportion by default (default True)
xsize: when aspect is False set the horizontal size between 0 and 1
ysize: when aspect is False set the vertical size between 0 and 1
transf: transformation if longitude in 0-360 format (default -180 180)
scatter: path of a csv file with station data (datetime, lat, lon, value)
logo: put a logo on the image (filename, x, y) (default None)
overwrite: overwrite existing filename(s) (default True)
anim: animation (default False)
total:
interval:
freq:

### MAPS and CROSS SECTIONS ###
bounds: value bounds (default auto)
boundaries:
colors: color/colormap (default 'jet')
over: sup saturation color
under: inf saturation color
wind: wind source file(s)
windopts: wind options (u, v, skip, barbs)
varconds: var conditions for accumulation operations
lat: latitude (min, max, int) (default auto)
lon: longitude (min, max, int) (default auto)
contours: (not filled) contours variable
contours_color: contours color
contours_label: contours label
contours_int: contours interval
nointerp: plot pixels instead of contours
colorbar: show/hide the colorbar (default True)
noruntime: hide model runtime in the title
tsteps: list of timesteps to plot (default empty)
limits: draw limits arrows on the colorbar

### MAPS ###
area_thresh: area threshold for map (default None)
shapefiles: additional shapefile(s) to plot
nocontourf: don't plot contourf
max: generate max image(s) (default False)
maxtitle: max image(s) title (default None)
nomap: don't plot the map (default False)
resolution: map resolution ('c','i','h','f') (default i)
drawopts: drawing list (countries, coastlines, states) (default coastlines)
background: use a map background or GIS (default False)
kml: generate kml (default False)
kmz: generate kmz (default False)

### CROSS SECTIONS ###

### TIME SERIES ###
"""


#from mapgenerator.plotting import plotmap
#from mapgenerator.plotting import cross
#from mapgenerator.plotting import tseries
