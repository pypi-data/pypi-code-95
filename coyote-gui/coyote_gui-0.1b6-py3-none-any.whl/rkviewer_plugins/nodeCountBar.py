"""
For development and testing only. Displays a bar graph showing the number of nodes on the canvas,
resetting when it reaches ten.

Version 0.01: Author: Claire Samuels (2021)

"""

from rkviewer import canvas
from rkviewer.canvas.geometry import Rect
import wx
from wx import EvtHandler
from rkviewer.plugin.classes import PluginMetadata, CommandPlugin, PluginCategory
from rkviewer.plugin import api
from rkviewer.plugin.api import Node, Vec2, Reaction, get_node_indices, node_count, reaction_count
from rkviewer.mvc import IDRepeatError
import math
import random as _random
import numpy as _np
import copy as _copy

from rkviewer.events import CanvasDidUpdateEvent, DidAddNodeEvent, DidDeleteEvent, bind_handler, DidPaintCanvasEvent
from rkviewer.config import Color

class NodeCountBar(CommandPlugin):
  metadata = PluginMetadata(
      name='Node Count Bar',
      author='Claire Samuels',
      version='0.0.1',
      short_desc='For development and testing only.',
      long_desc='For development and testing only. Displays a bar graph showing the number of nodes on the canvas, resetting when it reaches ten.',
      category=PluginCategory.UTILITIES,
   )
  def __init__(self):
      """
      Initialize the NodeCountBar.

      Args:
          self

      """
      super().__init__()

  def run(self):
      self.net_index = 0

      self.node_total = api.node_count(self.net_index)

      # DidAddNodeEvent occurs for each node that is added. DidDeleteEvent occurs once per delete,
      # which could include any number of nodes.
      # Alternatively we could use api.node_count(net_index) whenever we need the number of nodes on
      # the canvas, but this is faster
      bind_handler(DidAddNodeEvent, self.node_added)
      bind_handler(DidDeleteEvent, self.nodes_removed)

      bind_handler(DidPaintCanvasEvent, self.show_node_count_meter)

  def node_added(self, evt):
      self.node_total += 1

  def nodes_removed(self, evt):
      self.node_total -= len(evt.node_indices)

  def show_node_count_meter(self, evt):
    ''' Displays a graph in upper left of canvas. Bar size depends on the number of nodes on canvas.
        At 10 nodes, bar is full size'''

    # get graphics context from DidPaintCanvasEvent
    gc = evt.gc

    # draw background
    pen1 = gc.CreatePen(wx.GraphicsPenInfo(wx.Colour(0,0,150)))
    gc.SetPen(pen1)
    brush1 = wx.Brush(wx.Colour(0,0,150), style = wx.BRUSHSTYLE_SOLID)
    gc.SetBrush(brush1)
    bg_w = 20
    bg_h = 50
    bg_x = 20
    bg_y = 20
    gc.DrawRoundedRectangle(bg_x, bg_y, bg_w, bg_h, 2)

    # draw dynamic bar
    pen2 = gc.CreatePen(wx.GraphicsPenInfo(wx.Colour(255,0,50)))
    brush2 = wx.Brush(wx.Colour(255,0,50), style = wx.BRUSHSTYLE_SOLID)
    gc.SetBrush(brush2)
    gc.SetPen(pen2)
    bar = self.rect_from_count(bg_w, bg_h, bg_x, bg_y)
    gc.DrawRoundedRectangle(bar.position.x, bar.position.y, bar.size.x, bar.size.y, 0)

  def rect_from_count(self, background_width, background_height, background_x, background_y):
    ''' Calculate dimensions of bar for node count graph
    '''
    # 4 px buffer
    w = background_width - 8
    h = background_height - 8
    x = background_x + 4
    y = background_y + 4

    # when there are ten nodes, bar is full sized
    ratio =  (self.node_total%11)/10
    adj_h = round(h * ratio)
    # position correctly
    adj_y = background_y + background_height - 4 - adj_h

    return Rect(Vec2(x,adj_y), Vec2(w,adj_h))


