import xml.etree.ElementTree as ET
import snakes.plugins
snakes.plugins.load("gv", "snakes.nets", "nets")
from nets import PetriNet, Place, Transition, Value, Expression

def read_xml(file_path):
  tree = ET.parse(file_path)
  root = tree.getroot().find('cpnet').find('page')

  return root

def to_snakes(cpn):
  net = PetriNet("snakes")
  for place in cpn.places:
    p = Place(place.text, place.tokens or [])
    net.add_place(p)

  for trans in cpn.transitions:
    t = Transition(trans.text, Expression(str(trans.time or 0)))
    net.add_transition(t)

  for arc in cpn.arcs:
    placeend = cpn.fetch(arc.placeend)
    transend = cpn.fetch(arc.transend)
    if arc.orientation == 'PtoT':
      net.add_input(placeend.text, transend.text, Value(0))
    elif arc.orientation == 'TtoP':
      net.add_output(placeend.text, transend.text, Value(0))
    elif arc.orientation == 'BOTHDIR':
      net.add_input(placeend.text, transend.text, Value(0))
      net.add_output(placeend.text, transend.text, Value(0))

  return net