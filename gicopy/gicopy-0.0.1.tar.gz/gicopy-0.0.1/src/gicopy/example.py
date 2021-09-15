import numpy as np
from PIL import Image
import pdb, sys, os, time

def cos(x):
    return np.cos(x*np.pi)
def sin(x):
    return np.sin(x*np.pi)
def tan(x):
    return np.tan(x*np.pi)
def get_distance(v1, v2):
    return np.sqrt((v1[0]-v2[0])**2+(v1[1]-v2[1])**2+(v1[2]-v2[2])**2)
def get_length(v):
    return get_distance(v, [0,0,0])
def get_sum(v1, v2):
    return [v2[0]+v1[0], v2[1]+v1[1], v2[2]+v1[2]]
def dot_product(v1, v2):
    return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]
def lin_product(v, l):
    return [v[0]*l, v[1]*l, v[2]*l]

class Vertice:
    vCount = 0
    def __init__(self, index):
        self.index = index
        self.rgb = [0,0,0]
        self.gray = 0
        self.sal = 0
        self.xyz = None
        self.rtf = None
        self.hashxyz = None
        self.neighboridxs = []
        self.neighboragls = []
        self.affiliation = []
        self.max_depth = 3
        Vertice.vCount += 1

    def print_vertice(self):
        print(self.index)
