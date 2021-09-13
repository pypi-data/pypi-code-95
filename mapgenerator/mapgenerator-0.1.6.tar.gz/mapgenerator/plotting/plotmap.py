# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 Barcelona Supercomputing Center
# @license: https://www.gnu.org/licenses/gpl-3.0.html
# @author: see AUTHORS file


import matplotlib as mpl
mpl.use('Qt5Agg')

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.cbook import delete_masked_points
from matplotlib.image import imread
import numpy as np
from datetime import datetime
#from datetime import timedelta
#import time
import os.path
import subprocess
#import sys
from collections import Iterable
from PIL import Image
#from mapgenerator.plotting.mapgenerator import MapCross
#from mapgenerator.plotting.mapgenerator import MapDrawOptions
#from mapgenerator.plotting.mapgenerator import MapDataHandler
from .definitions import MapData
from .definitions import MapCross
from .definitions import MapDrawOptions
from .definitions import MapDataHandler
from .definitions import DataFrameHandler
from .definitions import is_grid_regular
from .definitions import do_interpolation
from .definitions import parse_parameter
from .definitions import parse_parameters
from .definitions import parse_parameters_list
from .definitions import parse_path
from urllib.request import urlopen
import copy
from glob import glob

import logging

#logging.basicConfig(level=logging.WARNING)
log = logging.getLogger(__name__)


class PlotSeries():
    """ Main class for plotting time series """

    def __init__(self, loglevel='WARNING', **kwargs):
        pass


class PlotCross():
    """ Main class for plotting cross sections """

    def __init__(self, loglevel='WARNING', **kwargs):
        pass


class PlotMap(MapCross, MapDrawOptions):
    """ Main class for plotting maps """

    def __init__(self, loglevel='DEBUG', **kwargs):
        """ Initialize class with attributes """
        MapCross.__init__(self, loglevel, **kwargs)
        MapDrawOptions.__init__(self, loglevel, **kwargs)
        self.nocontourf = False
        self.maxdata = False
        self.maxtitle = None
        self.nomap = False
        self.background = False
        self.extend = 'neither'
        self.kml = False
        self.kmz = False
        self.norm = None
        self.cmap = None
        #self.formats = None
        self.map = None   #Map
        #self.first_image = True # Is is the first image of the batch?
        self.mapName = None # name of the figure to map animation colors
#        self.drawopts = {'coastlines':
#                            {'linewidth': 0.5, 'color': 'grey', },
#                         'countries':
#                            {'linewidth': 0.3, 'color': 'grey', },
#                        }
        log.setLevel(loglevel)

    def __setattr__(self, key, value):
        #log.info("SETATTR: {} - {}".format(key, value))
        super(PlotMap, self).__setattr__(key, parse_parameter(key, value))

    def setResolution(self):
        """ 'c','l','i','h','f' """
        # lats = 36, 72, 108, 144, 180
        # lons = 72, 144, 216, 288, 360
        minlat, maxlat = self.lat[0], self.lat[-1]
        minlon, maxlon = self.lon[0], self.lon[-1]
        lats = maxlat + abs(minlat)
        lons = maxlon + abs(minlon)
        if lats > 130 and lons > 260:
            self.resolution = 'c'
        elif lats > 100 and lons > 200:
            self.resolution = 'l'
        elif lats > 60 and lons > 120:
            self.resolution = 'i'
        elif lats > 30 and lons > 60:
            self.resolution = 'h'
        elif lats <= 30 and lons <= 60:
            self.resolution = 'f'
        else:
            self.resolution = 'c' # default

    def setColorMap(self):
        """ Create color map """
        if not isinstance(self.colors, str) and isinstance(self.colors, Iterable):
            # adjust number of colors to number of bounds
            # min or max -> number of colors = number of bounds
            # both -> num of colors = num of bounds + 1
            # none -> num of colors = num of bounds - 1
            if self.bounds:
                if self.extend in ('min','max'):
                    if len(self.bounds) < len(self.colors):
                        self.colors = self.colors[:len(self.bounds)]
                elif self.extend == 'both':
                    if len(self.bounds)+1 < len(self.colors):
                        self.colors = self.colors[:len(self.bounds)+1]
            if self.extend == 'max':
                self.cmap = mpl.colors.ListedColormap(self.colors[:-1])
                self.cmap.set_over(self.colors[-1])
            elif self.extend == 'min':
                self.cmap = mpl.colors.ListedColormap(self.colors[1:])
                self.cmap.set_under(self.colors[0])
            elif self.extend == 'both':
                self.cmap = mpl.colors.ListedColormap(self.colors[1:-1])
                self.cmap.set_over(self.colors[-1])
                self.cmap.set_under(self.colors[0])
            else:
                self.cmap = mpl.colors.ListedColormap(self.colors)
            custom_cmap = True
        else:
            try:
                self.cmap = mpl.cm.get_cmap(self.colors)
            except:
                self.cmap = mpl.cm.get_cmap('jet')
            custom_cmap = False

        if self.bad:
            self.cmap.set_bad(self.bad)

        if self.background or self.kml or self.kmz:
            if self.extend in ('min', 'both'):
                self.cmap.set_under(color=(0, 0, 0, 0))
#             else:
#                 self.cmap.colors = [(0, 0, 0, 0),]+[c for c in self.cmap.colors[1:]]
#             try:
#                 self.cmap.colors = [(0, 0, 0, 0),]+[c for c in self.cmap.colors[1:]]
#             except: #if self.extend in ('min','both'):
#                 self.cmap.set_under(color=(0, 0, 0, 0))
#            else:
#                self.cmap.colors = [(0,0,0,0),]+[c for c in self.cmap.colors[1:]]

        # normalize colormap
        if self.bounds and self.smooth and not custom_cmap:
            if self.extend == 'min':
                self.norm = mpl.colors.BoundaryNorm([-np.inf]+self.bounds, self.cmap.N+1)
            elif self.extend == 'max':
                self.norm = mpl.colors.BoundaryNorm(self.bounds+[np.inf], self.cmap.N+1)
            elif self.extend == 'both':
                self.norm = mpl.colors.BoundaryNorm([-np.inf]+self.bounds+[np.inf], self.cmap.N+2)
            else:
                self.norm = mpl.colors.BoundaryNorm(self.bounds, self.cmap.N)
        elif self.bounds:
            self.norm = mpl.colors.BoundaryNorm(self.bounds, self.cmap.N)


    def setColorBar(self, mco, location='left', drawedges=False, cax=None):
        """ Create color bar """
#        xs = self.xsize
#        nap = .8-((1-xs)*0.4)
#        a = plt.axes([nap, 0, .14, 1])#, frameon=False)
#        plt.axis('off')
        mpl.rcParams['axes.linewidth'] = 0.1
        mpl.rcParams['axes.formatter.useoffset'] = False
        if self.ticks:
            #log.info("ticks %s" % str(self.ticks))
            self.ticks = parse_parameters_list(self.ticks)
        elif self.bounds:
            self.ticks = self.bounds
        else:
            try:
                self.ticks = mco.levels
            except:
                pass

        log.info("***** {} *****".format(self.formats))
        if self.map:
            cb = self.map.colorbar(mco, ticks=self.ticks, format=self.formats, pad="2%", size="3%", extend=self.extend, drawedges=drawedges)
        else:
            cb = plt.colorbar(mco, ticks=self.ticks, format=self.formats, pad=.06, extend=self.extend, drawedges=drawedges)

        cb.ax.tick_params(labelsize=float(self.coordsopts[1]))
        for lin in cb.ax.yaxis.get_ticklines():
            lin.set_visible(False)
        #self.printTime("colorbar")

        ## If required, draw arrow pointing to the specified limits
        if self.hasLimits():
            # The following two values are absolute
            shrink = 0.75
            upper = 0.863 - 0.45 * (0.8 - shrink) # formula seems to work ok
            lower = 0.137 + 0.45 * (0.8 - shrink)
            span = upper - lower
            arrows = self.limits

            if self.bounds:
                ticks = self.bounds
            else:
                ticks = mco.levels

            f = span/float(len(ticks) - 1)
            for i in arrows:
                for j in range(0, len(ticks) - 1):
                    if (i >= ticks[j] and i <= ticks[j+1]):
                        if (i == ticks[j+1]):
                            p = j+1
                            add = 0
                        else:
                            p = j
                            add = (float(i - ticks[j])/float(ticks[j+1] - ticks[j]))*f
                        pos = f*p + lower
                        plt.arrow(0.88, pos + add, 0.10, 0, length_includes_head=True, head_length=0.10, head_width=0.025, fill=True, color='k')
        #plt.colorbar(drawedges=drawedges, cax=cax, ticks=self.bounds)

    def setTitle(self, title, sdate, cdate, step, stime):
        """ Set the title of the current image to the one provided, substituting the
            patterns """

        titleDic = {
            'syear':  sdate.strftime("%Y"),
            'smonth': sdate.strftime("%m"),
            'sMONTH': sdate.strftime("%b"),
            'sday':   sdate.strftime("%d"),
            'shour':  sdate.strftime("%H"),
            'year':   cdate.strftime("%Y"),
            'month':  cdate.strftime("%m"),
            'MONTH':  cdate.strftime("%b"),
            'day':    cdate.strftime("%d"),
            'hour':   cdate.strftime("%H"),
            'step':   step,
            'simday': "%d" % (int(stime)/24),
            'simhh':  stime,
            #'simhh':  "%02d" % (int(stime)%24)
        }

        try:
            pTitle = str(title) % titleDic #("%sh" % sTime, valid)
        except Exception as e:
            print("Title error: %s", str(e))
            pTitle = title % titleDic #("%sh" % sTime, valid)

        return pTitle

    def printTime(self, msg=None):
        # initial time
        if 'start_t' not in globals():
            global start_t, last_t
            print("Creating start_t")
            start_t = datetime.now()
            last_t = start_t

        now_t = datetime.now()
        diff_t = now_t - last_t
        if (msg != None):
            print('TIME:', msg, ' done in ', diff_t.seconds, ' s')
        last_t = now_t

    def runCommand(self, commStr, fatal=True):
        print(commStr)
        p = subprocess.Popen(commStr.split(), stderr=subprocess.PIPE)
        output, err = p.communicate()
        print(output,'-----',err)
#        st, out = commands.getstatusoutput(commStr)
#        if st != 0:
#            print "Error: %s" % str(out)
#            if (fatal == True):
#                sys.exit(1)

    def genAnim(self, inpattern, outfile):
        ''' Generate an animation starting from a set of
            images, specified by the inpattern parameter '''
        #print "Animation: ", indir, inpattern, outdir, outfile
        # Create animation
        self.runCommand(
            "/usr/bin/convert -delay %s -loop 0 -layers Optimize %s/%s %s/%s" % \
            (self.anim_delay, self.outdir, inpattern, self.outdir, outfile))
        # Remove intermediate files
        #self.runCommand("rm %s/%s %s" % (indir, inpattern, self.mapName), False)

#           ccc = []
#           ccc.extend(self.colors)
#           print "Filtering scatter data for date/hour: ", currDate.strftime("%Y%m%d"), sTime24
#           csv_lat, csv_lon, csv_val = csv_handler.filter(currDate.strftime("%Y%m%d"), sTime24)
#           #csv_col = self.dataTransform.setColorsFromBuckets(ccc, self.bounds, csv_con)
#           if(len(csv_lat) > 0):
#               scatter_data = [csv_lon, csv_lat, 40, csv_col]
#               print "**************** SCATTER_DATA", scatter_data
#               print "Filtered %d records for scatterplot" % len(scatter_data)


    def initMap(self, grid):
        """ Initialize a Basemap map. Initialization should be performed only once
        the beginning of a serie of images """
        glon, glat = grid
        #print("***",self.lon, self.lat,"***")
        if not self.lat: # or len(self.lat) not in (2,3):
            self.lat = "%s-%s" % (str(round(glat.min(), 1)).replace('-','m'), str(round(glat.max(), 1)).replace('-','m'))

        if not self.lon: # or len(self.lon) not in (2,3):
            self.lon = "%s-%s" % (str(round(glon.min(), 1)).replace('-','m'), str(round(glon.max(), 1)).replace('-','m'))

        #print(self.lon, self.lat)
#        # Fix the printout of tick values to avoid .0 decimals in integers
#        strs = []
#        if self.bounds:
#            for b in self.bounds:
#                if (b == int(b)):
#                    strs.append("%d" % b)
#                else:
#                    strs.append(str(b))
#
        # Set the colormap
        self.setColorMap()
        if not self.resolution:
            self.setResolution()

        self.first_image = True


    def genImageMap(self, figName, grid, data,  imgTitle, cur_scatter_data=None, **kwargs):
        """ Generate image map """

        # overwrite option
        if os.path.exists(figName + ".png") and not self.overwrite:
            print(figName, " already exists.")
            plt.clf()
            return figName

        map_data = data.getMapData()
        # FIXME
        scatter_data = data.getScatterData() or cur_scatter_data

        plt.clf()
#        params = {
#             'font.size': 14,
#             'text.fontsize': 28,
#             'axes.titlesize': 11,
#             'savefig.dpi': self.dpi
#        }
#
#        mpl.rcParams.update(params)

        if not self.nomap:
            if self.projection != 'cyl':
                lon_0 = (self.lon[-1]-abs(self.lon[0]))/2
                lat_0 = (self.lat[-1]-abs(self.lat[0]))/2
                #print("-----------", lon_0, lat_0, "-----------")
            else:
                lon_0, lat_0 = None, None
            self.map = Basemap(
                projection=self.projection, resolution=self.resolution,
                llcrnrlon=self.lon[0], llcrnrlat=self.lat[0],
                urcrnrlon=self.lon[-1], urcrnrlat=self.lat[-1],
                lon_0=lon_0, lat_0=lat_0,
                fix_aspect=self.keep_aspect,
                area_thresh=self.area_thresh
            )

        glon, glat = grid
        #log.info("GLON: %s, GLAT: %s" % (str(glon.shape), str(glat.shape)))
        if len(glon.shape)==1 and len(glat.shape)==1:
            glon, glat = np.meshgrid(glon, glat)

        #print(glon, glat)
        log.info("1. GLON: %s, GLAT: %s" % (str(glon.shape), str(glat.shape)))

        # if curvilinear grid do interpolation, return already gridded coords
        if not is_grid_regular(glon, glat):
            map_data[0], glon, glat = do_interpolation(map_data[0], glon, glat)

        log.info("2. GLON: %s, GLAT: %s" % (str(glon.shape), str(glat.shape)))

        if not self.nomap:
            x, y = self.map(*(glon, glat))
        else:
            x, y = glon, glat

        log.info("3. GLON: %s, GLAT: %s" % (str(x.shape), str(y.shape)))
#        print "map_data", map_data[0].shape

        #self.printTime("meshgrid")
        #log.info("X: %s, Y: %s" % (str(x.shape), str(y.shape)))

#        # nomap option
#        if self.nomap and os.path.exists("%s-%s/%s.png" % (runDate, varName, figName)) and not self.overwrite:
#            print figName, " already exists."
#            plt.clf()
#            return figName

        if self.nomap:
            self.mgplot.frameon = False

        # Draw filled contour
        if not self.keep_aspect:
#            log.info("Not keeping original aspect")
#            log.info("XSIZE: %s" % self.xsize)
#            log.info("YSIZE: %s" % self.ysize)
            ysize_norm = self.ysize*0.8
            xsize_norm = self.xsize*0.8
            rows = imgTitle.count("\n")
            blines = max(rows - 2, 0)
            param = self.fontsize/400
            ystart_base_norm = 0.1 - param*(blines)#imgTitle
            xstart_base_norm = 0.1
            ystart_norm = (0.8 - ysize_norm) / 2 + ystart_base_norm
            xstart_norm = (0.8 - xsize_norm) / 2 + xstart_base_norm
            #ax_map = self.mgaxis.axes([xstart_norm, ystart_norm, xsize_norm, ysize_norm])
#            log.info("Ynorm: %s, Xnorm: %s, Ystart: %s, Xstart: %s" % (ysize_norm, xsize_norm, ystart_norm, xstart_norm))
            self.mgplot.add_axes([xstart_norm, ystart_norm, xsize_norm, ysize_norm])
            #print "Switching AXES for MAP:", ax_map

        if self.alpha != None and self.bounds != None:
            if self.extend in ('min', 'both'):
                map_data[0] = np.ma.masked_where(map_data[0] < self.bounds[0], map_data[0])
            else:
                map_data[0] = np.ma.masked_where((map_data[0] >= self.bounds[0]) & (map_data[0] < self.bounds[1]),
map_data[0])

        mco = None

        log.info(type(map_data[0]))
        map_data[0] = np.ma.filled(map_data[0], np.nan)
        log.info(type(map_data[0]))

        if not self.nocontourf and not self.nomap and self.smooth:
            log.info("X: %s, Y: %s, DATA: %s" % (x.shape, y.shape, map_data[0]))
            mco = self.map.contourf(x, y,
                                    map_data[0],
                                    cmap=self.cmap,
                                    norm=self.norm,
                                    levels=self.bounds,
                                    extend=self.extend,
                                    horizontalalignment='center',
                                    alpha=self.alpha,
                                    antialiased=True)

        elif not self.nocontourf and not self.nomap and not self.smooth:
            log.info("X: %s, Y: %s, DATA: %s" % (x.shape, y.shape, map_data[0]))
            mco = self.map.pcolormesh(x, y,
                                      map_data[0],
                                      cmap=self.cmap,
                                      norm=self.norm,
                                      alpha=self.alpha,
                                      antialiased=True)

        elif not self.nocontourf and self.nomap and self.smooth:
            mco = plt.contourf(x, y,
                               map_data[0],
                               cmap=self.cmap,
                               norm=self.norm,
                               levels=self.bounds,
                               extend=self.extend,
                               horizontalalignment='center',
                               alpha=self.alpha,
                               antialiased=True)

            plt.axis([self.lon[0], self.lon[-1], self.lat[0], self.lat[-1]])

        elif not self.nocontourf and self.nomap and not self.smooth:
            mco = plt.pcolormesh(x, y,
                                 map_data[0],
                                 cmap=self.cmap,
                                 norm=self.norm,
                                 alpha=self.alpha,
                                 antialiased=True)

            plt.axis([self.lon[0], self.lon[-1], self.lat[0], self.lat[-1]])

        # Draw shape files
        if self.hasShapeFiles():
            line_w = float(self.countropts[0])
            for shapef in self.shapefiles:
                log.info("Processing shape file: {} with line width: {}".format(shapef,line_w))
                self.map.readshapefile(shapef, "%s" % os.path.basename(shapef), linewidth=line_w, color=self.countropts[1])
                line_w = max(self.shapef_width_step, line_w - self.shapef_width_step)
        #self.printTime("contourf")

        ## FIXME Modify to use scatter inside DATA
        ## if DATA.hasScatterData()... etc...
        if scatter_data is not None:
            log.info("Plotting scatter data: {} of keys {}".format(str(scatter_data), str(scatter_data.keys())))
            if mco and self.bounds:
                self.map.scatter(scatter_data['lon'].tolist(),
                                 scatter_data['lat'].tolist(),
                                 s=scatter_data['size'].tolist(),
                                 c=scatter_data['color'].tolist(),
                                 marker='o',
                                 linewidth=0.3,
                                 vmin=self.bounds[0],
                                 vmax=self.bounds[-1],
                                 cmap=self.cmap,
                                 norm=self.norm,
                                 zorder=10)
            elif mco:
                self.map.scatter(scatter_data['lon'].tolist(),
                                 scatter_data['lat'].tolist(),
                                 s=scatter_data['size'].tolist(),
                                 c=scatter_data['color'].tolist(),
                                 marker='o',
                                 linewidth=0.3,
                                 cmap=self.cmap,
                                 norm=self.norm,
                                 zorder=10)
            elif self.bounds:
                mco = self.map.scatter(scatter_data['lon'].tolist(),
                                       scatter_data['lat'].tolist(),
                                       s=scatter_data['size'].tolist(),
                                       c=scatter_data['color'].tolist(),
                                       marker='o',
                                       linewidth=0.3,
                                       vmin=self.bounds[0],
                                       vmax=self.bounds[-1],
                                       cmap=self.cmap,
                                       norm=self.norm,
                                       zorder=10)
            else:
                mco = self.map.scatter(scatter_data['lon'].tolist(),
                                       scatter_data['lat'].tolist(),
                                       s=scatter_data['size'].tolist(),
                                       c=scatter_data['color'].tolist(),
                                       marker='o',
                                       linewidth=0.3,
                                       cmap=self.cmap,
                                       norm=self.norm,
                                       zorder=10)

        if data.hasWindData():
            winds = data.getWindData()
            X,Y,U,V = delete_masked_points(x.ravel(), y.ravel(), winds['u'].ravel(), winds['v'].ravel())
            #print("Wind scale is", self.wind_units, self.wind_scale)
            if winds.has_key('barbs'):
                self.map.barbs(X, Y, U, V, #units=self.wind_units,
                    #headlength=self.wind_head_length,
                    #headwidth=self.wind_head_width,
                    #width=self.wind_width,
                    #minshaft=self.wind_minshaft,
                    #scale=self.wind_scale,
                    color='k')
                #self.printTime("barbs")
            else:
                Q = self.map.quiver(X, Y, U, V, units=self.wind_units,
                        headlength=self.wind_head_length,
                        headwidth=self.wind_head_width,
                        width=self.wind_width,
                        minshaft=self.wind_minshaft,
                        scale=self.wind_scale,
                        color='gray')
                # Draw the key
                plt.quiverkey(Q,
                    self.wind_label_xpos,
                    self.wind_label_ypos,
                    self.wind_label_scale,
                    label='%s m/s' % self.wind_label_scale,
                    coordinates='axes',
                    labelpos='S', labelsep=0.05)
                #self.printTime("quivers")

        if data.hasContourData():
            interval = self.contours_int
            exclude = self.contours_exclude_vals
            cLowBound = -99999
            cUppBound = 99999
            cdata = data.getContourData()
            #print(cdata, type(cdata))
            try:
                cMin = min(filter (lambda a: a > cLowBound, cdata.ravel()))
                adjcMin = int(cMin - (cMin % interval) - interval * 2)
            except ValueError:
                cMin =0
            try:
                cMax = max(filter (lambda a: a < cUppBound, cdata.ravel()))
                adjcMax = int(cMax - (cMax % interval) + interval * 2)
            except ValueError:
                cMax = 0
            lvls = np.arange(adjcMin, adjcMax, interval)
            for ex in exclude:
                lvls = filter (lambda ex: ex != 0, lvls)
            if (len(lvls) > 0) and map_data != None:
                mco = self.map.contourf(x, y,
                                        map_data[0],
                                        cmap=self.cmap,
                                        norm=self.norm,
                                        levels=self.bounds,
                                        extend=self.extend,
                                        horizontalalignment='center',
                                        alpha=self.alpha)

            #print "-----------------", map_data, cdata, "--------------------"
            if map_data != None and (map_data[0] == cdata).all():
                print(":::::::::::::::::::::::: SAME !!! :::::::::::::::::::")
                CS = plt.contour(x, y,
                                 cdata,
                                 levels=self.bounds,
                                 colors=self.contours_color,
                                 linewidths=self.contours_linewidth,
                                 alpha=self.alpha)
            else:
                print(":::::::::::::::::::::::: DIFFERENT !!! :::::::::::::::::::")
                print("MIN:", cMin, "MAX:", cMax)
                CS = plt.contour(x, y,
                                 cdata,
                                 levels=lvls,
                                 colors=self.contours_color,
                                 linewidths=self.contours_linewidth,
                                 alpha=self.alpha)

            if self.contours_label:
                self.mgplot.clabel(CS,
                                   inline=1,
                                   fontsize=self.contours_lbl_fontsize,
                                   #backgroundcolor='r',
                                   fmt=self.contours_lbl_format)
#            else:
#                print "Not drawing contours since levels has ", len(lvls), " elements"

        #coords normalization
#        lat_offset = abs(self.lat[0]) % self.lat[2]
#        lon_offset = abs(self.lon[0]) % self.lon[2]

        if not self.nomap and not self.kml and not self.kmz:
#            self.map.drawparallels(np.arange(self.lat[0]+lat_offset, self.lat[1], self.lat[2]),labels=[1,0,0,0],linewidth=self.coords_linewidth, fontsize=self.coords_fontsize)
#            self.map.drawmeridians(np.arange(self.lon[0]+lon_offset, self.lon[1], self.lon[2]),labels=[0,0,0,1],linewidth=self.coords_linewidth, fontsize=self.coords_fontsize)
            #self.printTime("coords")
            self.map.drawparallels(self.lat, labels=[0,0,0,0],linewidth=float(self.coordsopts[0]), fontsize=float(self.coordsopts[1]), color=str(self.coordsopts[2]))
            self.map.drawmeridians(self.lon, labels=[0,0,0,0],linewidth=float(self.coordsopts[0]), fontsize=float(self.coordsopts[1]), color=str(self.coordsopts[2]))
            self.map.drawcountries(linewidth=float(self.countropts[0]), color=str(self.countropts[1]))
            self.map.drawcoastlines(linewidth=float(self.coastsopts[0]), color=str(self.coastsopts[1]))
            if self.continents:
                self.map.fillcontinents(color=self.continents, zorder=0)

#            drawopts = self.drawopts
#            if drawopts:
#                # Drawing countries
#                if 'countries' in drawopts:
#                    self.map.drawcountries(**drawopts['countries'])
#                    #self.printTime("countries")
#                # Drawing coastlines (land/sea, lakes, etc...)
#                if 'coastlines' in drawopts:
#                    self.map.drawcoastlines(**drawopts['coastlines'])
#                    #self.printTime("coastlines")
##                # Drawing states (FIXME does it work outside the U.S.?)
##                if 'states' in drawopts:
##                    self.map.drawstates(**drawopts['states'])
##                    #self.printTime("states")

        # Change axes for colorbar
        if self.colorbar and not self.kml and not self.kmz and (not self.nocontourf or scatter_data is not None):
            self.setColorBar(mco)

        #m.bluemarble()
        if self.background == 'shadedrelief':
            self.map.shadedrelief()
        if self.background == 'bluemarble':
            self.map.bluemarble()
        if self.background == 'etopo':
            self.map.etopo()
        if self.background == 'GIS':
            h0 = float(self.lat[-1] - self.lat[0])
            w0 = float(self.lon[-1] - self.lon[0])
            ff = h0/w0      # form factor
            height = 1024*ff       # height
            size = "%d,%d" % (1024, height)
            # basemap_url = "http://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/export?\
            # basemap_url = "http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export?\
            basemap_url = "http://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/export?\
bbox=%s,%s,%s,%s&\
bboxSR=4326&\
imageSR=4326&\
size=%s&\
dpi=%d&\
format=png24&\
f=image" % (self.lon[0], self.lat[0], self.lon[-1], self.lat[-1], size, self.dpi)
            self.map.imshow(imread(urlopen(basemap_url)), origin='upper')

        #logo
        if self.logo:
            im = Image.open(self.logo[0])
#            height = im.size[1]
#            width  = im.size[0]

            # We need a float array between 0-1, rather than
            # a uint8 array between 0-255
            nim = np.array(im).astype(np.float) / 255

            # With newer (1.0) versions of matplotlib, you can
            # use the "zorder" kwarg to make the image overlay
            # the plot, rather than hide behind it... (e.g. zorder=10)
            self.mgplot.figimage(nim, self.logo[1], self.logo[2], zorder=10)

        # SAVEFIG
        fullname = "{}.{}".format(figName, self.filefmt)
        log.warning("printing {}".format(fullname))
        if self.kml or self.kmz:
            #self.mgplot.axes(frameon=0)
            self.mgplot.savefig(fullname,
                                bbox_inches='tight',
                                frameon=0,
                                pad_inches=0, dpi=self.dpi, transparent=True)
        else:
            #a = plt.axes([0.0, 0.0, 1.0, 1.0])
            #plt.axis('off')
            plt.setp(plt.gca().spines.values(), linewidth=.1)
            xpos = self.xsize/2 + 0.07
            if not self.keep_aspect:
                ypos = ystart_norm + ysize_norm + 0.05
            else:
                ypos = self.ysize*0.95

            self.mgplot.text(
                xpos,
                ypos,
                imgTitle,
                horizontalalignment='right',
                verticalalignment='top',
                fontsize=self.fontsize,
                zorder=0,
                )
            self.mgplot.savefig(fullname, bbox_inches='tight', pad_inches=.2, dpi=self.dpi)
            #self.mgplot.show()

        #plt.tight_layout()
        #self.printTime("saving")

#        if(self.first_image):
#            #if first image of the batch, produce a image "color map"
#            print "First image of the batch: creating image color map"
#            self.mapName = "%s.map.png" % figName
#            # Get the colorbar to generate the image color map
#            self.runCommand("convert -crop 70x600+730+0 -colors 160 %s.png %s" % (figName, self.mapName))
#            self.first_image = False

        #convert from png to gif
        #print "printing ", figName
#        self.runCommand("convert -quality 80 +dither -remap %s %s.png %s.anim.png" % (self.mapName, figName, figName))
#        self.runCommand("convert +dither %s.png %s.gif" % (figName, figName))
#        self.runCommand("rm %s.png" % figName)

        #plt.clf()
        #self.printTime("convert")
        return figName


    def compareMaps(self, mapNames, outdir, date, steps, tpl=''):
        """ Generate maps comparison """

        os.chdir(outdir)

        #print "MAPNAMES", mapNames
        #for mapName in mapNames:
#        newMapNames = mapNames[0]
#        items = {} #[i[0] for i in mapNames]
#        for i in range(0, len(mapNames)-1):
#            items, newMapNames, newMapNameTpl = self.twoMapsCompare([newMapNames, mapNames[i+1]], items)

        mn = np.array(mapNames)
        ks = mn.T

        idx = 0
        for item in ks:
#            if idx >= len(newMapNames):
#                continue
            imgs = ' '.join([str(i) + '.gif' for i in item])
            if tpl:
                newimg = tpl % {'date':date, 'step':steps[idx]}
            else:
                newimg = steps[idx]
            #comm = "montage %s -tile 2x -geometry 800x600+1+1 %s.gif" % (imgs, newMapNames[idx])
            comm = "montage %s -tile 2x -geometry +1+1 %s.gif" % (imgs, newimg)
            #print "COMPARE COMMAND:", comm
            st, out = subprocess.getstatusoutput(comm)
            idx += 1

        #montage <infiles> -tile 2x -geometry 800x600+1+1 <outfile>

        #rename from 00-06-... to 00-01 ...
#        st, out = commands.getstatusoutput("ls %s*" % newMapNameTpl)
#        if st != 0:
#            print "Error: %s" % str(out)
#        else:
#            names = out.split('\n')
#            #print names
#            for num in range(0, len(names)):
#                snum = "%02d" % num
#                #print "mv %s %s.gif" % (names[num], newMapNameTpl.replace("??", snum))
#                st2, out2 = commands.getstatusoutput("mv -f %s %s.gif" % (names[num], newMapNameTpl.replace("??", snum)))
#                if st2 != 0:
#                    print "Error: %s" % str(out2)

#        newMapNameTpl2 = newMapNameTpl.replace("??", "loop")
        nimg0 = "??"
        nimg1 = "loop"
        if tpl:
            nimg0 = tpl % {'date':date, 'step':nimg0}
            nimg1 = tpl % {'date':date, 'step':nimg1}
        st, out = subprocess.getstatusoutput("convert -delay 75 -loop 0 %s.gif %s.gif" % (nimg0, nimg1))
        if st != 0:
            print("Error: %s" % str(out))


    def genKML(self, figNames, srcvars, dims, online):
        """ """
        from lxml import etree
#        from pykml.parser import Schema
        from pykml.factory import KML_ElementMaker as KML
#        from datetime import datetime, timedelta
        import zipfile

        lon = self.lon
        lat = self.lat

        print(figNames)
        #kmlName = '-'.join(os.path.basename(figNames[0]).split('-')[:-1])
        kmlName = os.path.basename(figNames[0])[:-3]
        varName = srcvars[0] #figNames[0].split('-')[-2]
        runDate0 = datetime.strptime(dims[0], "%HZ%d%b%Y") #.strftime("%Y%m%d%H")
        runDate1 = datetime.strptime(dims[1], "%HZ%d%b%Y") #.strftime("%Y%m%d%H")
        begindate = runDate0.strftime("%Y%m%d%H")
        dirName = os.path.join(self.outdir, begindate + '-' + varName).replace('./','')
        interval = runDate1 - runDate0
        datefmt = "%Y-%m-%dT%H:00:00Z"

        doc = KML.kml(
            KML.Folder(
                KML.name(kmlName),
                KML.LookAt(
                    KML.longitude((lon[1]+lon[-1])/2),
                    KML.latitude((lat[1]+lat[-1])/2),
                    KML.range(8500000.0),
                    KML.tilt(0),
                    KML.heading(0),
                ),
                KML.ScreenOverlay(
                    KML.name("Legend"),
                    KML.open(1),
                    KML.Icon(
                        KML.href("%s/%s-colorbar.png" % (dirName, begindate)),
                    ),
                    KML.overlayXY(x="0",y="1",xunits="fraction",yunits="fraction"),
                    KML.screenXY(x=".01",y="0.55",xunits="fraction",yunits="fraction"),
                    KML.rotationXY(x="0",y="0",xunits="fraction",yunits="fraction"),
                    KML.size(x="0",y="0.5",xunits="fraction",yunits="fraction"),
                    id="%s-ScreenOverlay" %(begindate),
                ),
            )
        )

        try:
            os.mkdir(dirName)
        except:
            pass

        if not online:
            zf = zipfile.ZipFile("%s.kmz" % kmlName, 'w')

        for figName, dat in zip(figNames, sorted(dims.keys())):
            dt = dims[dat]
            figName = figName + ".png"
            figPath = os.path.join(dirName,os.path.basename(figName))
            startdate = datetime.strptime(dt, "%HZ%d%b%Y")
            begdate = startdate.strftime(datefmt)
            enddate = (startdate + interval).strftime(datefmt)
            starth = startdate.hour
            doc.Folder.append(KML.GroundOverlay(
                KML.name("%02d:00:00Z" % starth),
                KML.TimeSpan(
                    KML.begin(begdate),
                    KML.end(enddate),
                ),
                KML.Icon(
                    KML.href(figPath),
                    KML.viewBoundScale(1.0),
                ),
                KML.altitude(0.0),
                KML.altitudeMode("relativeToGround"),
                KML.LatLonBox(
                    KML.south(lat[0]),
                    KML.north(lat[-1]),
                    KML.west(lon[0]),
                    KML.east(lon[-1]),
                    KML.rotation(0.0),
                ),
            ))

            if os.path.exists(figName):
                os.rename(figName, figPath)
                zf.write(figPath)

        outf = file("%s.kml" % kmlName, 'w')
        outf.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        outf.write(etree.tostring(doc, pretty_print=True))
        outf.close()

        if not online:
            zf.write("%s.kml" % kmlName)
            zf.write("%s/%s-colorbar.png" % (dirName, begindate))
            zf.close()

            for img in os.listdir(dirName):
                os.remove("%s/%s" % (dirName, img))
            os.rmdir(dirName)
            os.remove("%s.kml" % kmlName)


    def aplot(self, x, y, map_data=None, wind_data=None, contour_data=None, scatter_data=None, **kwargs):
        """ Plot one or more maps directly from numerical arrays """

        # store options to be restored at the end
        localvars = copy.deepcopy(vars(self))
        # update from config file
        if ('config' in kwargs) and ('section' in kwargs):
            self.loadConf(kwargs['section'],kwargs['config'])
        # update from command line
        vars(self).update(parse_parameters(kwargs))
        # arguments are only local

        # parse wind arguments
        if (self.windopts and (len(self.windopts) == 4)):
            self.wind_scale = int(self.windopts[3])
        log.info("SHP {}".format(str(self.shapefiles)))
        if self.shapefiles:
            self.shapefiles = [f.replace(".shp","") for f in glob(self.shapefiles)]
        log.info("SHP {}".format(str(self.shapefiles)))

        if scatter_data is not None:
            if type(scatter_data) == str:
                scatter_data = DataFrameHandler(parse_path(self.indir, scatter_data)).filter()
            else:
                scatter_data = DataFrameHandler(scatter_data).filter()
        else:
            scatter_data = None
        log.info("scatter data: {}".format(str(scatter_data)))

        data = MapData(
                    map_data=[map_data], #temporarily
                    wind_data=wind_data,
                    contour_data=contour_data,
                    scatter_data=scatter_data
                )
        grid = (x, y)
        self.initMap(grid)

        if self.img_template:
            fName = self.img_template
        else:
            fName = 'mg_aplot'
        figName = "%s/%s" % (self.outdir, fName)

        plt.clf()
        self.mgplot, self.mgaxis = plt.subplots()

        fn = self.genImageMap(
                              figName,
                              grid,
                              data,
                              self.title,
                              #scatter_data=scatter_data
                             )

#        # Create Max at required intervals
#        if self.maxdata and nTime in self.maxdata:
#            if (self.maxtitle != None):
#                figName = "%s_%s" % (fName, 'MAXD%d' % (nTime/24))
#                pTitle = self.setTitle(self.maxtitle, sDate, currDate, sTime)
#                self.genImageMap(
#                                figName,
#                                grid,
#                                nc_handler.getCurrentMaxData(),
#                                pTitle
#                                )
#            else:
#                print "Missing MAXTITLE, thus not generating MAX images!"

        # restore options without local function parameters
        vars(self).update(localvars)

    def plot_cube(self, cube, **kwargs):
        if 'title' not in kwargs:
            kwargs['title'] = '{0.long_name} ({0.units})'.format(cube)

        self.aplot(
            cube.coord('longitude').points,
            cube.coord('latitude').points,
            map_data=cube.data,
            **kwargs
        )

    def plot(self, **kwargs):
        """ Plot one or more maps from netCDF file(s) """

        # store options to be restored at the end
        localvars = copy.deepcopy(vars(self))
        # update from config file
        if ('config' in kwargs) and ('section' in kwargs):
            self.loadConf(kwargs['section'],kwargs['config'])
        # update from command line
        vars(self).update(parse_parameters(kwargs))
        # arguments are only local

        if isinstance(self.srcvars, str):
            self.srcvars = [self.srcvars]
        elif not isinstance(self.srcvars, list):
            log.error('Error')

        if isinstance(self.srcfiles, str):
            self.srcfiles = [self.srcfiles]
        elif not isinstance(self.srcfiles, list):
            log.error('Error')

        # parse wind arguments
        if (self.windopts and (len(self.windopts) == 4)):
            self.wind_scale = int(self.windopts[3]);
        log.info("SHP {}".format(str(self.shapefiles)))
        if self.shapefiles:
            self.shapefiles = [f.replace(".shp","") for f in glob(self.shapefiles)]
        log.info("SHP {}".format(str(self.shapefiles)))

        if self.scatter is not None:
            if type(self.scatter) == str:
                scatter_data = DataFrameHandler(parse_path(self.indir, self.scatter)).filter()
            else:
                scatter_data = DataFrameHandler(self.scatter).filter()
        else:
            scatter_data = None
        log.info("scatter data: {}".format(str(scatter_data)))

        #run = ''
        run_tmp = ''
        mapNames = []

        nc_handler = MapDataHandler(
                                    self.srcfiles,
                                    self.srcvars,
                                    self.indir,
                                    self.srcgaps,
                                    self.wind,
                                    self.windopts,
                                    self.lat,
                                    self.lon,
                                    self.transf,
                                    self.subsetting,
                                    self.dimension,
                                    winds={'src': self.wind,
                                           'opts': self.windopts},
                                    contours={'var': self.contours},
                                    varconds=self.varconds,
                                   )

        figNames = []
        pltNames = []

        dims = nc_handler.getDims()

        if self.timesteps == 'all':
            self.timesteps = list(sorted(dims.keys()))

        run_tmp = dims[0] #12:30Z30NOV2010
        if run_tmp[:-10] == "01:30": run_tmp = run_tmp.replace("01:30", "00")
        #run = "%sh %s %s %s" % (run_tmp[:-10], run_tmp[-9:-7], run_tmp[-7:-4], run_tmp[-4:])

        # return grid
        grid = nc_handler.grid

        #if not NOMAP:
        self.initMap(grid)

        sDate = datetime.strptime("%s %s %s %s" % (run_tmp[-4:], run_tmp[-7:-4], run_tmp[-9:-7], run_tmp[0:2]), "%Y %b %d %H" )

        ssDate = sDate.strftime("%Y%m%d")
        steps = []

        START = self.timesteps[0]

        #log.info("Start @ %s - sDate: %s - run_tmp: %s" % (START, sDate, run_tmp))

        if START is None:
            START = 0

        for nTime in self.timesteps: #range(START,int(TOTAL),INTERVAL):

            plt.clf()

#            self.mgplot = plt.figure()
#            self.mgaxis = plt.gca()
            self.mgplot, self.mgaxis = plt.subplots()

            valid_tmp = dims[nTime]
            currDate = datetime.strptime("%s %s %s %s" % (valid_tmp[-4:], valid_tmp[-7:-4], valid_tmp[-9:-7], valid_tmp[0:2]), "%Y %b %d %H" )

            sTime = "%02d" % nTime
            steps.append(sTime)

            pTime = (currDate - sDate).total_seconds()/3600
            sTime24 = "%02d" % (pTime%24)
            #sTime3d = "%03d" % pTime # Currently unused, only for Valentina who has more than 99 img in a set

            if self.img_template:
                fName = self.img_template % {'date': ssDate, 'step': sTime}
                figName = "%s/%s" % (self.outdir, fName)
                loopName = self.img_template % {'date': ssDate, 'step': 'loop'}
            else:
                fName = '.'.join(os.path.basename(self.srcfiles[0]).split('.')[:-1])
                figName = "%s/%s_%s" % (self.outdir, fName, sTime)
                loopName = "%s_loop" % (fName)

            #valid = "%02dUTC %s" % (pTime % 24, currDate.strftime("%d %b %Y"))

            #stime = "%02d" % (int(run_tmp.split('Z')[0])+pTime)
            stime = "%02d" % (pTime)
            pTitle = self.setTitle(self.title, sDate, currDate, sTime, stime)
            cur_scatter_data = None
            if scatter_data != None and (currDate in scatter_data):
                cur_scatter_data = scatter_data[currDate]

            fn = self.genImageMap(
                                  figName,
                                  grid,
                                  nc_handler.getDataForTstep(nTime),
                                  pTitle,
                                  cur_scatter_data=cur_scatter_data
                                 )

            figNames.append(fn)
            pltNames.append((self.mgplot, self.mgaxis))

            # Create Max at required intervals
            if self.maxdata and nTime in self.maxdata:
                if (self.maxtitle != None):
                    figName = "%s_%s" % (fName, 'MAXD%d' % (nTime/24))
                    pTitle = self.setTitle(self.maxtitle, sDate, currDate, sTime)
                    self.genImageMap(
                                    figName,
                                    grid,
                                    nc_handler.getCurrentMaxData(),
                                    pTitle
                                    )
                else:
                    print("Missing MAXTITLE, thus not generating MAX images!")

        if self.kml or self.kmz:
            plt.clf()

            runDate = sDate.strftime("%Y%m%d%H")
            #separate colorbar
            mpl.rcParams['axes.linewidth'] = 0.1
            fig = plt.figure(figsize=(.1,12))
            ax = fig.add_axes([0.05, 0.80, 0.9, 0.15], axisbg=(1,1,1,0))
            print("...", self.bounds, "...")
            cb = mpl.colorbar.ColorbarBase(
                                           ax,
                                           cmap=self.cmap,
                                           norm=self.norm,
                                           values=self.bounds,
                                           ticks=self.bounds,
                                           extend=self.extend,
                                           drawedges=False)
            if self.bounds:
                cb.set_ticklabels(self.bounds)
            else:
                try:
                    cb.set_ticklabels(mco.levels)
                except:
                    pass
            cb.ax.tick_params(labelsize=6)
            plt.setp(plt.getp(ax, 'yticklabels'), color='w')
            plt.setp(plt.getp(ax, 'yticklabels'), fontsize=6)
            for lin in cb.ax.yaxis.get_ticklines():
                lin.set_visible(False)

            tit = str(pTitle)
            idx1 = tit.find('(')
            idx2 = tit.find(')')
            varUnit = tit[idx1:idx2+1]
            if varUnit.find("%s") >= 0:
                varUnit = ''
            plt.xlabel(
                pTitle,
                #"%s\n%s" % (self.srcvars[0], varUnit),
                horizontalalignment='left',
                color='w',
                fontsize=6,
            )
            ax.xaxis.set_label_coords(-0.025,-0.025)

            try:
                os.mkdir("%s-%s" % (runDate, self.srcvars[0]))
            except:
                pass

            fig.savefig(
                        "%s/%s-%s/%s-colorbar.png" % (self.outdir, runDate, self.srcvars[0], runDate),
                        bbox_inches='tight',
                        pad_inches=0, dpi=self.dpi,
                        transparent=True
                       )

            #generate KMZ - Offline
            if self.kmz:
                print("Generating KMZ ...")
                self.genKML(figNames, self.srcvars, dims, online=False)

            #generate KML - Online
            if self.kml:
                print("Generating KML ...")
                self.genKML(figNames, self.srcvars, dims)

        #generate animation.
        if self.anim:
            self.genAnim(
                         "%s.%s" % (loopName.replace('loop','*'), self.filefmt),
                         "%s.gif" % loopName
                        )
#            fulloutdir = os.path.join(self.outdir, os.path.dirname(self.img_template))
#            loopName = os.path.basename(loopName)
#            self.genAnim(
#                         fulloutdir,
#                         "%s.%s" % (loopName.replace('loop','*'), self.filefmt),
#                         fulloutdir,
#                         "%s.gif" % loopName
#                        )

        mapNames.append(figNames)

        # restore options without local function parameters
        vars(self).update(localvars)

        #print "Returning ", pltNames
        #return pltNames

#    num = len(mapNames)
#    if num > 1:
#        mg.compareMaps(mapNames, OUTDIR, ssDate, steps, JOINT_TEMPLATE )


    def resetConf(self):
        """ Back to the initial conditions. """

        self.__init__()


    def loadConf(self, section=None, fpath=None, reset=False):
        """ Load existing configurations from file. """

        from .config import readConf

        if fpath == None:
            fpath = parse_path(self.config_dir, self.config_file)
        else:
            fpath = parse_path(self.indir, fpath)

        if not os.path.isfile(fpath):
            print("Error %s" % fpath)
            return

        opts = readConf(section, fpath)
        if section == None:
            return opts

        if reset:
            self.resetConf()
        vars(self).update(parse_parameters(opts))


    def writeConf(self, section, fpath=None):
        """ Write configurations on file. """

        from .config import writeConf

        if fpath == None:
            fpath = parse_path(self.config_dir, self.config_file)
        else:
            fpath = parse_path(self.indir, fpath)

        # create new dir if doesn't exist
        dirname = os.path.dirname(fpath)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        # save current conf
        curropts = copy.deepcopy(vars(self))
        # load defaults
        self.resetConf()
        defaults = copy.deepcopy(vars(self))
        # calculate diff
        diff = {k : curropts[k] for k in curropts if curropts[k]!=defaults[k]}
        # reload diff
        vars(self).update(diff)
        # save diff
        writeConf(section, fpath, diff)
