
from abc import ABCMeta
from typing import Optional

class ArgoException(Exception,metaclass=ABCMeta):
  pass

class ResponseTimeout(ArgoException):
  def __init__(self, timeout : Optional[float], *args, **kwargs):
    self.timeout = timeout
    super().__init__(f'Timed out waiting for response (timeout = {timeout!r})', *args, **kwargs)
