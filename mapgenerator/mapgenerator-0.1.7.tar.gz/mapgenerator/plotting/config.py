# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 Barcelona Supercomputing Center
# @license: https://www.gnu.org/licenses/gpl-3.0.html
# @author: see AUTHORS file

import os
import configargparse as argparse
import configparser
from optparse import OptionParser
import mapgenerator

import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


#def list_callback(option, opt_str, value, parser):
#    setattr(parser.values, option.dest, value.split(','))
#    print("**************", value, type(value))
#    print('\toption:', repr(option))
#    print('\topt_str:', opt_str)
#    print('\tvalue:', value)
#    print('\tparser:', parser)
#    return

class ArgumentParser(object):
    def __init__(self):
        """
        Initialization of the arguments the parser can handle
        """

        try:
            self.parser = argparse.ArgumentParser(description='')
            self.parser.add_argument('-V', '--version', action='version',
                                     version=mapgenerator.__version__,
                                     help="returns MapGenerator version number and exit")
            self.parser.add_argument('--config', #is_config_file=True,
                                    dest="config",
                                     help='specifies the config file to read'
                                     ) #required=False)

            self.parser.add_argument("--section",
                                dest="section",
                                help="config file section to read")
            # main options
            self.parser.add_argument("--srcfiles",
                                dest="srcfiles",
                                help="main source netCDF file")
            self.parser.add_argument("--srcvars",
                                dest="srcvars",
                                help="main variable")
            self.parser.add_argument("--plottype",
                                dest="pltype",
                                choices=['map', 'cross', 'timeseries'],
                                help="type of plots to generate")
            #
            self.parser.add_argument("--loglevel",
                                dest="loglevel",
                                choices=['DEBUG', 'INFO', 'WARNING', 'ERROR',
                                         'CRITICAL'],
                                help="logging levelbug (default=WARNING)")

            self.parser.add_argument("--indir",
                                dest="indir",
                                help="directory where is/are stored the input file(s)")
            self.parser.add_argument("--outdir",
                                dest="outdir",
                                help="directory where is/are to be stored the output file(s)")
            self.parser.add_argument("--file_format",
                                dest="filefmt",
                                help="format of the output file(s) (default=png)")
            self.parser.add_argument("--timesteps",
                                dest="timesteps",
                                nargs="+",
                                help="timesteps to plot (list or 'all' - default=[0])")
            self.parser.add_argument("--bounds",
                                dest="bounds",
                                nargs="+",
                                help="values bounds list (default=None)")
            self.parser.add_argument("--ticks",
                                dest="ticks",
                                help="colorbar ticks list (default=None)")
            self.parser.add_argument("--colors",
                                dest="colors",
                                help="colors list or colormap name (default='jet'), for a list check here: https://matplotlib.org/users/colormaps.html")
            self.parser.add_argument("--lon",
                                dest="lon",
                                nargs="+",
                                help="longitude list")
            self.parser.add_argument("--lat",
                                dest="lat",
                                nargs="+",
                                help="latitude list")
            self.parser.add_argument("--smooth",
                                dest="smooth",
                                help="plot without smoothing (default=True)")
            self.parser.add_argument("--subsetting",
                                dest="subsetting",
                                help="subset according to given lat/lon (default=True)")
            self.parser.add_argument("--nocontourf",
                                dest="nocontourf",
                                help="no contourf")
            self.parser.add_argument("--colorbar",
                                dest="colorbar",
                                help="toggle colorbar (default=True)")
            self.parser.add_argument("--formats",
                                dest="formats",
                                help="colorbar labels format (default=auto)")
            self.parser.add_argument("--extend",
                                dest="extend",
                                choices=['both','max','min'],
                                help="extend colormap extremes (default='neither')")
            self.parser.add_argument("--resolution",
                                dest="resolution",
                                choices=['c','l','i','h','f'],
                                help="details level of coastlines/coutries")
            self.parser.add_argument("--dpi",
                                dest="dpi",
                                help="output image dpi (default=200)")
            self.parser.add_argument("--fontsize",
                                dest="fontsize",
                                help="title fontsize (default=12)")
            self.parser.add_argument("--continents",
                                dest="continents",
                                help="color to fill continents (default=None)")
            self.parser.add_argument("--coordsopts",
                                dest="coordsopts",
                                help="coordinates linewidth, fontsize, color (default=0.3,10,grey)")
            self.parser.add_argument("--coastsopts",
                                dest="coastsopts",
                                help="coastlines linewidth, color (default=0.5,grey)")
            self.parser.add_argument("--countropts",
                                dest="countropts",
                                help="countries linewidth, color (default=0.3,grey)")
            self.parser.add_argument("--anim",
                                dest="anim",
                                help="Toggle Animation (default=False)")
            self.parser.add_argument("--scatter",
                                dest="scatter",
                                help="data file for additional scatter plot")
            self.parser.add_argument("--contours",
                                dest="contours",
                                help="additional contour variable")
            self.parser.add_argument("--keep_aspect",
                              dest="keep_aspect",
                              help="preserve map aspect ratio when drawing (default=False)")
            self.parser.add_argument("--shapefiles",
                              dest="shapefiles",
                              help="additional shape files")
            self.parser.add_argument("--wind",
                              dest="wind",
                              help="wind source file")
            self.parser.add_argument("--windopts",
                              dest="windopts",
                              help="wind options")
            self.parser.add_argument("--xsize",
                              dest="xsize",
                              help="proportion of X dimension (between 0 and 1)")
            self.parser.add_argument("--ysize",
                              dest="ysize",
                              help="proportion of Y dimension (between 0 and 1)")
            self.parser.add_argument("--projection",
                              dest="projection",
                              help="map projection to draw (default=cyl)")
            self.parser.add_argument("--area_thresh",
                              dest="area_thresh",
                              help="area threshold in surface drawing (including lakes)")

            self.parser.add_argument("--title",
                              dest="title",
                              help="title of the figure")
            self.parser.add_argument("--contours_int",
                              dest="contours_int",
                              help="interval between contours")
            self.parser.add_argument("--contours_color",
                              dest="contours_color",
                              help="contours color")
            self.parser.add_argument("--contours_label",
                              dest="contours_label",
                              help="contours label")
#            self.parser.add_argument("--varconds",
#                              dest="varconds",
#                              help="varconds")
            self.parser.add_argument("--dimension",
                              dest="dimension",
                              help="dimension name and operation in the form DIMENSION,OPERATION (mean, max, min, ...) as documented in the numpy reference guide. If OPERATION is a number it will extract the correspondent element")
            self.parser.add_argument("--alpha",
                              dest="alpha",
                              help="alpha value for colormap netween 0 and 1 (default=1)")
            ############
            self.parser.add_argument("--img_template",
                              dest="img_template",
                              help="Image template")
            self.parser.add_argument("--joint_template",
                              dest="joint_template",
                              help="Joint template")
            self.parser.add_argument("--nomap",
                              dest="nomap",
                              help="hide map")
#            self.parser.add_argument("--kml",
#                              dest="kml",
#                              help="generate KML. String with base url (default='')")
            self.parser.add_argument("--kmz",
                              dest="kmz",
                              help="generate KMZ (default=False)")
            self.parser.add_argument("--overwrite",
                              dest="overwrite",
                              help="overwrite outputs (default=True)")
            self.parser.add_argument("--background",
                              dest="background",
                              choices=['bluemarble','shadedrelief','etopo','GIS'],
                              help="background orography (default=None)")
            self.parser.add_argument("--logo",
                              dest="logo",
                              help="put a logo (image path, x, y - default=None)")
#            self.parser.add_argument("--noruntime",
#                              dest="noruntime",
#                              help="no runtime")
#            self.parser.add_argument("--limits",
#                              dest="limits",
#                              help="limits where to put an arrow in the colorbar")
#            self.parser.add_argument("-g", "--gap",
#                              action="store",
#                              dest="gap",
#                              default="",
#                              help="gap between time steps in different sources, specified as the first hour for each source")
#            self.parser.add_argument("-I", "--interval",
#                              action="store",
#                              dest="interval",
#                              default="",
#                              help="interval of time instants")
#            self.parser.add_argument("-f", "--freq",
#                              action="store",
#                              dest="freq",
#                              default="",
#                              help="frequency of time instants")
#            self.parser.add_argument("-T", "--total",
#                              action="store",
#                              dest="total",
#                              default="",
#                              help="total time instants")
#            self.parser.add_argument("-N", "--start-at",
#                              action="store",
#                              dest="start",
#                              default="",
#                              help="starting time")
#            self.parser.add_argument("--transf",
#                              action="store",
#                              dest="transf",
#                              default="",
#                              help="Transform coordinates")
#            self.parser.add_argument("--maxtitle",
#                              action="store",
#                              dest="maxtitle",
#                              default="",
#                              help="title of the max figure")
#            self.parser.add_argument("--max",
#                              action="store",
#                              dest="max",
#                              default="",
#                              help="max")

        except Exception as e:
            log.error('Unhandled exception on MapGenerator: %s' % e, exc_info=True)

    #-----------------------------------------------------------------------
    # Parse arguments and preprocess
    #-----------------------------------------------------------------------
    def parse_args(self, args=None):
        """
        Parse arguments given to an executable
        :param args:
        """
        try:
            #return self.parser.parse_args(args)
            return self.parser.parse_args(args)
        except Exception as e:
            print(e)
            raise mg_exceptions.ArgumentParserException


def readConf(section=None, fpath=None):
    """ Read configuration """

    config = configparser.RawConfigParser()
    config.read(fpath)
    if section == None:
        return config.sections()

    res = {}
    for k, v in config.items(section):
        try:
            res[k] = eval(v)
        except:
            res[k] = v
    return res


def writeConf(section, fpath, opts):
    """ Write configurations on file. """

    config = ConfigParser.RawConfigParser()

    # check if file exists
    if os.path.exists(fpath):
        config.read(fpath)

    # check if section exists
    if not config.has_section(section):
        config.add_section(section)

    # update configuration
    for item in opts:
        val = opts[item]
        config.set(section, item, val)

    # write configuration
    with open(fpath, 'wb') as configfile:
        config.write(configfile)

