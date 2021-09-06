import astropy.io.fits as pyfits
import healpy
import healtics


from integralclient import converttime
import ephem
from astropy.coordinates import SkyCoord
from astropy import units as u
#import ephem    
from numpy import *

class Visibility:
    def __init__(self,minsolarangle=30):
        self.ijd02=float(converttime("UTC","2002-01-01T00:00:00","IJD"))
        self.ijd12=float(converttime("UTC","2012-01-01T00:00:00","IJD"))
        self.minsolarangle = minsolarangle

    def get_grid(self,nsides):
        theta,phi=healpy.pix2ang(nsides,arange(healpy.nside2npix(nsides)))
        return SkyCoord(phi,theta,1,unit=u.rad,representation="physicsspherical")
        
    def for_time(self,t,coord=None,nsides=16):
        ijd=float(converttime("ANY",t,"IJD"))

        ijd02,ijd12=self.ijd02,self.ijd12

        yeard=(ijd12-ijd02)/10

        year=int((ijd-ijd02)/yeard)
        doy=ijd-ijd02-year*yeard
        
        if coord is None:
            print("get grid...")
            coord=self.get_grid(nsides)        

        
        sun=ephem.Sun(ijd-ijd02-ephem.Date("2002/01/01"))
        sun_coord=SkyCoord(sun.ra,sun.dec,unit=u.rad,representation="spherical")
        
        print("sun coord",sun_coord)

        vmap=zeros(coord.shape[0])
        
        print("will compute map..",coord.shape)
        
        sep=coord.separation(sun_coord).deg
        vmap[(sep>90-self.minsolarangle) & (sep<90+self.minsolarangle)]=1
        
        return vmap
        
