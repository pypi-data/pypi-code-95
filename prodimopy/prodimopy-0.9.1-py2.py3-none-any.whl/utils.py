from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from astropy import units as u


def calc_dustcolumnd(model):
  '''
  Calculated the vertical column density for every species at every point
  in the disk (from top to bottom). Very simple and rough method.

  :param model: the ProDiMo model
  :return cd: mass column density for the dust at every point

  TODO: maye put this back into the data structure as util function or both=
  '''
  cd=0.0*model.rhod
  for ix in range(model.nx):
    for iz in range(model.nz-2,-1,-1):  # from top to bottom
      dz=(model.z[ix,iz+1]-model.z[ix,iz])
      dz=dz*u.au.to(u.cm)
      nn=0.5*(model.rhod[ix,iz+1]+model.rhod[ix,iz])
      cd[ix,iz]=cd[ix,iz+1]+nn*dz

  return cd


def load_mplstyle(stylename):
  import matplotlib.pyplot as plt
  styles=plt.style.available
  if stylename in styles:
    plt.style.use(stylename)
    print("INFO: Load "+stylename+" mplstyle.")
  else:
    print("WARN: Could not load "+stylename+" mplstyle.")


def set_param(paramFileList,param,value):
  """

  Utility function that allows to change ProDiMo parameter values in a list
  of ProDiMo Parameters (e.g. read in from Parameter.in)

  This routine cannot deal yet with complex parameter structures. Only works
  with parameters that have a single value.

  Parameters
  ----------
  paramFileList : list()
    The content of the Parameter.in as a list.
    You can get it via `f.readLines()`
    This can also be a list that already includes changed parameters.
    Each entry in the list should correspond to one Parameter.

  param : str
    The ProDiMo Parameter name (without the ! )

  value : str
    the Parameter value. The string will be use as is.
    There are no checks or anything.


  Returns
  -------
  list
    the paramFileList

  """
  replaced=False
  for i in range(len(paramFileList)):
    ip=paramFileList[i].find(param)
    if ip>-1:
      val=paramFileList[i][0:ip-1]
      rest=paramFileList[i][ip:]
      lval=len(val)
      lnewval=len(value)
      if lval>lnewval:
        newval=value+" "*(lval-lnewval)+" "
      elif lval<lnewval:
        newval=value+"  "
      else:
        newval=value+" "
      print(val,rest,lval,lnewval,newval)

      paramFileList[i]=newval+rest
      print("change : ",paramFileList[i])
      replaced=True

  if not replaced:
    paramFileList.append(value+"  "+param+"\n")
    print("append : ",paramFileList[-1])

  return paramFileList
