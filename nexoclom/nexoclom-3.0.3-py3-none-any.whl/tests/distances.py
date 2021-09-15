import pickle
import numpy as np
from scipy.spatial import distance, distance_matrix
import timeit


def oldway(packets, xdata, boresight):
    # Old way
    rpr = np.ndarray((len(packets), len(xdata)))
    for i in range(len(xdata)):
        row_pr = xdata[i, :]
        xpr = packets-row_pr[np.newaxis, :]
        #bore = boresight[i, :]
        rpr[:,i] = np.linalg.norm(xpr, axis=1)
        
        # Packet-s/c boresight angle
        #losrad = np.sum(xpr*bore[np.newaxis, :], axis=1)
        # costheta = losrad/rpr
        # costheta[costheta > 1] = 1.
        # costheta[costheta < -1] = -1.
        
    return rpr

def newway(packets, xdata, boresight):
    for i in range(len(xdata)):
        row_pr = xdata[i, :]
        xpr = packets-row_pr[np.newaxis, :]
        bore = boresight[i, :]
        losrad = distance.cdist(xpr, bore[np.newaxis, :],
                                metric=lambda u, v: np.dot(u, v)).flatten()
    
    return losrad

def thirdway(packets, xdata, boresight):
    rpr = distance_matrix(packets, xdata)
    return rpr

packets, xdata, boresight = pickle.load(open('packets.pkl', 'rb'))
#packets = packets[0:1000,:]
#xdata = xdata[0:10,:]
#boresight = boresight[0:10,:]

#print(timeit.timeit('oldway(packets[:,2:5], xdata, boresight)', globals=globals()))
#print(timeit.timeit('newway(packets[:,2:5], xdata, boresight)', globals=globals()))
#print(timeit.timeit('thirdway(packets[:,2:5], xdata, boresight)', globals=globals()))

from datetime import datetime

t0 = datetime.now()
rpr0 = oldway(packets[:,2:5], xdata, boresight)
t1 = datetime.now()
rpr1 = thirdway(packets[:,2:5], xdata, boresight)
t2 = datetime.now()

print(t1-t0, t2-t1)

