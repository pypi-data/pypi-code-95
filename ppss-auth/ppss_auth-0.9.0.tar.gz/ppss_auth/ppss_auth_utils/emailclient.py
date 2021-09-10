from ..constants import Conf

__emailclient =None
def getClient():
  if __emailclient is None:
    __emailclient = __Email()

class __Email():
  def __init__(self,user,password,host,port):
    self.user = user
    self.password = password
    self.host = host
    self.port = port


  def sendActivationEmail(self,newuser,tpl = Conf.activationemailtpl):
    pass
