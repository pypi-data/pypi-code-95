"""
another test plugin. purpose is to ensure that concentration features in api.py work.
"""
import wx
from rkviewer.plugin.classes import PluginMetadata, CommandPlugin, PluginCategory
from rkviewer.plugin import api
from rkviewer.plugin.api import Node, Vec2, Reaction
from rkviewer.mvc import IDRepeatError
import math
import random as _random
import numpy as _np
import copy as _copy

class Concentration(CommandPlugin):
  metadata = PluginMetadata(
      name='concentration',
      author='Claire Samuels',
      version='0.0.1',
      short_desc='concentration.',
      long_desc='uses api features for editing node concentrations.',
      category=PluginCategory.UTILITIES,
   )
  def __init__(self):
      """
      Initialize the DuplicateReaction.

      Args:
          self

      """
      super().__init__()

  def run(self):

    net = 0

    # create a node with a specified concentration
    n0Idx = api.add_node(net, "n_0", concentration=5.1)

    # 1. ensure that it really does have that concentration
    n0 = api.get_node_by_index(net, n0Idx)
    if not n0.concentration == 5.1:
        print("failed check 1")
    else:
        print("passed check 1")

    # create a node without a specified concentration
    n1Idx = api.add_node(net, "n_1")

    # 2. ensure default concentration is correct
    n1 = api.get_node_by_index(net, n1Idx)
    if not n1.concentration == 0.0:
        print("failed check 2")
    else:
        print("passed check 2")

    # change the concentration
    api.update_node(net, n1Idx, concentration=2)

    # 3. ensure concentration still right
    if api.get_node_by_index(net, n1Idx).concentration == 2:
        print("passed check 3")
    else:
        print("failed check 3")

    # change some other features of the node
    api.update_node(net, n1Idx, border_width=15, shape_index=1)

    # 4. concentration still good?
    if api.get_node_by_index(net, n1Idx).concentration == 2:
        print("passed check 4")
    else:
        print("failed check 4")

    # 5. create a node with an invalid concentration value
    try:
        n2Idx = api.add_node(net, "n_2", position=Vec2(100,100), concentration=-1)
    except ValueError as err:
        print("passed check 5 by throwing " + str(err))

    # 6. change a concentration to something invalid
    try:
        api.update_node(net, n1Idx, concentration=-100)
    except ValueError as err:
        print("passed check 6 by throwing " + str(err))
