import pandas as pd
import glob
import pickle
import numpy as np
import os
#import pkg_resources
#path = 'botnoiw2v_small.mod'
#modloc = pkg_resources.resource_filename(__name__,path)

#mod = pickle.load(open(modloc))
def sentencevector(sentenceList,mod):
	return mod.transform(sentenceList)