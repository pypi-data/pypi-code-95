""" Utility functions and classes for SRP

Context : SRP
Module  : SRPGW
Version : 1.0.0
Author  : Stefano Covino
Date    : 23/08/2017
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   :

Remarks :

History : (23/08/2017) First version.
"""


#import SRPGW as GW
import numpy
from photutils import CircularAperture, CircularAnnulus, aperture_photometry
from astropy.table import hstack



def ApyPhot(x,y,data,rds=(5,10,15),backgr=True,gain=1.,ron=0.):
    aperture = CircularAperture((x,y), r=rds[0])
    if backgr:
        baperture = CircularAnnulus((x,y), r_in=rds[1], r_out=rds[2])
        back_table = aperture_photometry(data, baperture, method='subpixel')
    else:
        bg = 0.0
        ebg = 0.0
    #
    flux_table = aperture_photometry(data, aperture, method='subpixel')
    npix = aperture.area()
    #
    if backgr:
        phot_table = hstack([flux_table, back_table], table_names=['raw', 'bkg'])
        bpix = baperture.area()
        bg = phot_table['aperture_sum_bkg'] / bpix
    bkg_sum = bg * npix
    flux = phot_table['aperture_sum_raw'] - bkg_sum
    #
    fluxerr = numpy.sqrt(numpy.fabs(phot_table['aperture_sum_raw'])*gain + numpy.fabs(bkg_sum)*gain + (npix+bpix)*ron)
    #
    return flux,fluxerr
    
