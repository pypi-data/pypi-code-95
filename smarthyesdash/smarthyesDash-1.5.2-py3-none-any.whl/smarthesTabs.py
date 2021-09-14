import datetime as dt, pickle, time, os,re,pandas as pd
import dash, dash_core_components as dcc, dash_html_components as html, dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.express as px, plotly.graph_objects as go
from dorianUtils.utilsD import Utils
from dorianUtils.dccExtendedD import DccExtended
from dorianUtils.dashTabsD import TabMaster,TabSelectedTags,TabUnitSelector,TabMultiUnits
import smarthyesDash.configFilesSmarthyes as cfs

class SmarthyesTab(TabMaster):
    def __init__(self,app,baseId):
        TabDataTags.__init__(self,app,baseId)

class MultiUnitSmarthyesTab(TabMultiUnits):
    def __init__(self,folderPkl,app,baseId='mut0_'):
        self.cfg = cfs.ConfigFilesSmarthyes(folderPkl)
        TabMultiUnits.__init__(self,folderPkl,self.cfg,app,baseId)
        self.tabLayout = self._buildLayout(widthG=85,initialTags=[])
        self._define_callbacks()

class TagSelectedSmarthyesTab(TabSelectedTags):
    def __init__(self,folderPkl,app,baseId='tst0_'):
        self.cfg = cfs.ConfigFilesSmarthyes(folderPkl)
        TabSelectedTags.__init__(self,folderPkl,self.cfg,app,baseId)
        self.tabLayout = self._buildLayout(widthG=85,tagCatDefault='CEAEANAFour_°C')
        self._define_callbacks()

class UnitSelectorSmarthyesTab(TabUnitSelector):
    def __init__(self,folderPkl,app,baseId='tst0_'):
        self.cfg = cfs.ConfigFilesSmarthyes(folderPkl)
        TabUnitSelector.__init__(self,folderPkl,self.cfg,app,baseId)
        self.tabLayout = self._buildLayout(widthG=80,unitInit='V',patTagInit='')
        self._define_callbacks()
