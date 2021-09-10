"""
For development and testing only.
Version 0.01: Author: Claire Samuels (2021)

"""

from rkviewer import canvas
from rkviewer.canvas.geometry import Rect
import wx
from rkviewer.plugin.classes import PluginMetadata, CommandPlugin, PluginCategory
from rkviewer.plugin import api
#from rkviewer.plugin.api import CustomShape, CustomShapeGroup, Node, Vec2, Reaction, get_node_indices, reaction_count
from rkviewer.mvc import IDRepeatError
import math
import random
import numpy as _np
import copy as _copy

class PluginEvents1(CommandPlugin):
  metadata = PluginMetadata(
      name='plugin event',
      author='Claire Samuels',
      version='0.0.1',
      short_desc='For development and testing only.',
      long_desc='For development and testing only. Draws a bar next to selected node.',
      category=PluginCategory.UTILITIES,
   )
  def __init__(self):
      """
      Initialize.

      Args:
          self

      """
      super().__init__()

  def run(self):
      self.net_index = 0
      bind_handler(DidDeleteEvent, self.add_more_nodes)
 #     bind_handler(DidResizeNodesEvent, chaos)

  def add_more_nodes(self, evt):
  #  node_index = evt.node_indices.pop()
    for i in range(5):
      try:
        api.add_node(self.net_index, id="hydra", size=Vec2(100,30))
      except IDRepeatError:
     #   pos = api.get_node_by_index(self.net_index, node_index).position
     #   id = api.get_node_by_index(self.net_index, node_index).id
        pos = Vec2(300, 300)
        all_ids = []
        ns = api.get_nodes(self.net_index)
        for n in ns:
          all_ids.append(n.id)
        c = 1
        new_id = 'hydra_head_{}'.format(c)
        while new_id in all_ids:
          c += 1
          new_id = 'hydra_head_{}'.format(c)
        api.add_node(self.net_index, id=new_id, size=Vec2(200,30),
                    position=Vec2(pos.x+random.random()*300, pos.y+random.random()*300))

def chaos(evt):
  print("count yourself lucky!")

