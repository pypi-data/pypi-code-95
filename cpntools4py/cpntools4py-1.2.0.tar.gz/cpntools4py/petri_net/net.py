from .obj.place import Place
from .obj.transition import Transition
from .obj.arc import Arc

class CPN:
  def __init__(self, xml_doc):
    self.__doc = xml_doc
    self.places = self.places()
    self.transitions = self.transitions()
    self.arcs = self.arcs()

  def places(self):
    places = []
    for doc in self.__doc.findall('place'):
      params = {
        'text': doc.find('text').text,
        'type': doc.find('type').find('text').text,
        'initmark': doc.find('initmark').find('text').text
      }
      place = Place(params)
      places.append(place)

    return places

  def transitions(self):
    transitions = []
    for doc in self.__doc.findall('trans'):
      params = {
        'text': doc.find('text').text,
        'time': doc.find('time').find('text').text
      }
      trans = Transition(params)
      transitions.append(trans)

    return transitions
  
  def arcs(self):
    arcs = []
    place_docs = self.__doc.findall('place')
    trans_docs = self.__doc.findall('trans')

    for doc in self.__doc.findall('arc'):
      place_doc = list(filter(lambda e: e.attrib['id'] == doc.find('placeend').attrib['idref'], place_docs))[0]
      trans_doc = list(filter(lambda e: e.attrib['id'] == doc.find('transend').attrib['idref'], trans_docs))[0]
      params = {
        'orientation': doc.attrib['orientation'],
        'placeend': place_doc.find('text').text,
        'transend': trans_doc.find('text').text
      }
      arc = Arc(params)
      arcs.append(arc)
    
    return arcs

  def fetch(self, id):
    nodes = self.places + self.transitions
    for node in nodes:
      if not node.id == id:
        continue

      return node

  def add_place(self, text, color_type, initmark=None):
    texts = list(map(lambda p: p.text, self.places))
    if text in texts:
      raise Exception(f'place {text} exists.')

    if not type(text): 
      raise TypeError(f'argument must be a string: {text}')

    if not type(color_type) == str:
      raise TypeError(f'argument must be a string: {color_type}')

    params = {
      'text': text,
      'type': type,
      'initmark': initmark
    }
    place = Place(params)
    self.places.append(place)

  def add_trans(self, text, time):
    texts = list(map(lambda p: p.text, self.transitions))
    if text in texts:
      raise Exception(f'transition {text} exists.')

    if not type(text) == str:
      raise TypeError(f'argument must be a string: {text}')

    if not (type(time) == int or type(time) == float):
      raise TypeError(f'argument must be a integer or float: {type}')

    params = {
      'text': text,
      'time': str(time),
    }
    trans = Transition(params)
    self.transitions.append(trans)

  def add_arc(self, orientation, placeend, transend):
    place_texts = list(map(lambda p: p.text, self.places))
    trans_texts = list(map(lambda p: p.text, self.transitions))

    if not (type(orientation) == str):
      raise TypeError(f'argument must be a string: {orientation}')

    if not (type(placeend) == str):
      raise ValueError(f'Could not convert {type(placeend)} to string: "{placeend}"')

    if not (type(transend) == str):
      raise ValueError(f'Could not convert {type(transend)} to string: "{transend}"')

    if not (orientation == 'PtoT' or orientation == 'TtoP' or orientation == 'BOTHDIR'):
      raise Exception('direction is either "PtoT", "TtoP", or "BOTHDIR".')

    if not placeend in place_texts:
      raise Exception(f'{placeend} does not exist')

    if not transend in trans_texts:
      raise Exception(f'{transend} does not exist')

    params = {
      'orientation': orientation,
      'placeend': placeend,
      'transend': transend
    }
    trans = Arc(params)
    self.arcs.append(trans)