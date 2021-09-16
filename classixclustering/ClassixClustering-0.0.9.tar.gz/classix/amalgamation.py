#!python
#cython: language_level=3
#cython: profile=True
#cython: linetrace=True

# CLASSIX: Fast and explainable clustering based on sorting

# License: BSD 3 clause

# Copyright (c) 2021, Stefan Güttel, Xinye Chen
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Python implementation for amalgamation

cimport cython
import numpy as np
cimport numpy as np
from scipy.special import betainc, gamma
ctypedef np.uint8_t uint8
np.import_array()
    
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.binding(True)
cpdef amalgamate(np.ndarray[np.float64_t, ndim=2] data, np.ndarray[np.float64_t, ndim=2] splist, double radius, str method="distance"):
    cpdef list connected_pairs = list()
    cdef double volume, den1, den2, cid
    cdef Py_ssize_t i, j
    cdef unsigned int internum
    cdef np.ndarray[np.float64_t, ndim=2] neigbor_sp, 
    cdef np.ndarray[np.npy_bool, ndim=1, cast=True] index_overlap, c1, c2
    for i in splist[:, 1].astype(int):
        sp1 = splist[int(i), 3:]

        if method == "density":                    
            volume = np.pi**(data.shape[1]/2) * radius**data.shape[1] / gamma(data.shape[1]/2+1)
            index_overlap = np.linalg.norm(splist[:,3:] - sp1, ord=2, axis=-1) <= 2*radius 
            if not np.any(index_overlap):
                continue
            neigbor_sp = splist[index_overlap]
            neigbor_sp = neigbor_sp[neigbor_sp[:,1] > i]
            c1 = np.linalg.norm(data-sp1, ord=2, axis=-1) <= 2*radius
            den1 = np.count_nonzero(c1) / volume
            for j in neigbor_sp[:,1].astype(int):
                sp2 = splist[int(j), 3:]
                c2 = np.linalg.norm(data-sp2, ord=2, axis=-1) <= 2*radius
                den2 = np.count_nonzero(c2) / volume
                if check_if_overlap(sp1, sp2, radius=radius): 
                    internum = np.count_nonzero(c1 & c2)
                    cid = cal_inter_density(sp1, sp2, radius=radius, num=internum)
                    if cid >= den1 or cid >= den2: 
                        connected_pairs.append([i,j]) 

        else:
            index_overlap = np.linalg.norm(splist[:,3:] - sp1, ord=2, axis=-1) <= 1.5*radius  

            if not np.any(index_overlap):
                continue

            neigbor_sp = splist[index_overlap] 
            neigbor_sp = neigbor_sp[neigbor_sp[:,1] > i]
            for j in neigbor_sp[:,1]:
                connected_pairs.append([i,j]) 
    return connected_pairs



cpdef merge_pairs(list pairs):
    """Transform connected pairs to connected groups (list)"""
    
    cdef unsigned int len_p = len(pairs)
    cdef unsigned int maxid = 0
    cdef long long[:] ulabels = np.full(len_p, -1, dtype=int)
    cdef list labels = list()
    cdef list sub = list()
    cdef list com = list()
    cdef Py_ssize_t i, j, ind
    
    for i in range(len_p):
        if ulabels[i] == -1:
            sub = pairs[i]
            ulabels[i] = maxid

            for j in range(i+1, len_p):
                com = pairs[j]
                if check_if_intersect(sub, com):
                    sub = sub + com
                    if ulabels[j] == -1:
                        ulabels[j] = maxid
                    else:
                        for ind in range(len(ulabels)):
                            if ulabels[ind] == maxid:
                                ulabels[ind] = ulabels[j]

            maxid = maxid + 1

    for i in np.unique(ulabels):
        sub = list()
        for j in [ind for ind in range(len_p) if ulabels[ind] == i]:
            sub = sub + pairs[int(j)]
        labels.append(list(set(sub)))
    return labels



# deprecated (24/07/2021)
# def density(num, volume):
#     ''' Calculate the density
#     num: number of objects inside the cluster
#     volume: the area of the cluster
#     '''
#     return num / volume



cpdef check_if_intersect(list g1, list g2):
    """Check if two list have the same elements."""
    return set(g1).intersection(g2) != set()



cpdef check_if_overlap(double[:] starting_point, double[:] spo, double radius, int scale = 1):
    """Check if two groups formed by aggregation overlap
    """
    cdef Py_ssize_t dim
    cdef double[:] subs = starting_point.copy()
    for dim in range(starting_point.shape[0]):
        subs[dim] = starting_point[dim] - spo[dim]
    return np.linalg.norm(subs, ord=2, axis=-1) <= 2 * scale * radius


    

cpdef cal_inter_density(double[:] starting_point, double[:] spo, double radius, int num):
    """Calculate the density of intersection (lens)
    """
    cdef double in_volume = cal_inter_volume(starting_point, spo, radius)
    return num / in_volume




cpdef cal_inter_volume(double[:] starting_point, double[:] spo, double radius):
    """
    Returns the volume of the intersection of two spheres in n-dimensional space.
    The radius of the two spheres is r and the distance of their centers is d.
    For d=0 the function returns the volume of full sphere.
    Reference: https://math.stackexchange.com/questions/162250/how-to-compute-the-volume-of-intersection-between-two-hyperspheres

    """
    
    cdef Py_ssize_t dim
    cdef unsigned int fdim = starting_point.shape[0]
    cdef double[:] subs = starting_point.copy()
    for dim in range(fdim):
        subs[dim] = starting_point[dim] - spo[dim]
    cdef double dist = np.linalg.norm(subs, ord=2, axis=-1) # the distance between the two groups
    if dist > 2*radius:
        return 0
    cdef double c = dist / 2
    return np.pi**(fdim/2)/gamma(fdim/2 + 1)*(radius**fdim)*betainc((fdim + 1)/2, 1/2, 1 - c**2/radius**2)




