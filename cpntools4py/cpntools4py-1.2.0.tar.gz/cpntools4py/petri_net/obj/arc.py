class Arc:
  def __init__(self, params):
    self.orientation = params['orientation']
    self.placeend = params['placeend']
    self.transend = params['transend']


  def __repr__(self):
    return f'<Arc(orientation={self.orientation}, placeend={self.placeend}, transend={self.transend})>'

  def __str__(self):
    return str(self.__dict__)

  # def __eq__(self, other):
  #   if not isinstance(other, Arc):
  #       return False
  #   return self.text == other.id

  def __hash__(self):
      return hash(self.id)
