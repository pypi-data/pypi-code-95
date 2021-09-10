
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
    name='test',
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

        #bind_handler(DidMoveNodesEvent, self.did_move_nodes)
        bind_handler(DidMoveNodesEvent, self.event_callback)
     #   bind_handler(DidCommitDragEvent, self.did_commit_drag) 
        
      #  bind_handler(SelectionDidUpdateEvent, self.selection_did_update)
        #bind_handler(DidMoveCompartmentsEvent, self.did_move_compartments)
        bind_handler(DidMoveCompartmentsEvent, self.event_callback)

        '''
        bind_handler(DidMoveBezierHandleEvent, self.did_move_bezier_handle)
        bind_handler(DidMoveReactionCenterEvent, self.did_move_reaction_center)
        bind_handler(DidAddNodeEvent, self.did_add_node)
        bind_handler(DidDeleteEvent, self.did_delete)
        '''
        bind_handler(DidMoveBezierHandleEvent, self.event_callback)
        bind_handler(DidMoveReactionCenterEvent, self.event_callback)
        bind_handler(DidAddNodeEvent, self.event_callback)
        bind_handler(DidDeleteEvent, self.event_callback)

        '''
        bind_handler(DidAddReactionEvent, self.did_add_reaction)
        bind_handler(DidAddCompartmentEvent, self.did_add_compartment)
        bind_handler(DidChangeCompartmentOfNodesEvent, self.did_change_compartment)
        bind_handler(DidModifyNodesEvent, self.did_modify_nodes)
        '''
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

    def did_modify_nodes(self, evt):
        self.display_text = "DidModifyNodesEvent"

        self.display_text += "\nIndices: " + str(evt.indices)
        self.display_text += "\nBy user: " + str(evt.by_user)

    def did_change_compartment(self, evt):
        self.display_text = "DidChangeCompartmentOfNodesEvent"
        self.display_text += "\nnode ndices: " + str(evt.node_indices)
        self.display_text += "\nOld comp index: " + str(evt.old_compi)
        self.display_text += "\nNew comp index: " + str(evt.new_compi)
        self.display_text += "\nBy user: " + str(evt.by_user)

    def did_add_compartment(self, evt):
        self.display_text = "DidAddCompartmentEvent"
        self.display_text += "\nIndex: " + str(evt.index)

    def did_add_reaction(self, evt):
        self.display_text = "DidAddReactionEvent"
        self.display_text += "\nIndex: " + str(evt.index)

    def did_delete(self, evt):
        self.display_text = "DidDeleteEvent"
        self.display_text += "\nNode Indices: " + str(evt.node_indices)
        self.display_text += "\nReaction Indices: " + str(evt.reaction_indices)
        self.display_text += "\nCompartment Indices: " + str(evt.compartment_indices)

    def did_add_node(self, evt):
        self.display_text = "DidAddNodeEvent"
        self.display_text += "\nNode: " + str(evt.node)

    def did_move_reaction_center(self, evt):
        self.display_text = "DidMoveReactionCenterEvent"
        self.display_text += "\nNet Index: " + str(evt.net_index)
        self.display_text += "\nReaction Index: " + str(evt.reaction_index)
        self.display_text += "\nOffset: " + str(evt.offset)
        self.display_text += "\nDragged: " + str(evt.dragged)

    def did_move_bezier_handle(self, evt):
        self.display_text = ("DidMoveBezierHandleEvent")
        self.display_text += "\nNet Index: " + str(evt.net_index)
        self.display_text += "\nReaction Index: " + str(evt.reaction_index)
        self.display_text += "\nNode Index: " + str(evt.node_index)
        self.display_text += "\nBy Usr: " + str(evt.by_user)
        self.display_text += "\nDirect: " + str(evt.direct)

    def did_move_compartments(self, evt):
        self.display_text = "DidMoveCompartmentsEvent"

        self.display_text += "\nCompartment Indices: " + str(evt.compartment_indices) 
        self.display_text += "\nOffset: " + str(evt.offset)
        self.display_text += "\nDragged: " + str(evt.dragged)
        self.display_text += "\nBy user: " + str(evt.by_user)
    
    def selection_did_update(self, evt):
        self.display_text = "SelectionDidUpdateEvent"
        self.display_text += "\nNode Indices: " + str(evt.node_indices)
        self.display_text += "\nReaction Indices: " + str(evt.reaction_indices)
        self.display_text += "\nCompartment Indices: " + str(evt.compartment_indices)

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

    def did_move_nodes(self, evt):
        self.display_text = "DidMoveNodesEvent"
        self.display_text += "\nNode Indices: " + str(evt.node_indices)
        self.display_text += "\nOffset: " + str(evt.offset)
        self.display_text += "\nDragged: " + str(evt.dragged)
        self.display_text += "\nBy User: " + str(evt.by_user)
        
    def did_commit_drag(self, evt):
        self.display_text = "DidCommitDragEvent"
        self.display_text += "\nSource: " + str(evt.source)
