
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
from rkviewer.events import *
import math
import random
import numpy as _np
import copy as _copy

class PluginEvents2(CommandPlugin):
    metadata = PluginMetadata(
    name='Info About Events',
    author='Claire Samuels',
    version='0.0.1',
    short_desc='For development and testing only.',
    long_desc='For development and testing only. Listens to events and displays information about them.',
    category=PluginCategory.UTILITIES,
    )

    def __init__(self):
        """ Initialize.

        Args: self """
        super().__init__()

    def run(self):
        self.net_index = 0

        # make text box
        self.display_text = "ready."
        self.paint_id = bind_handler(DidPaintCanvasEvent, self.on_paint)

        # remove the text when the canvas is cleared
        bind_handler(DidNewNetworkEvent, self.remove)

        bind_handler(DidMoveNodesEvent, self.event_callback)
        bind_handler(DidResizeNodesEvent, self.event_callback)

      #  bind_handler(SelectionDidUpdateEvent, self.event_callback)
        bind_handler(DidMoveCompartmentsEvent, self.event_callback)

        bind_handler(DidMoveBezierHandleEvent, self.event_callback)
        bind_handler(DidMoveReactionCenterEvent, self.event_callback)
        bind_handler(DidAddNodeEvent, self.event_callback)
        bind_handler(DidDeleteEvent, self.event_callback)

        bind_handler(DidAddReactionEvent, self.event_callback)
        bind_handler(DidAddCompartmentEvent, self.event_callback)
        bind_handler(DidChangeCompartmentOfNodesEvent, self.event_callback)
        bind_handler(DidModifyNodesEvent, self.event_callback)

        bind_handler(DidModifyReactionEvent, self.event_callback)
        bind_handler(DidModifyCompartmentsEvent, self.event_callback)
        bind_handler(DidUndoEvent, self.event_callback)
        bind_handler(DidRedoEvent, self.event_callback)

    def event_callback(self, evt):
        self.display_text = str(evt)
        for field in evt.__dataclass_fields__:
            value = getattr(evt, field)
            self.display_text += "\n" + str(field) + ": " + str(value)

    def on_paint(self, evt):
        # put contents of self.display_text on canvas
        gc = evt.gc
        font = wx.Font(wx.FontInfo(10))
        gc.SetFont(font, wx.Colour(0,0,0))
        pen1 = gc.CreatePen(wx.GraphicsPenInfo(wx.Colour(0,0,150)))
        gc.SetPen(pen1)
        gc.DrawText(self.display_text, 30, 30)

    def remove(self, evt):
        print("this method ran")
        unbind_handler(self.paint_id)

