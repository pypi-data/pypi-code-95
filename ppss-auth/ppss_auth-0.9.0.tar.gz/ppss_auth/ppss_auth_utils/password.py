from .. import constants
from .i18n import _,__
import re
import hashlib

import os,datetime,logging
l = logging.getLogger('ppssauth')

class chkResult():
  def __init__(self,b,m,*args,**kwargs):
    self.b = b
    self.m = m
    self.args = args
    self.kwargs = kwargs
  def __bool__(self):
    l.info("Bool({}) = {}".format(self.b,bool(self.b) )  )
    return bool(self.b)
  def __str__(self):
    return str(self.m)
  def getMsg(self,request):
    if request:
      return __(request,self.m ).format(*self.args,**self.kwargs)
    else:
      return self.m.format(*self.args,**self.kwargs)

def checkPassword(user,newpassword):
  prevpasslist = user.passowrdhistory
  passworddig = getPasswordDigest(newpassword)
  for prevpass in prevpasslist[0:constants.Conf.passwordpreviousdifferent]:
    l.debug("\n{}\n vs \n{}".format(passworddig, prevpass.password))
    if passworddig == prevpass.password:
      l.warn("password already used on {}".format(prevpass.insertdt))
      return chkResult(False,"password already used on {}",prevpass.insertdt )
  for reexp in constants.Conf.passwordrelist:
    myre = re.compile(reexp)
    if myre.search(newpassword) is None:
      l.info("password {} don't match constaint:{}".format(newpassword,reexp))
      return chkResult(False, "password for user '{}' don't match constaint:{}",user.username,reexp )
  return chkResult(True,"ok")


def getPasswordDigest(password):
  s = hashlib.sha512(password.encode('utf-8'))
  dig = s.hexdigest()
  return dig



