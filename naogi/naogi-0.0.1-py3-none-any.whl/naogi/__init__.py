from abc import ABC, abstractmethod

class NaogiModel(ABC):
  def __init__(self):
    super()
    self.model = None

  @abstractmethod
  def predict(self):
    pass

  @abstractmethod
  def load_model(self):
    pass

  @abstractmethod
  def prepare(self):
    pass
