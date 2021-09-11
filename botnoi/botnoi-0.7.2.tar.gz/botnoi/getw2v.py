import pandas as pd
import glob
from pythainlp.tokenize import word_tokenize
import pickle
import numpy as np
import os
#import pkg_resources
#path = 'botnoiw2v_small.mod'
#modloc = pkg_resources.resource_filename(__name__,path)

#mod = pickle.load(open(modloc))
def sentencevector(senList,mod):
	vecList = []
	for i in range(len(senList)):
		sen = senList[i]
		print('encode: %i/%i'%(i+1,len(senList)))
		wList = word_tokenize(str(sen),engine='newmm')
		wvec = []
		for w in wList:
			try:
				wvec.append(mod[w])
			except:
				pass
		if len(wvec)==0:
			vec = np.zeros(50)
		else:
			vec = np.mean(wvec,0)
		vecList.append(vec)
	return vecList