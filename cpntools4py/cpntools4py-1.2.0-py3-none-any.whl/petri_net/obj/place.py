class Place:
  def __init__(self, params):
    self.text = params['text']
    self.type = params['type']
    self.__initmark = params['initmark']

  def __repr__(self):
    return f'<Place(text={self.text}, type={self.type}, tokens={self.tokens})>'

  def __str__(self):
    return str(self.__dict__)

  def __eq__(self, other):
    if not isinstance(other, Place):
        return False
    return self.text == other.text

  def __hash__(self):
      return hash(self.text)

  @property
  def tokens(self):
    if self.__initmark is None:
      return

    if self.type == 'UNIT':
      token = self.__initmark.replace('`()','')
      return int(token)
    else:
      tokens = []
      for text in self.__initmark.replace('\n','').split('++'):
        token = text.split('`')
        tokens += [token[1]] * int(token[0])

      return tokens