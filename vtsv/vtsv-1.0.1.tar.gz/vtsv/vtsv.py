#!/usr/bin/env python3
"""basic TSV viewer

usage: vtsv file1[ file2 [...]]
"""
# 2021-07-23 sokol@insa-toulouse.fr
# Copyright 2021, INRAE/INSA/CNRS

## imports
import sys
import os
from pathlib import Path
import getopt
import re

import wx
import wx.grid
import wx.adv
import wx.lib.colourdb
from wx.lib.wordwrap import wordwrap
from wx.lib.intctrl import IntCtrl
import wx.html
#import wx.html2
import webbrowser

import numpy as np

import vtsv
dirx=Path(sys.argv[0]).resolve().parent; # execution dir
diri=Path(vtsv.__file__).resolve().parent; # install dir

# timeit
from time import strftime, localtime, process_time as tproc
globals()["_T0"]=tproc()
def timeme(s="", dig=2):
    "if a global variable TIMEME is True and another global variable _T0 is set, print current CPU time relative to _T0. This printing is preceded by a message from 's'"
    if TIMEME:
        if "_T0" in globals():
            print(s, ":\tCPU=", round(tproc()-_T0, dig), "s", sep="")
        else:
            globals()["_T0"]=tproc()

TIMEME=False

## custom classes
class f2grid(wx.grid.Grid):
    "read a SV file and show it in a grid"
    def __init__(self, parent, f, *args, **kwargs):
        #import pdb; pdb.set_trace()
        parent.f=f
        self._grid=super(type(self), self)
        self._grid.__init__(parent, *args, **kwargs)
        rows=f.read_text().splitlines()
        #import pdb; pdb.set_trace()
        if rows[-1] == "":
            rows=rows[:-1]
        nrow=len(rows)
        self.nrow=nrow
        if nrow == 0:
            err_mes("File '%s' is empty"%f.name)
            return
        for i in range(nrow):
            rows[i]=rows[i].split("\t")
        ncol=max(len(r) for r in rows)
        self.ncol=ncol
        # create numpy array
        self.arr=np.array([r + [None]*(ncol-len(r)) for r in rows]).astype(object)
        # destroy previous grid
        if "grid" in dir(parent):
            parent.grid.Destroy()
        self.CreateGrid(nrow, ncol)
        self.EnableEditing(True)
        parent.grid=self
        #import pdb; pdb.set_trace()
        for i,r in enumerate(rows):
            for j,v in enumerate(r):
                self.SetCellValue(i, j, v)
            if len(r) < ncol:
                #import pdb; pdb.set_trace()
                for j in range(len(r), ncol):
                    self.SetReadOnly(i, j)
        self.AutoSizeColumns(setAsMin=False)
        self.AutoSizeRows(setAsMin=False)
        if not parent.GetSizer():
            parent.SetSizer(wx.BoxSizer(wx.VERTICAL))
        parent.GetSizer().Add(self, 1, wx.EXPAND)
        self.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.OnCellSel)
        self.Bind(wx.grid.EVT_GRID_EDITOR_HIDDEN, self.OnCellSel)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGING, OnEdit)
    def OnCellSel(self, evt):
        "Show the cell content in the status bar"
        global ir, jc, ktab
        #print("evt has\n", dir(evt))
        #import pdb; pdb.set_trace()
        ir,jc=evt.Row,evt.Col
        gui.txt_cell.SetLabel("%s%s: "%(self.GetColLabelValue(jc), self.GetRowLabelValue(ir)))
        # make this cell non editable if it did not exist in original file
        if self.arr[ir, jc] is None:
            gui.tctl_cell.ChangeValue("uneditable")
            gui.tctl_cell.Disable()
        else:
            gui.tctl_cell.ChangeValue(self.GetCellValue(ir,jc))
            gui.tctl_cell.Enable()
        evt.Skip()
## global vars
me="vtsv"; # program name
gui=wx.Object()
fdata=[]; # names of data files
wd=""
version=""

ir=-1 # i row selected
jc=-1 # j column selected
ktab=-1 # k tab selected
edited=set()
findme={}

with (diri/"licence_en.txt").open() as fp:
    licenseText=fp.read()
with (diri/"version.txt").open() as fp:
    version=fp.read().strip()

## call back functions
def OnExit(evt):
    """
    This is executed when the user clicks the 'Exit' option
    under the 'File' menu or close the window.  We ask the user if he *really*
    want to exit, then close everything down if he does.
    """
    global fdata
    if not fdata or not edited:
        gui.mf.Destroy()
        return
    dlg=wx.MessageDialog(None, 'Some files are not saved. Exit anyway?', 'Choose Yes or No!', wx.YES_NO | wx.ICON_QUESTION)
    if dlg.ShowModal() == wx.ID_YES:
        dlg.Destroy()
        gui.mf.Destroy()
    else:
        dlg.Destroy()
def OnOpen(evt):
    """
    This is executed when the user clicks the 'Open' option
    under the 'File' menu.  We ask the user to choose a TSV file.
    """
    win=evt.GetEventObject()
    win=win.GetWindow()
    with wx.FileDialog(None, defaultDir=str(wd), wildcard="Spreadsheets (*.tsv;*.txt;*.csv;)|*.tsv;*.txt;*.csv|Special files (*.kvh;*.ftbl)|*.kvh;*.ftbl|All files (*.*)|*.*",
        style=wx.FD_OPEN) as dlg:
        if dlg.ShowModal() == wx.ID_OK:
            # proceed the data file
            f2nb(Path(dlg.GetPath()).resolve())
            OnTabSel(None)
            # resize
            w,h=gui.mf.GetSize()
            gui.mf.SetSize(w+1,h+1)
            wx.CallAfter(gui.mf.SetSize, w,h)
def OnSave(evt):
    "Save all opened tabs in corresponding files"
    global edited
    #import pdb; pdb.set_trace()
    for ktab in edited.copy():
        pg=gui.nb.pages[ktab]
        g=pg.grid
        text="\n".join("\t".join(g.arr[ir, jc] for jc in range(g.ncol) if g.arr[ir, jc] is not None) for ir in range(g.nrow))
        if text[-1] != "\n":
            text += "\n"
        fdata[ktab].write_text(text)
        gui.sbar.SetStatusText("File '%s' was saved"%fdata[ktab].name)
        edited.remove(ktab)
def OnFind(evt):
    "Find and select a cell having searched text"
    global findme, ir, jc, ktab
    #print("onfind here, evt=", evt)
    #import pdb; pdb.set_trace()
    #val=gui.tctl_find.GetValue()
    val=evt.GetString()
    ktab=gui.nb.GetSelection()
    upw=gui.chk_up.GetValue()
    g=gui.nb.pages[ktab].grid
    #print("g=", g, "\narr=\n", g.arr)
    if findme and findme["target"] == val and findme["ktab"] == ktab:
        # just move to the next occurrence
        if len(findme["wh"][0]):
            findme["i"]=(findme["i"]+(-1 if upw else 1))%len(findme["wh"][0])
        else:
            # nothing to do: string not found
            gui.sbar.SetStatusText("not found")
            return
    else:
        # create new findme struct
        findme["target"]=val
        findme["ktab"]=ktab
        findme["wh"]=np.where((np.char.find(g.arr.astype(str), val) >= 0) & (g.arr != None))
        if len(findme["wh"][0]) == 0:
            gui.sbar.SetStatusText("not found")
            return;
        else:
            gui.sbar.SetStatusText("")
        #import pdb; pdb.set_trace()
        if upw:
            # find the last occurrence before the current cell
            i=np.where(((findme["wh"][0] == ir) & (findme["wh"][1] < jc)) | (findme["wh"][0] < ir))[0]
            i=len(findme["wh"][0])-1 if len(i) == 0 else i[0]
        else:
            # find the first occurrence after the current cell
            i=np.where(((findme["wh"][0] == ir) & (findme["wh"][1] > jc)) | (findme["wh"][0] > ir))[0]
            i=0 if len(i) == 0 else i[0]
        findme["i"]=i
    ir,jc=findme["wh"][0][findme["i"]],findme["wh"][1][findme["i"]]
    g.GoToCell(ir, jc)
def OnAbout(evt):
    "show about dialog"
    win=evt.GetEventObject()
    win=win.GetWindow()
    info = wx.adv.AboutDialogInfo()
    info.SetName(me)
    info.SetVersion(version)
    info.SetCopyright("(C) 2021 INRAE/INSA/CNRS")
    info.SetDescription(wordwrap(
        "vtsv is a basic TSV (tab separated values) format viewer/editor. "
        "\nBased on wxPython."
        ,
        350, wx.ClientDC(win)))
    info.SetWebSite("https://pypi.org/project/vtsv")
    info.AddDeveloper("Serguei SOKOL")

    info.SetLicense(wordwrap(licenseText, 500, wx.ClientDC(win)))

    # Then we call wx.AboutBox giving it that info object
    wx.adv.AboutBox(info)
def OnSize(evt):
    "main window is resized"
    win=evt.GetEventObject()
    sz=evt.GetSize()
    win.SetSize(sz)
    evt.Skip()
def OnEdit(evt):
    "Trasfer tctl_cell content to a corresponding grid cell"
    global ir, jc, ktab, findme
    if ir == -1 or jc == -1:
        return
    ktab=gui.nb.GetSelection()
    edited.add(ktab)
    pg=gui.nb.pages[ktab]
    
    if evt.EventType == wx.grid.EVT_GRID_CELL_CHANGING.typeId:
        val=evt.GetString()
        #print("ir=", ir, "jc=", jc, "readonly ?", pg.grid.IsReadOnly(ir, jc))
    else:
        val=gui.tctl_cell.GetValue()
    pg.grid.SetCellValue(ir, jc, val)
    gui.tctl_cell.ChangeValue(val)
    pg.grid.arr[ir, jc]=val
    findme={}
    #print("val=", val, "pg=", pg, "\ng=", pg.grid, "\narr=\n", pg.grid.arr)
    #import pdb; pdb.set_trace()
def OnTabSel(evt):
    "Change win title when tab is changed"
    #import pdb; pdb.set_trace()
    gui.mf.SetTitle("%s: %s"%(me, fdata[gui.nb.GetSelection()].name))
def OnGoto(evt):
    "Select first cell on the asked line"
    global ktab
    i=gui.ictl_goto.GetValue()-1
    ktab=gui.nb.GetSelection()
    g=gui.nb.pages[ktab].grid
    i=min(i, g.nrow-1)
    i=max(i, 0)
    g.GoToCell(i, 0)
    gui.ictl_goto.ChangeValue(i+1)
def OnHelp(evt):
    "Open help window in a separate window"
    gui.help.Show()
def OnLinkClicked(evt):
    webbrowser.open_new_tab(evt.GetLinkInfo().Href);
def OnHelpClose(evt):
    evt.EventObject.Hide()

# helpers
def err_mes(mes):
    "Show error dialog in GUI mode or raise exception"
    dlg=wx.MessageDialog(None, mes, "Error", wx.OK | wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()
def warn_mes(mes):
    "Show info dialog in GUI mode or print on stderr"
    if dogui:
        dlg=wx.MessageDialog(None, mes, "Warning", wx.OK | wx.ICON_WARNING)
        dlg.ShowModal()
        dlg.Destroy()
    else:
        print(me+": "+mes, file=sys.stderr)
def usage():
    print(__doc__)
def f2nb(f):
    "Read path 'f' and show its content in a new tab/grid"
    global fdata, edited, ktab
    #import pdb; pdb.set_trace()
    # check if already opened
    fi=[i for i,v in enumerate(fdata) if v == f]
    if fi:
        ktab=fi[0]
        if ktab in edited:
            dlg=wx.MessageDialog(None, f"File '%s' was not saved. Reload anyway?"%f.name, "Choose Yes or No!", wx.YES_NO | wx.ICON_QUESTION)
            if dlg.ShowModal() == wx.ID_NO:
                return
        pg=gui.nb.pages[ktab]
        gui.nb.SetSelection(ktab)
    else:
        ktab=len(gui.nb.pages)
        pg=wx.Panel(gui.nb, size=(100,50))
        gui.nb.AddPage(pg, f.name)
        gui.nb.pages.append(pg)
        fdata.append(f)
        gui.nb.SetSelection(ktab)
        #import pdb; pdb.set_trace()
    grid=f2grid(pg, f)
    
    #import pdb; pdb.set_trace()
    if grid.nrow == 0:
        pg.Destroy()
        del(gui.nb.pages[ktab])
        del(fdata[ktab])
        edited.remove(ktab)
        if ktab:
            ktab -= 1
        if ktab >= 0:
            gui.nb.SetSelection(ktab)

def make_gui():
    "create GUI"
    global gui
    gui=wx.Object()
    gui.app=wx.App()
    wx.lib.colourdb.updateColourDB()
    # main frame
    gui.mf=wx.Frame(None, size=(800,600))
    gui.mf.SetTitle(me)
    gui.sbar=gui.mf.CreateStatusBar()
    # menu
    gui.mbar=wx.MenuBar()
    gui.fmenu=wx.Menu()
    gui.fmenu.Append(wx.ID_OPEN, "&Open\tCtrl-O", "Open file with tab separated values")
    gui.fmenu.Append(wx.ID_SAVE, "&Save\tCtrl-S", "Save all edited files")
    gui.fmenu.AppendSeparator()
    gui.fmenu.Append(wx.ID_EXIT, "&Quit\tCtrl-Q", "Exit the program")
    gui.hmenu=wx.Menu()
    gui.btn_help=gui.hmenu.Append(wx.ID_ANY, "Content")
    gui.hmenu.Append(wx.ID_ABOUT, "&About")
    gui.mbar.Append(gui.fmenu, '&File')
    gui.mbar.Append(gui.hmenu, '&Help')
    gui.mf.SetMenuBar(gui.mbar)
    # toolbar
    gui.tbar=gui.mf.CreateToolBar()
    gui.txt_cell=wx.StaticText(gui.tbar, label="Cell Id: ")
    gui.tctl_cell=wx.TextCtrl(gui.tbar, size=(200, -1))
    #gui.txt_find=wx.StaticText(gui.tbar, label="Find: ")
    gui.sctl_find=wx.SearchCtrl(gui.tbar, size=(200, -1), style=wx.TE_PROCESS_ENTER)
    gui.chk_up=wx.CheckBox(gui.tbar, label="up")
    gui.txt_goto=wx.StaticText(gui.tbar, label="  Goto line: ")
    gui.ictl_goto=IntCtrl(gui.tbar, style=wx.TE_PROCESS_ENTER)
    gui.tbar.AddControl(gui.txt_cell)
    gui.tbar.AddControl(gui.tctl_cell)
    gui.tbar.AddSeparator()
    #gui.tbar.AddControl(gui.txt_find)
    gui.tbar.AddControl(gui.sctl_find)
    gui.tbar.AddControl(gui.chk_up)
    gui.tbar.AddSeparator()
    gui.tbar.AddControl(gui.txt_goto)
    gui.tbar.AddControl(gui.ictl_goto)
    gui.tbar.Realize()
    # general layout
    gui.nb=wx.Notebook(gui.mf, style=wx.NB_BOTTOM)
    gui.nb.pages=[] # will contain tabs
    gui.mf.SetSizer(wx.BoxSizer(wx.VERTICAL))
    gui.mf.GetSizer().Add(gui.nb, 1, wx.EXPAND|wx.ALL)
    gui.mf.Bind(wx.EVT_MENU, OnOpen, id=wx.ID_OPEN)
    gui.mf.Bind(wx.EVT_MENU, OnSave, id=wx.ID_SAVE)
    gui.mf.Bind(wx.EVT_MENU, OnExit, id=wx.ID_EXIT)
    gui.mf.Bind(wx.EVT_MENU, OnAbout, id=wx.ID_ABOUT)
    gui.mf.Bind(wx.EVT_CLOSE, OnExit)
    gui.mf.Bind(wx.EVT_SIZE, OnSize)
    gui.mf.Bind(wx.EVT_TEXT, OnEdit, gui.tctl_cell)
    #gui.mf.Bind(wx.EVT_TEXT, OnFind, gui.tctl_find)
    gui.mf.Bind(wx.EVT_SEARCH, OnFind, gui.sctl_find)
    gui.mf.Bind(wx.EVT_TEXT_ENTER, OnFind, gui.sctl_find)
    gui.mf.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, OnFind, gui.sctl_find)
    gui.mf.Bind(wx.EVT_TEXT_ENTER, OnGoto, gui.ictl_goto)
    gui.mf.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, OnTabSel, gui.nb)
    gui.mf.Bind(wx.EVT_MENU, OnHelp, gui.btn_help)
    gui.mf.Center()
    # help init
    gui.help=wx.Frame(gui.mf, size=(800,600))
    gui.help.browser=wx.html.HtmlWindow(gui.help)
    gui.help.browser.Bind(wx.html.EVT_HTML_LINK_CLICKED, OnLinkClicked)
    gui.help.Bind(wx.EVT_CLOSE, OnHelpClose)
    gui.help.Bind(wx.EVT_SIZE, OnSize)
    fhelp=diri/"../help/vtsv.htm"
    if not fhelp.is_file():
        fhelp=diri/"help/vtsv.htm"
    gui.help.browser.LoadFile(str(fhelp))
    # show starts here
    gui.mf.Show(True)
## take arguments
def main(args=sys.argv[1:]):
    make_gui()
    for f in args:
        f2nb(Path(f).resolve())
        OnTabSel(None)
    gui.app.MainLoop()
if __name__ == "__main__":
    main()
