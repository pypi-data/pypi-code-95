import numpy as np
import math

def findZeros(values, axis=None, start=0, end=-1):
  def getX(index):
    if (axis is None):
      return index
    lo = math.floor(index)
    alpha = index - lo
    if (alpha == 0.0):
      return axis[lo]
    else:
      return (1-alpha)*axis[lo] + alpha*axis[lo+1]

  n = values.size
  if (end<0):
    end = n + end
  if (start<0):
    start = n + start
  
  lastval = values[start]
  result = []

  for i in range(start+1, end+1):
    nextval = values[i]
    if (nextval==0.0):
      result.append(getX(i))
    elif (lastval*nextval < 0.0):
      result.append(getX( i - nextval/(nextval-lastval) ))
    lastval = nextval
  
  return np.array(result)

