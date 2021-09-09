class DisconnectedEventArgs():
  def __init__(self, clientWasConnected = False, exception = None):
    self._clientWasConnected = clientWasConnected
    self._exception = exception

  @property
  def clientWasConnected(self):
    return self._clientWasConnected

  @clientWasConnected.setter
  def clientWasConnected(self, value):
    self._clientWasConnected = value

  @property
  def exception(self):
    return self._exception

  @exception.setter
  def exception(self, value):
    self._exception = value

class MessageReceivedEventArgs():
  def __init__(self, msgType = None, message = None):
    self.__type = msgType
    self.__message = message

  @property
  def type(self):
    return self.__type

  @type.setter
  def type(self, value):
    self.__type = value

  @property
  def message(self):
    return self.__message

  @message.setter
  def message(self, value):
    self.__message = value