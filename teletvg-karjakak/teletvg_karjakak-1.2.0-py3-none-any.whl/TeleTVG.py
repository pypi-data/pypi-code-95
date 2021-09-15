# -*- coding: utf-8 -*-
#Copyright (c) 2020, KarjaKAK
#All rights reserved.

from telethon import TelegramClient, functions, types
from tkinter import *
from tkinter import ttk, messagebox, simpledialog, filedialog
from datetime import datetime as dt, timedelta
from contextlib import redirect_stdout
from Clien.clien import cmsk, reading
import string
import asyncio
import shutil
from . import emo
import os
import sys
import json
import re
import io
import ast
from sys import platform
from pathlib import Path


class Reminder:
    """
    Building Reminder Telegram to help remind a friend or yourself.
    """
    API = None
    HASH_ = None
    RESZ = None
    STOP_A = False
    def __init__(self, root):
        self.root = root
        self.root.title('TeleTVG')
        self.orip = Path(os.getcwd())
        self.plat = platform        
        self.wid = 705
        self.hei = 650
        self.root.minsize(705, 650)
        self.pwidth = int(self.root.winfo_screenwidth()/2 - self.wid/2)
        self.pheight = int(self.root.winfo_screenheight()/3 - self.hei/3)
        self.root.geometry(f'{self.wid}x{self.hei}+{self.pwidth}+{self.pheight}')
        self.RESZ = f'{self.wid}x{self.hei}+{self.pwidth}+{self.pheight}'
        gem = None
        if os.path.exists(os.path.join(self.orip.parent, 'telgeo.tvg')):
            with open(os.path.join(self.orip.parent, 'telgeo.tvg'), 'rb') as geo:
                try:
                    gem = ast.literal_eval(geo.read().decode('utf-8'))
                except:
                    messagebox.showerror(
                        'TeleTVG', 
                        'Unabale to set geometry because file setting is corrupted!'
                    )
                else:
                    self.root.geometry(gem['geo'])
                    self.RESZ = gem['geo']
        del gem
        self.root.protocol('WM_DELETE_WINDOW', self.winexit)
        self.root.bind('<Control-p>', self.paste)
        self.root.bind('<Control-c>', self.copc)
        self.root.bind('<Control-x>', self.clear)
        self.root.bind('<Control-o>', self.stopauto)
        self.root.bind('<Control-m>', self.multiselect)
        self.root.bind('<Control-s>', self.rectext)
        self.root.bind('<Control-d>', self.delscreen)
        if self.plat. startswith('win'):
            self.root.bind('<Control-F1>', self.help)
        else:
            self.root.bind('<Key-F1>', self.help)
        self.seconds = None
        self.langs = None
        self.chacc = None
        self.lock = False
        self.afterid = None
        self.refidx = None
        self.upt = tuple()
        self.sel = []
        self.result = None
        self.api_id = Reminder.API
        self.api_hash = Reminder.HASH_
        del Reminder.API, Reminder.HASH_
        self.users = {}
        if self.plat.startswith('win'):
            self.stl = ttk.Style(self.root)
            self.stl.theme_use('clam')
        self.frm1 = ttk.Frame(self.root)
        self.frm1.pack(fill = 'x')
        self.lab1 = ttk.Label(self.frm1, text = 'To:', justify = RIGHT)
        self.lab1.pack(side = LEFT, padx = (2, 7), pady = 5)
        self.entto = ttk.Combobox(self.frm1)
        self.entto.pack(side = LEFT, pady = 5, padx = (0, 5), fill = 'x', expand = 1)
        self.entto.bind('<KeyRelease>', self.tynam)
        self.frm2 = ttk.Frame(self.root)
        self.frm2.pack(fill = 'x')
        self.bem = Button(
            self.frm2, 
            text = 'EMOJI', 
            font = 'consolas 10 bold', 
            relief = GROOVE, 
            command = self.emj, 
            width = 4
        )
        self.bem.pack(side = LEFT, padx = 2, pady = (0, 5), fill = 'x', expand = 1)        
        self.bup = Button(
            self.frm2, 
            text = 'PASTE', 
            font = 'consolas 10 bold', 
            relief = GROOVE, 
            command = self.paste, 
            width = 4
        )
        self.bup.pack(side = LEFT, padx = 2, pady = (0, 5), fill = 'x', expand = 1)
        self.buo = Button(
            self.frm2, 
            text = 'COPIED', 
            font = 'consolas 10 bold', 
            relief = GROOVE, 
            command = self.copc, 
            width = 4
        )
        self.buo.pack(side = LEFT, padx = 2, pady = (0, 5), fill = 'x', expand = 1)        
        self.buc = Button(
            self.frm2, 
            text = 'CLEAR', 
            font = 'consolas 10 bold', 
            relief = GROOVE, 
            command = self.clear, 
            width = 4
        )
        self.buc.pack(side = LEFT, padx = 2, pady = (0, 5), fill = 'x', expand = 1)      
        self.bsel = Button(
            self.frm2, 
            text = 'MULTI', 
            font = 'consolas 10 bold', 
            relief = GROOVE, 
            command = self.multiselect, 
            width = 4
        )
        self.bsel.pack(side = LEFT, padx = 2, pady = (0, 5), fill = 'x', expand = 1)
        self.bedm = Button(
            self.frm2, 
            text = 'ED MULTI', 
            font = 'consolas 10 bold', 
            relief = GROOVE, 
            command = self.editmu, 
            width = 4
        )
        self.bedm.pack(side = LEFT, padx = 2, pady = (0, 5), fill = 'x', expand = 1)
        self.bau = Button(
            self.frm2, text = 'AUTO SAVE', 
            font = 'consolas 10 bold', 
            relief = GROOVE, 
            command = self.rectext, 
            width = 4
        )
        self.bau.pack(side = LEFT, padx = 2, pady = (0, 5), fill = 'x', expand = 1)
        self.boo = Button(
            self.frm2, 
            text = 'ON\OFF', 
            font = 'consolas 10 bold', 
            relief = GROOVE, 
            command = self.stopauto, 
            width = 4
        )
        self.boo.pack(side = LEFT, padx = 2, pady = (0, 5), fill = 'x', expand = 1)        
        self.bds = Button(
            self.frm2, 
            text = 'DEL REPLY', 
            font = 'consolas 10 bold', 
            relief = GROOVE, 
            command = self.delscreen, 
            width = 4
        )
        self.bds.pack(side = LEFT, padx = 2, pady = (0, 5), fill = 'x', expand = 1)
        self.frll = ttk.Frame(self.root)
        self.frll.pack(fill = 'x', padx = 2)
        self.frsp = ttk.Frame(self.root)
        self.frsp.pack(fill = 'x')        
        self.spl1 = ttk.Label(self.frsp, text = 'Days')
        self.spl1.pack(side = LEFT, pady = (0, 5), padx = (2, 0))
        self.sp1v = IntVar(self.root)
        self.sp1 = ttk.Spinbox(
            self.frsp, 
            from_ = 0, 
            to = 365, 
            textvariable = self.sp1v, 
            justify = 'center', 
            width = 4
        )
        self.sp1.config(state = 'readonly')
        self.sp1.pack(side = LEFT, pady = (0, 5), padx = (0, 5), fill = 'x', expand = 1)
        self.spl2 = ttk.Label(self.frsp, text = 'Hours')
        self.spl2.pack(side = LEFT, pady = (0, 5), padx = (0, 5))
        self.sp2v = IntVar(self.root)
        self.sp2 = ttk.Spinbox(
            self.frsp, 
            from_ = 0, 
            to = 24, 
            textvariable = self.sp2v, 
            justify = 'center', 
            width = 4
        )
        self.sp2.config(state = 'readonly')
        self.sp2.pack(side = LEFT, pady = (0, 5), padx = (0, 5), fill = 'x', expand = 1)
        self.spl3 = ttk.Label(self.frsp, text = 'Minutes')
        self.spl3.pack(side = LEFT, pady = (0, 5), padx = (0, 5))
        self.sp3v = IntVar(self.root)
        self.sp3 = ttk.Spinbox(
            self.frsp, 
            from_ = 0, 
            to = 60, 
            textvariable = self.sp3v, 
            justify = 'center', 
            width = 4
        )
        self.sp3.config(state = 'readonly')
        self.sp3.pack(side = LEFT, pady = (0, 5), padx = (0, 5), fill = 'x', expand = 1)
        self.spl4 = ttk.Label(self.frsp, text = 'Seconds')
        self.spl4.pack(side = LEFT, pady = (0, 5), padx = (0, 5))
        self.sp4v = IntVar(self.root)
        self.sp4 = ttk.Spinbox(
            self.frsp, 
            from_ = 5, 
            to = 60, 
            textvariable = self.sp4v, 
            justify = 'center', 
            width = 4
        )
        self.sp4v.set(5)
        self.sp4.config(state = 'readonly')
        self.sp4.pack(side = LEFT, pady = (0, 5), padx = (0, 3), fill = 'x', expand = 1)
        self.frms = ttk.Frame(self.root)
        self.frms.pack(fill = 'x')
        self.schb = Button(
            self.frms, 
            text = 'S C H E D U L E R  S E N D', 
            command = self.runsend, 
            font = 'consolas 12 bold', 
            relief = GROOVE
        )
        self.schb.pack(side = LEFT, padx = 2, pady = (0, 5), fill = 'x', expand = 1)
        self.schm = Button(
            self.frms, 
            text = 'S C H E D U L E R  M U L T I', 
            command = self.multisched, 
            font = 'consolas 12 bold', 
            relief = GROOVE
        )
        self.schm.pack(side = LEFT, padx = 2, pady = (0, 5), fill = 'x', expand = 1)        
        self.frm3 = ttk.Frame(self.root)
        self.frm3.pack(fill = 'both')
        self.text = Text(
            self.frm3,
            pady = 3, 
            padx = 5, 
            relief = FLAT, 
            wrap = 'word', 
            height = 12
        )
        if self.plat.startswith('win'):
            self.text.config(font = '-*-Segoe-UI-Emoji-*--*-153-*')
        else:
            self.text.config(font = 'consolas 12 bold')        
        self.text.pack(side = LEFT, padx = (2,0), pady = (0, 5), fill = 'both', expand = 1)
        self.text.bind('<KeyRelease-space>', self.autotext)
        self.scroll = Scrollbar(self.frm3)
        self.scroll.pack(side = RIGHT, fill = 'y', padx = (0,2), pady = (0, 5))
        self.scroll.config(command = self.text.yview)
        self.text.config(yscrollcommand = self.scroll.set)
        self.frbs = ttk.Frame(self.root)
        self.frbs.pack(fill = 'x')
        self.sbut = Button(
            self.frbs, 
            text = 'S E N D  N O W', 
            command = self.sentem, 
            font = 'consolas 12 bold', 
            relief = GROOVE, 
            width = 4
        )
        self.sbut.pack(side =  LEFT, padx = 2, pady = (0, 5), fill = 'x', expand = 1)
        self.busf = Button(
            self.frbs, 
            text = 'S E N D  F I L E', 
            command = self.sf, 
            font = 'consolas 12 bold', 
            relief = GROOVE, 
            width = 4
        )
        self.busf.pack(side =  LEFT, padx = (0, 2), pady = (0, 5), fill = 'x', expand = 1)
        self.busf = Button(
            self.frbs, 
            text = 'S E N D  M U L T I', 
            command = self.multisend, 
            font = 'consolas 12 bold', 
            relief = GROOVE, 
            width = 4
        )
        self.busf.pack(side =  LEFT, padx = (0, 2), pady = (0, 5), fill = 'x', expand = 1)
        self.bufm = Button(
            self.frbs, 
            text = 'F I L E  M U L T I', 
            command = self.mulfile, 
            font = 'consolas 12 bold', 
            relief = GROOVE, 
            width = 4
        )
        self.bufm.pack(side =  RIGHT, padx = (0, 2), pady = (0, 5), fill = 'x', expand = 1)          
        self.frm4 = ttk.Frame(self.root)
        self.frm4.pack(fill = 'both', expand = 1)
        self.text2 = Text(
            self.frm4, 
            pady = 3, 
            padx = 5, 
            relief = FLAT, 
            wrap = 'word', 
            height = 12
        )
        if self.plat.startswith('win'):
            self.text2.config(font = '-*-Segoe-UI-Emoji-*--*-153-*')
        else:
            self.text2.config(font = 'consolas 12 bold')
        self.text2.pack(side = LEFT, padx = (2,0), pady = (0, 5), fill = 'both', expand = 1)
        self.scroll2 = Scrollbar(self.frm4)
        self.scroll2.pack(side = RIGHT, fill = 'y', padx = (0,2), pady = (0, 5))
        self.scroll2.config(command = self.text2.yview)
        self.text2.config(yscrollcommand = self.scroll2.set)
        self.text2.config(state = 'disable')
        self.frgr = ttk.Frame(self.root)
        self.frgr.pack(fill = 'both')
        self.bugr = Button(
            self.frgr, 
            text = 'G E T  R E P L Y', 
            command = self.getrep, 
            font = 'consolas 12 bold', 
            relief = GROOVE, 
            width = 4
        )
        self.bugr.pack(side = LEFT, padx = 2, pady = (0, 5), fill = 'both', expand = 1)
        self.bugf = Button(
            self.frgr, 
            text = 'G E T  F I L E', 
            command = self.gf, 
            font = 'consolas 12 bold', 
            relief = GROOVE, 
            width = 4
        )
        self.bugf.pack(side = LEFT, padx = (0, 2), pady = (0, 5), fill = 'both', expand = 1)
        self.buof = Button(
            self.frgr, 
            text = 'F O L D E R S', 
            command = self.opfold, 
            font = 'consolas 12 bold', 
            relief = GROOVE, 
            width = 4
        )
        self.buof.pack(side = LEFT, padx = (0, 2), pady = (0, 5), fill = 'both', expand = 1)        
        self.bulg = Button(
            self.frgr, 
            text = 'L O G  O U T', 
            command = self.lg, 
            font = 'consolas 12 bold', 
            relief = GROOVE, 
            width = 4
        )
        self.bulg.pack(side = RIGHT, padx = (0, 2), pady = (0, 5), fill = 'both', expand = 1)        
        self.entto.focus()
        self.auto = {}
        if os.path.exists(os.path.join(self.orip.parent, 'auto.tvg')):
            with open(os.path.join(self.orip.parent, 'auto.tvg')) as aur:
                try:
                    rd = ast.literal_eval(aur.read())
                    self.auto = rd
                except:
                    os.remove(os.path.join(self.orip.parent, 'auto.tvg'))
                    messagebox.showwarning(
                        'TeleTVG', 
                        'The file has been corrupted and removed!!!', 
                        parent = self.root
                    )
                
    def stopauto(self, event = None):
        # Disable autotext
        
        if self.STOP_A:
            self.STOP_A = False
            if self.plat.startswith('win'):
                self.messages('<<Auto-Text>>\n\nis enabled!', 700)
            else:
                messagebox.showinfo('TeleTVG', 'Auto-Text is enabled!')
        else:
            self.STOP_A = True
            if self.plat.startswith('win'):
                self.messages('<<Auto-Text>>\n\nis disabled!', 700)
            else:
                messagebox.showinfo('TeleTVG', 'Auto-Text is disabled!')
                
    def messages(self, m: str, t_out: int):
        # Message for informing.
        
        def exit(event = None):
            root.destroy()        
        root = Toplevel(self.root)
        root.after(t_out, exit)
        root.attributes('-topmost', 1)
        wd = int(root.winfo_screenwidth()/2 - 250/2)
        hg = int(root.winfo_screenheight()/3 - 250/3)
        root.geometry(f'300x300+{wd}+{hg}')
        root.overrideredirect(1)
        a = Message(master= root)
        a.pack()
        a.tk_strictMotif(1)
        frm = Frame(a, borderwidth = 7, bg = 'dark blue', width = 250, height = 250)
        frm.pack(fill = 'both', expand = 1)
        tx = m
        lab = Label(
            frm, 
            text = tx, 
            justify = 'center', 
            anchor = 'center', 
            font = 'verdana 15 bold', 
            width = 250, 
            height = 250, 
            bg = 'gold', 
            fg = 'black'
        )
        lab.pack(fill = 'both', expand = 1)
    
    def rectext(self, event = None):
        # Autotext saving with format: 
        # <text>::<text>\n
        # text [space] expanded
        
        if self.text.get('0.1', END)[:-1]:
            ask = messagebox.askyesno(
                'TeleTVG', 
                '"Yes" save autotext or "No" to delete', 
                parent = self.root
            )
            if ask:
                ck = [i for i in self.text.get('0.1', END).split('\n') if i]
                collect = [
                    tuple(
                        [
                            k.partition('::')[0].strip(), 
                            k.partition('::')[2].strip().replace('~', '\n')
                        ]
                    ) 
                    for k in ck if '::' in k
                ]
                if len(ck) == len(collect):
                    del ck
                    self.auto = {}
                    if not os.path.exists(os.path.join(self.orip.parent, 'auto.tvg')):
                        with open(os.path.join(self.orip.parent, 'auto.tvg'), 'w') as aur:
                            aur.write(str(dict(collect)))
                        self.auto = dict(collect)
                    else:
                        try:
                            with open(os.path.join(self.orip.parent, 'auto.tvg')) as aur:
                                rd = ast.literal_eval(aur.read())
                        except:
                            with open(os.path.join(self.orip.parent, 'auto.tvg'), 'w') as aur:
                                aur.write(str(dict(collect)))
                            self.auto = dict(collect)                            
                            messagebox.showwarning(
                                'TeleTVG', 
                                'The file has been corrupted and recreated new!!!', 
                                parent = self.root
                            )
                        else:
                            with open(os.path.join(self.orip.parent, 'auto.tvg'), 'w') as aur:
                                aur.write(str(rd | dict(collect)))
                            self.auto = rd | dict(collect)
                        finally:
                            del collect
                            self.text.delete('1.0', END)
                else:
                    del ck
                    del collect
                    messagebox.showinfo(
                        'TeleTVG', 
                        'No autotext recorded (please check the format)!', 
                        parent = self.root
                    )
            else:
                if os.path.exists(os.path.join(self.orip.parent, 'auto.tvg')):
                    try:
                        with open(os.path.join(self.orip.parent, 'auto.tvg')) as aur:
                            rd = ast.literal_eval(aur.read())
                    except:
                        messagebox.showerror(
                            'TeleTVG', 
                            'File has been corrupted!!!', 
                            parent = self.root
                        )
                    else:
                        def sure(event):
                            try:
                                if event.char in string.ascii_letters:
                                    if event.widget.get():
                                        idx = event.widget.index(INSERT)
                                        gt = event.widget.get()
                                        event.widget.delete(0, END)
                                        event.widget.insert(0, gt[:idx])
                                        if event.widget.get():
                                            for name in rd:
                                                if (
                                                    event.widget.get().title() in name.title() 
                                                    and name.title().startswith(
                                                        event.widget.get().title()[0]
                                                        )
                                                    ):
                                                    event.widget.delete(0, END)
                                                    event.widget.insert(END, f'{name}: {rd[name]}')
                                                    MyDialog.am.see(list(rd).index(name))
                                        event.widget.icursor(index = idx)
                            except Exception as e:
                                messagebox.showwarning('TeleTVG', f'{e}', parent = self.root)

                        class MyDialog(simpledialog.Dialog):
                            am = None
                            def body(self, master):
                                self.title('Select Autotext')
                                fr1 = Frame(master)
                                fr1.pack()
                                Label(fr1, text="Text: ").pack(side = LEFT)
                                self.e1 = Listbox(fr1, selectmode = MULTIPLE)
                                for i in rd:
                                    self.e1.insert(END,f'{i}: {rd[i]}')
                                self.e1.pack(side = LEFT)
                                MyDialog.am = self.e1
                                self.sce1 = ttk.Scrollbar(fr1, orient = 'vertical')
                                self.sce1.pack(side = RIGHT, fill = 'y')
                                self.sce1.config(command = self.e1.yview)
                                self.e1.config(yscrollcommand = self.sce1.set)
                                fr2 = Frame(master)
                                fr2.pack(anchor = W)
                                Label(fr2, text = 'Search:').pack(side = LEFT)
                                self.e3 = Entry(fr2)
                                self.e3.pack(side = RIGHT)
                                self.e3.bind('<KeyRelease>', sure)
                    
                            def apply(self):
                                self.result = [list(rd)[int(i)] for i in self.e1.curselection()]
                    
                        d = MyDialog(self.root)
                        if d.result:
                            for i in d.result:
                                del rd[i]
                            if rd:
                                with open(os.path.join(self.orip.parent, 'auto.tvg'), 'w') as aur:
                                    aur.write(str(rd))
                            else:
                                os.remove(os.path.join(self.orip.parent, 'auto.tvg'))
                        else:
                            messagebox.showinfo(
                                'TeleTVG', 
                                'Deleteion of autotext aborted!', 
                                parent = self.root
                            )
        else:
            messagebox.showinfo('TeleTVG', 'No autotext to record!', parent = self.root)
            
    def autotext(self, event = None):
        # Autotext algorithm:
        # text [space] expanded
        
        if self.STOP_A is False:
            if 'text' in str(self.root.focus_get()):
                if self.text.get('0.1', END)[:-1]:
                    if self.auto:
                        vpox = self.text.get(f'{INSERT} linestart', f'{INSERT}-1c').split(' ')[-1]
                        if list(self.auto).count(
                            vpox := vpox.lower() 
                            if list(self.auto).count(vpox.lower()) 
                            else 
                            vpox
                            ):
                            if len(
                                self.text.get(f'{INSERT} linestart', f'{INSERT}-1c').split(' ')
                                ) == 1 or self.text.get(
                                    f'{INSERT} linestart', f'{INSERT}-1c'
                                    ).split(' ')[-2][-1] == '.':
                                self.text.delete(f'{INSERT}-{len(vpox)+1}c', f'{INSERT}')
                                if self.auto[vpox][0] in string.ascii_lowercase:
                                    self.text.insert(
                                        f'{INSERT}', 
                                        self.auto[vpox][0].upper()+self.auto[vpox][1:]+' '
                                    )
                                else:
                                    self.text.insert(f'{INSERT}', self.auto[vpox]+' ')
                            else:
                                self.text.delete(f'{INSERT}-{len(vpox)+1}c', f'{INSERT}')
                                self.text.insert(f'{INSERT}', self.auto[vpox]+' ')
                        del vpox
                            
    def tynam(self, event = None):
        # To predict the key-in typing in "To" combobox.
        
        try:
            if event.char in string.ascii_letters:
                if self.entto.get():
                    idx = self.entto.index(INSERT)
                    gt = self.entto.get()
                    self.entto.delete(0, END)
                    self.entto.insert(0, gt[:idx])
                    if self.entto.get():
                        r = 2
                        while r:
                            for name in self.users:
                                if (self.entto.get().lower() in name.lower() 
                                    and self.entto.get().lower() == name.lower()[
                                        :len(self.entto.get().lower())
                                        ]
                                    ):
                                    self.entto.current(sorted(list(self.users)).index(name))
                            r -= 1
                    self.entto.icursor(index = idx)
        except Exception as e:
            messagebox.showwarning('TeleTVG', f'{e}', parent = self.root)
        
    def emj(self):
        # Emoji window.
        
        if self.plat.startswith('win'):
            emo.main(self)
        else:
            messagebox.showinfo('TeleTVG', 'In MacOS Emoji not working in tkinter!')
        
    def winexit(self):
        # Will close ReminderTel and Emoji window as well.
        
        if str(self.root.state()) != 'withdrawn':
            if str(self.root.winfo_geometry()) == self.RESZ:
                with open(os.path.join(self.orip.parent, 'telgeo.tvg'), 'wb') as geo:
                    geo.write(str({'geo': self.RESZ}).encode())
            else:
                ask = messagebox.askyesno(
                    'TeleTVG', 
                    "Do you want to set your new window's position?",
                    parent = self.root
                )
                if ask:
                    with open(os.path.join(self.orip.parent, 'telgeo.tvg'), 'wb') as geo:
                        geo.write(str({'geo': str(self.root.winfo_geometry())}).encode())
                else:
                    with open(os.path.join(self.orip.parent, 'telgeo.tvg'), 'wb') as geo:
                        geo.write(str({'geo': self.RESZ}).encode())
        if self.afterid:
            self.root.after_cancel(self.afterid)
        if emo.Emo.status is False:
            emo.Emo.mainon.destroy()
        self.root.destroy()
            
    def paste(self, event = None):
        # Paste any copied text.

        try:
            p = self.root.clipboard_get()
            if p:
                ask = messagebox.askyesno(
                    'TeleTVG', 
                    'Do you want to paste text?', 
                    parent = self.root
                )
                if ask:
                    self.text.delete('1.0', END)
                    self.text.insert(END, p)
                    self.root.clipboard_clear()
        except:
            pass
    
    def copc(self, event = None):
        # Copied text and delete them on screen.

        if self.text.get('1.0', END)[:-1]:
            if self.text.tag_ranges('sel'):
                self.root.clipboard_clear()
                self.root.clipboard_append(self.text.selection_get())
                self.text.tag_remove('sel', 'sel.first', 'sel.last')
                self.text.mark_set('insert', INSERT)
                messagebox.showinfo(
                    'TeleTVG', 
                    'Selected text has been copied!', 
                    parent = self.root
                )
            else:
                self.root.clipboard_clear()
                self.root.clipboard_append(self.text.get('1.0', END)[:-1])
                messagebox.showinfo(
                    'TeleTVG', 
                    'The text has been copied!', 
                    parent = self.root
                )
    
    def clear(self, event = None):
        # Clear screen.
        
        if self.text.get('1.0', END)[:-1]:
            ask = messagebox.askyesno(
                'TeleTVG', 
                'Do you want to clear the text?', 
                parent = self.root
            )
            if ask:
                self.text.delete('1.0', END)
                
    async def runs(self, sch: dict, mul: list = None):
        # Run Scheduler to send Telegram
        
        gms = int(len(self.text.get('1.0', END)[:-1])/4096)
        async with TelegramClient('ReminderTel', self.api_id, self.api_hash) as client:
            try:
                await client.connect()
                if gms == 0:
                    if mul:
                        await asyncio.gather(
                            *[
                                client.send_message(
                                self.users[user], 
                                self.text.get('1.0', END)[:-1], 
                                schedule = timedelta(
                                    days = sch['days'], 
                                    hours = sch['hours'],
                                    minutes = sch['minutes'],
                                    seconds = sch['seconds']
                                    )
                                ) for user in mul
                            ]
                        )
                    else:
                        await client.send_message(
                            self.users[
                                self.entto.get()
                                ], 
                            self.text.get('1.0', END)[:-1], 
                            schedule = timedelta(
                                days = sch['days'], 
                                hours = sch['hours'],
                                minutes = sch['minutes'],
                                seconds = sch['seconds']
                            )
                        )
                else:
                    orm = self.text.get('1.0', END)[:-1].split('\n')
                    while orm:
                        getm = ''
                        num = 0
                        for i in range(len(orm)):
                            if len(getm) + (len(orm[i])+1) < 4090:
                                getm += ''.join(orm[i]+'\n')
                            else:
                                num = i
                                break
                        if mul:
                            await asyncio.gather(
                                *[
                                    client.send_message(
                                    self.users[user], 
                                    getm, 
                                    schedule = timedelta(
                                        days = sch['days'], 
                                        hours = sch['hours'],
                                        minutes = sch['minutes'],
                                        seconds = sch['seconds']
                                        )
                                    ) for user in mul
                                ]
                            )
                        else:
                            await client.send_message(
                                self.users[
                                    self.entto.get()
                                    ], 
                                getm,
                                schedule = timedelta(
                                    days = sch['days'], 
                                    hours = sch['hours'],
                                    minutes = sch['minutes'],
                                    seconds = sch['seconds']
                                )
                            )
                        if num:
                            orm = orm[i:]
                            continue
                        else:
                            break
                await client.disconnect()
                ct = timedelta(
                    days = sch['days'], 
                    hours = sch['hours'], 
                    minutes = sch['minutes'], 
                    seconds = sch['seconds']
                )
                ct = str(dt.today().replace(microsecond = 0) + ct)
                tms = f'Message schedule sent at {ct}'
                messagebox.showinfo('TeleTVG', tms, parent = self.root)
            except:
                await client.disconnect()
                messagebox.showinfo(
                    'TeleTVG', 
                    f'\n{sys.exc_info()}\n\n{msg}', 
                    parent = self.root
                ) 
            
    def runsend(self):
        # Asyncio method of calling for running schedulers.
        
        if self.entto.get():
            if self.text.get('1.0', END)[:-1]:
                stm = dict(
                    days = self.sp1v.get(), 
                    hours = self.sp2v.get(), 
                    minutes = self.sp3v.get(), 
                    seconds = self.sp4v.get(),
                )        
                asyncio.get_event_loop().run_until_complete(self.runs(stm))
            else:
                messagebox.showinfo(
                    'TeleTVG', 
                    'Please write message!', 
                    parent = self.root
                )
        else:
            messagebox.showinfo(
                'TeleTVG', 
                'Please fill "To"!', 
                parent = self.root
            )            
                
    async def sent(self):
        # Sending Telegram to anyone.
        
        try:
            gms = int(len(self.text.get('1.0', END)[:-1])/4096)
            async with TelegramClient('ReminderTel', self.api_id, self.api_hash) as client:
                await client.connect()
                if gms == 0:
                    await client.send_message(
                        self.users[self.entto.get()], 
                        self.text.get('1.0', END)[:-1]
                    )
                else:
                    orm = self.text.get('1.0', END)[:-1].split('\n')
                    while orm:
                        getm = ''
                        num = 0
                        for i in range(len(orm)):
                            if len(getm) + (len(orm[i])+1) < 4090:
                                getm += ''.join(orm[i]+'\n')
                            else:
                                num = i
                                break
                        await client.send_message(self.users[self.entto.get()], getm)
                        if num:
                            orm = orm[i:]
                            continue
                        else:
                            break
                await client.disconnect()
            self.text.delete('1.0', END)
        except:
            messagebox.showinfo(
                'TeleTVG', 
                f'\n{sys.exc_info()}', 
                parent = self.root
            )
            await client.disconnect()
            
    def sentem(self):
        # Asyncio method of calling for sending message at once.
        
        if self.entto.get():
            if self.text.get('1.0', END)[:-1]:
                asyncio.get_event_loop().run_until_complete(self.sent())
                if self.afterid:
                    self.root.after_cancel(self.afterid)
                asyncio.get_event_loop().run_until_complete(self.rep())
            else:
                messagebox.showinfo('TeleTVG', 'Please write message!', parent = self.root)
        else:
            messagebox.showinfo('TeleTVG', 'Please fill "To" first!', parent = self.root)            
            
    async def sentfile(self, filename: str):
        # Sending file to user.
        
        try:
            async with TelegramClient('ReminderTel', self.api_id, self.api_hash) as client:
                await client.connect()
                await client.send_file(
                    self.users[self.entto.get()], 
                    filename, 
                    caption = 'TreeViewGui'
                )
                await client.disconnect()
            tms = f'Message finished sent at \
            {dt.isoformat(dt.now().replace(microsecond = 0)).replace("T", " ")}'
            messagebox.showinfo('TeleTVG', tms, parent = self.root)
        except:
            messagebox.showinfo('TeleTVG', f'\n{sys.exc_info()}', parent = self.root)
            await client.disconnect()
    
    def sf(self):
        # Sending file using asyncio call
        
        if self.entto.get():
            fpt = os.path.join(self.orip.parent, 'TVGPro')
            ask = filedialog.askopenfilename(
                initialdir = fpt, 
                filetypes = [("All files","*.*")], 
                parent = self.root
            )
            if ask:
                asyncio.get_event_loop().run_until_complete(self.sentfile(ask))
            else:
                messagebox.showinfo('TeleTVG', 'Send file is aborted!', parent = self.root)
        else:
            messagebox.showinfo('TeleTVG', 'Please fill "To" first!', parent = self.root)
            
    async def rep(self):
        # Getting reply from a user [get the last 15 messages]
        try:
            async with TelegramClient('ReminderTel', self.api_id, self.api_hash) as client:
                await client.connect()
                self.text2.config(state = 'normal')
                self.text2.delete('1.0', END)
                async for message in client.iter_messages(self.users[self.entto.get()], 15):
                    mtx = message.message if message.message else "(>^_^<)>Sticker/File<(>^_^<)"
                    msg = message.text
                    if not self.plat.startswith('win'):
                        mtx = ''.join(filter(lambda x: x in string.printable, mtx))
                        msg = ''.join(filter(lambda x: x in string.printable, msg))
                    if message.out:
                        td = dt.ctime(dt.astimezone(message.date))
                        if msg:
                            self.text2.insert('1.0', f'{msg}\n\n')
                        else:
                            self.text2.insert('1.0', f'{mtx}\n\n')
                        self.text2.insert('1.0', f'{td}\n')
                    else:
                        td = dt.ctime(dt.astimezone(message.date))
                        if msg:
                            self.text2.insert('1.0', f'{msg}\n\n')
                        else:
                            self.text2.insert('1.0', f'{mtx}\n\n')
                        self.text2.insert('1.0', f'{td} [{self.entto.get()}]\n')
                    del mtx, msg
                self.text2.config(state = 'disable')
                self.text2.yview_moveto(1)
                await client.disconnect()
            if self.plat.startswith('win'):
                self.afterid = self.root.after(60000, self.getrep)
        except Exception as e:
            await client.disconnect()
            messagebox.showerror('TeleTVG', f'{e}')
                
    def getrep(self):
        # Asyncio method of calling for getting reply.
        
        if self.entto.get():
            if self.afterid:
                self.root.after_cancel(self.afterid)
            try:
                if not asyncio.get_event_loop().is_running():
                    asyncio.get_event_loop().run_until_complete(self.rep())
                    if self.plat.startswith('win'):
                        self.messages('<<<TeleTVG>>>\n\nGet Reply\n\nhas been updated!', 1200)
                else:
                    if self.plat.startswith('win'):
                        self.afterid = self.root.after(60000, self.getrep)
            except Exception as e:
                messagebox.showwarning('TeleTVG', f'{e}')
        else:
            messagebox.showinfo('TeleTVG', 'Please fill "To" first!', parent = self.root)
            
    def delscreen(self, event =  None):
        if self.afterid:
            self.root.after_cancel(self.afterid)
        self.text2.config(state = 'normal')
        self.text2.delete('1.0', END)
        self.text2.config(state = 'disabled')
            
    async def getfile(self, amt: int = None):
        # Getting file from a user [get all TVG protected text file]
                   
        path = os.path.join(self.orip.parent,'TeleTVGPro')
        pathf = os.path.join(
            path, 
            re.sub(
                r'\W+', '_', dt.isoformat(dt.now()).replace('T', '_')
            )
        )
        os.mkdir(pathf)
        async with TelegramClient('ReminderTel', self.api_id, self.api_hash) as client:
            try:
                await client.connect()
                num = 0
                async for message in client.iter_messages(self.users[self.entto.get()], None):
                    if message.media:
                        if isinstance(message.media, types.MessageMediaDocument):
                            if message.media.document.mime_type not in [
                                'application/x-tgsticker', 
                                'image/webp'
                                ]:
                                if amt is not None:
                                    if amt > 0: amt -= 1 
                                    else: break
                                num += 1
                                await client.download_media(message, pathf)
                        elif isinstance(
                            message.media, (
                            types.MessageMediaPhoto, 
                            types.MessageMediaContact
                                )
                            ):
                            if amt is not None:
                                if amt > 0: amt -= 1 
                                else: break
                            num += 1
                            await client.download_media(message, pathf)
                await client.disconnect()
            except Exception as e:
                await client.disconnect()
                messagebox.showerror('TeleTVG', f'{e}', parent = self.root)
            finally:
                if num:
                    ask = messagebox.askyesno(
                        'TeleTVG', 
                        f'You have download {num} files, want to open file folder?', 
                        parent = self.root
                    )
                    if ask:
                        if self.plat.startswith('win'):
                            os.startfile(pathf)
                        else:
                            os.system(f'open "{pathf}"')
                else:
                    os.rmdir(pathf)
                    messagebox.showinfo('TeleTVG', 'Nothing downloaded!', parent = self.root)
                del path, pathf, num
        
    def gf(self):
        # Starting running asyncio get file.
        
        if self.entto.get():
            ask = simpledialog.askinteger(
                'TeleTVG', 
                'Download the last how many? \
                [files/photos]\nIf 0 mean all files will be downloaded!', 
                parent = self.root
            )
            if ask:
                asyncio.get_event_loop().run_until_complete(self.getfile(ask))
            else:
                asyncio.get_event_loop().run_until_complete(self.getfile())
        else:
            messagebox.showinfo('TeleTVG', 'Please fill "To" first!', parent = self.root)        
            
    async def filcomb(self):
        # Intitiate filling contacts and languages.
        
        async with TelegramClient('ReminderTel', self.api_id, self.api_hash) as client:
            await client.connect()
            result = await client(functions.contacts.GetContactsRequest(hash=0))
            mypro = await client.get_me()
            await client.disconnect()
            if mypro.last_name:
                self.root.title(f'TeleTVG-{mypro.first_name} {mypro.last_name}')
            else:
                self.root.title(f'TeleTVG-{mypro.first_name}')
            self.users = {}
            self.langs = None
            for user in result.users:
                if user.username:
                    if user.last_name:
                        self.users[f'{user.first_name} {user.last_name}'] = f'@{user.username}'
                    else:
                        self.users[f'{user.first_name}'] = f'@{user.username}'
                else:
                    if user.last_name:
                        self.users[f'{user.first_name} {user.last_name}'] = f'+{user.phone}'
                    else:
                        self.users[f'{user.first_name}'] = f'+{user.phone}'
            self.entto.delete(0, END)
            self.entto['values'] = sorted(list(self.users))
            
    async def acc(self):
        # Checking account's folder.
        
        async with TelegramClient('ReminderTel', self.api_id, self.api_hash) as client:
            await client.connect()
            mypro = await client.get_me()
            await client.disconnect()
            ori = os.path.join(os.getcwd(), 'Telacc')
            self.chacc = f'{mypro.id}'
            if self.chacc not in os.listdir(ori):
                os.mkdir(os.path.join(ori, self.chacc))
                    
    def multiselect(self, event = None):
        # Select multiple recepients and save them under a group.
        
        if self.lock is False:
            self.lock = True
            users = sorted(list(self.users))
            def sure(event):
                try:
                    if event.char in string.ascii_letters:
                        if event.widget.get():
                            idx = event.widget.index(INSERT)
                            gt = event.widget.get()
                            event.widget.delete(0, END)
                            event.widget.insert(0, gt[:idx])
                            if event.widget.get():
                                r = 2
                                while r:
                                    for name in self.users:
                                        if (
                                            event.widget.get().lower() in name.lower() 
                                            and event.widget.get().lower() == name.lower()
                                            [:len(event.widget.get().lower())]
                                           ):
                                            event.widget.delete(0, END)
                                            event.widget.insert(END, name)
                                            self.refidx = sorted(list(self.users)).index(name)
                                            MyDialog.am.see(self.refidx)
                                    r -= 1
                            event.widget.icursor(index = idx)
                except Exception as e:
                    messagebox.showwarning('TeleTVG', f'{e}', parent = self.root)
            
            def updatesel(event = None):
                if self.upt:
                    if set(MyDialog.am.curselection()) - set(self.upt):
                        x = list(set(MyDialog.am.curselection()) - set(self.upt)).pop()
                        self.sel.append(x)
                        self.upt = MyDialog.am.curselection()
                    elif set(self.upt) - set(MyDialog.am.curselection()):
                        x = list(set(self.upt)-set(MyDialog.am.curselection())).pop()
                        del self.sel[self.sel.index(x)]
                        self.upt = MyDialog.am.curselection()
                else:
                    self.upt = MyDialog.am.curselection()
                    self.sel.append(self.upt[0]) 
            
            def selectmode():
                if self.refidx is not None and self.refidx >= 0:
                    if self.refidx in MyDialog.am.curselection():
                        MyDialog.am.select_clear(self.refidx)
                        MyDialog.ent.focus()
                        updatesel()
                    else:
                        MyDialog.am.select_set(self.refidx)
                        MyDialog.ent.focus()
                        updatesel()
                        self.refidx = None
                else:
                    if MyDialog.am.curselection():
                        MyDialog.am.see(self.sel[-1])
                        MyDialog.am.select_clear(self.sel[-1])
                        updatesel()
                        
            groups = [
                i.partition('_')[0]  for i in os.listdir(
                    os.path.join(
                        'Telacc', self.chacc
                        )
                    ) if '_group' in i 
            ]        
            class MyDialog(simpledialog.Dialog):
                am = None
                ent = None
                def body(self, master):
                    self.title('Select users')
                    fr1 = Frame(master)
                    fr1.pack()
                    Label(fr1, text="Users: ").pack(side = LEFT)
                    self.e1 = Listbox(fr1, exportselection = False, selectmode = MULTIPLE)
                    for i in users:
                        self.e1.insert(END, i)
                    self.e1.pack(side = LEFT)
                    self.e1.bind('<ButtonRelease>', updatesel)
                    MyDialog.am = self.e1
                    self.sce1 = ttk.Scrollbar(fr1, orient = 'vertical')
                    self.sce1.pack(side = RIGHT, fill = 'y')
                    self.sce1.config(command = self.e1.yview)
                    self.e1.config(yscrollcommand = self.sce1.set)
                    fr2 = Frame(master)
                    fr2.pack(anchor = W)
                    Label(fr2, text = 'Search:').grid(row = 0, column = 0, sticky = W)
                    self.e3 = Entry(fr2)
                    self.e3.grid(row = 0, column = 1, sticky = W, pady = (2, 0))
                    MyDialog.ent = self.e3
                    self.e3.bind('<KeyRelease>', sure)
                    self.e4 = Button(
                        fr2, 
                        text = 'Un/Select', 
                        command = selectmode, 
                        width = 16, 
                        relief = GROOVE
                    )
                    self.e4.grid(row = 2, column = 1, sticky = W, pady = 2)
                    Label(fr2, text = 'Folder:').grid(row = 4, column = 0, sticky = W)
                    self.e2 = ttk.Combobox(fr2)
                    self.e2.grid(row = 4, column = 1)
                    if groups:
                        self.e2['values'] = groups
                        self.e2.current(0)
                    return self.e3
            
                def apply(self):
                    MyDialog.am = None
                    MyDialog.ent = None
                    self.result = [users[int(i)] for i in self.e1.curselection()]
                    self.folder = self.e2.get()
                                
            d = MyDialog(self.root)
            self.lock = False
            if d.result is not None:
                dest = os.path.join('Telacc', self.chacc)
                mfold = os.path.join(dest, f'{d.folder}_group')            
                if d.result and d.folder:
                    if f'{d.folder}_group' not in os.listdir(dest):
                        os.mkdir(mfold)
                        with open(os.path.join(mfold,f'{d.folder}.json'), 'w') as fs:
                            mkc = {d.folder: d.result}
                            json.dump(mkc, fs)
                    else:
                        with open(os.path.join(mfold,f'{d.folder}.json')) as fs:
                            rd = dict(json.load(fs))
                            ou = rd[d.folder]
                            for u in d.result:
                                if u not in ou:
                                    ou.append(u)
                            rd[d.folder] = ou
                        with open(os.path.join(mfold,f'{d.folder}.json'), 'w') as wj:
                            json.dump(rd, wj)   
                elif d.folder:
                    if f'{d.folder}_group' in os.listdir(dest):
                        ask = messagebox.askyesno(
                            'TeleTVG', 
                            'Do you want to delete this group?', 
                            parent = self.root
                        )
                        if ask:
                            shutil.rmtree(mfold)
                        else:
                            messagebox.showinfo(
                                'TeleTVG', 
                                'Deletion aborted!', 
                                parent = self.root
                            )
                    else:
                        messagebox.showinfo(
                            'TeleTVG', 
                            'Not created yet!', 
                            parent = self.root
                        )
                else:
                    messagebox.showinfo(
                        'TeleTVG', 
                        'Please create folder first!', 
                        parent = self.root
                    )
            self.refidx = None
            self.upt = tuple()
            self.sel = []
                    
    def editmu(self):
        # To get Users in group for edit. [deleting users in group]
        
        if self.lock is False:        
            groups = [
                i  for i in os.listdir(
                    os.path.join(
                        'Telacc', 
                        self.chacc
                        )
                    ) if '_group' in i 
            ]
            if groups:
                self.lock = True
                class MyDialog(simpledialog.Dialog):
                
                    def body(self, master):
                        self.title('Choose Group')
                        Label(master, text="Group: ").grid(row=0, column = 0, sticky = E)
                        self.e1 = ttk.Combobox(master, state = 'readonly')
                        self.e1['values'] = groups
                        self.e1.current(0)
                        self.e1.grid(row=0, column=1)
                        return self.e1
                
                    def apply(self):
                        self.result = self.e1.get()
                                    
                d = MyDialog(self.root)
                if d.result:
                    path = os.path.join('Telacc', self.chacc, d.result,
                                        f'{d.result.partition("_")[0]}.json')
                    with open(path) as rd:
                        edt = dict(json.load(rd))
                        users = sorted(edt[d.result.partition("_")[0]])
                    def sure(event):
                        try:
                            if event.char in string.ascii_letters:
                                if event.widget.get():
                                    idx = event.widget.index(INSERT)
                                    gt = event.widget.get()
                                    event.widget.delete(0, END)
                                    event.widget.insert(0, gt[:idx])
                                    if event.widget.get():
                                        r = 2
                                        while r:
                                            for name in users:
                                                if (
                                                    event.widget.get().lower() in name.lower() 
                                                    and event.widget.get().lower() == name.lower()
                                                    [:len(event.widget.get().lower())]
                                                   ):
                                                    event.widget.delete(0, END)
                                                    event.widget.insert(END, name)
                                                    self.refidx = users.index(name)
                                                    UserDialog.am.see(self.refidx)
                                            r -= 1
                                    event.widget.icursor(index = idx)
                        except Exception as e:
                            messagebox.showwarning('TeleTVG', f'{e}', parent = self.root)
                
                    def updatesel(event = None):
                        if self.upt:
                            if set(UserDialog.am.curselection()) - set(self.upt):
                                x = list(set(UserDialog.am.curselection()) - set(self.upt)).pop()
                                self.sel.append(x)
                                self.upt = UserDialog.am.curselection()
                            elif set(self.upt) - set(UserDialog.am.curselection()):
                                x = list(set(self.upt)-set(UserDialog.am.curselection())).pop()
                                del self.sel[self.sel.index(x)]
                                self.upt = UserDialog.am.curselection()
                        else:
                            self.upt = UserDialog.am.curselection()
                            self.sel.append(self.upt[0]) 
                
                    def selectmode():
                        if self.refidx is not None and self.refidx >= 0:
                            if self.refidx in UserDialog.am.curselection():
                                UserDialog.am.select_clear(self.refidx)
                                UserDialog.ent.focus()
                                updatesel()
                            else:
                                UserDialog.am.select_set(self.refidx)
                                UserDialog.ent.focus()
                                updatesel()
                                self.refidx = None
                        else:
                            if UserDialog.am.curselection():
                                UserDialog.am.see(self.sel[-1])
                                UserDialog.am.select_clear(self.sel[-1])
                                updatesel()                    
                        
                    class UserDialog(simpledialog.Dialog):
                        am = None
                        ent = None
                        def body(self, master):
                            self.title('Delete users')
                            fr1 = Frame(master)
                            fr1.pack()
                            Label(fr1, text="Users: ").pack(side = LEFT)
                            self.e1 = Listbox(fr1, exportselection = False, selectmode = MULTIPLE)
                            for i in users:
                                self.e1.insert(END, i)
                            self.e1.pack(side = LEFT)
                            self.e1.bind('<ButtonRelease>', updatesel)
                            UserDialog.am = self.e1
                            self.sce1 = ttk.Scrollbar(fr1, orient = 'vertical')
                            self.sce1.pack(side = RIGHT, fill = 'y')
                            self.sce1.config(command = self.e1.yview)
                            self.e1.config(yscrollcommand = self.sce1.set)
                            fr2 = Frame(master)
                            fr2.pack(anchor = W)
                            Label(fr2, text = 'Search:').grid(row = 0, column = 0, sticky = W)
                            self.e3 = Entry(fr2)
                            self.e3.grid(row = 0, column = 1, sticky = W, pady = 2)
                            UserDialog.ent = self.e3
                            self.e3.bind('<KeyRelease>', sure)
                            self.e4 = Button(
                                fr2, 
                                text = 'Un/Select', 
                                command = selectmode, 
                                width = 16, 
                                relief = GROOVE
                            )
                            self.e4.grid(row = 2, column = 1, sticky = W)
                            return self.e3
                            
                        def apply(self):
                            UserDialog.am = None
                            UserDialog.ent = None
                            self.result = [users[int(i)] for i in self.e1.curselection()]
                                        
                    u = UserDialog(self.root)
                    self.lock = False
                    if u.result:
                        dus = [i for i in users if i not in u.result]
                        if dus:
                            edt[d.result.partition("_")[0]] = dus
                            with open(path, 'w') as wu:
                                json.dump(edt, wu)
                        else:
                            shutil.rmtree(os.path.join('Telacc', self.chacc, d.result))
                    self.refidx = None
                    self.upt = tuple()
                    self.sel = []
                else:
                    self.lock = False
                    
    async def mulsend(self, sen, file = None):
        # Asyncio module of sending multiple.
        
        try:
            if file:
                async with TelegramClient('ReminderTel', self.api_id, self.api_hash) as client:
                    await client.connect()
                    await asyncio.gather(
                        *[
                            client.send_file(
                                self.users[user], 
                                file, 
                                caption = 'TreeViewGui'
                            ) for user in sen
                        ]
                    )
                    await client.disconnect()
            else:
                gms = int(len(self.text.get('1.0', END)[:-1])/4090)
                async with TelegramClient('ReminderTel', self.api_id, self.api_hash) as client:
                    await client.connect()
                    if gms == 0:
                        await asyncio.gather(
                            *[
                                client.send_message(
                                    self.users[user], 
                                    self.text.get('1.0', END)[:-1]
                                    ) for user in sen
                            ]
                        )
                    else:
                        orm = self.text.get('1.0', END)[:-1].split('\n')
                        while orm:
                            getm = ''
                            num = 0
                            for i in range(len(orm)):
                                if len(getm) + (len(orm[i])+1) < 4090:
                                    getm += ''.join(orm[i]+'\n')
                                else:
                                    num = i
                                    break
                            await asyncio.gather(
                                *[
                                    client.send_message(
                                        self.users[user], 
                                        getm
                                        ) for user in sen
                                ]
                            )
                            if num:
                                orm = orm[i:]
                                continue
                            else:
                                break
                    await client.disconnect()
            tms = f'Message finished sent at \
            {dt.isoformat(dt.now().replace(microsecond = 0)).replace("T", " ")}'
            messagebox.showinfo('TeleTVG', tms, parent = self.root)
        except:
            messagebox.showinfo('TeleTVG', f'\n{sys.exc_info()}', parent = self.root)
            await client.disconnect()
            
    def multisched(self):
        if self.lock is False:        
            groups = [ 
                i  for i in os.listdir(
                    os.path.join(
                        'Telacc', 
                        self.chacc
                        )
                    ) if '_group' in i 
            ]
            if groups:
                if self.text.get('1.0', END)[:-1]:
                    sel = list(self.users)
                    self.lock = True
                    class MyDialog(simpledialog.Dialog):
                    
                        def body(self, master):
                            self.title('Choose Group')
                            Label(master, text="Group: ").grid(row=0, column = 0, sticky = E)
                            self.e1 = ttk.Combobox(master, state = 'readonly')
                            self.e1['values'] = groups
                            self.e1.current(0)
                            self.e1.grid(row=0, column=1)
                            return self.e1
                    
                        def apply(self):
                            self.result = self.e1.get()
                                        
                    d = MyDialog(self.root)
                    self.lock = False
                    if d.result:
                        tkd = os.path.join(
                            'Telacc', 
                            self.chacc, 
                            d.result, 
                            f'{d.result.rpartition("_")[0]}.json'
                        )
                        with open(tkd, 'r') as us:
                            rd = dict(json.load(us))
                        unsen = [
                            i for i in rd[
                                d.result.rpartition("_")[0]
                                ] if i not in sel
                        ]
                        if unsen:
                            messagebox.showinfo(
                                'TeleTVG', 
                                'There are {len(unsen)} user/s:\n{unsen}\nneed updated!', 
                                parent = self.root
                            )
                        else:
                            sen = [
                                i for i in rd[
                                    d.result.rpartition("_")[0]
                                    ] if i in sel
                            ]
                            if sen:
                                stm = dict(
                                    days = self.sp1v.get(), 
                                    hours = self.sp2v.get(), 
                                    minutes = self.sp3v.get(), 
                                    seconds = self.sp4v.get(),
                                )
                                asyncio.get_event_loop().run_until_complete(self.runs(stm, sen))
                            else:
                                messagebox.showinfo(
                                    'TeleTVG', 
                                    'This group is no longer exist, please delete it!', 
                                    parent = self.root
                                )
                else:
                    messagebox.showinfo('TeleTVG', 'No message to send?', parent = self.root)
                    
    def multisend(self, event = None):
        # Multiple send message to group, like broadcast.
        
        if self.lock is False:        
            groups = [ i  for i in os.listdir(os.path.join('Telacc', self.chacc)) if '_group' in i ]
            if groups:
                if self.text.get('1.0', END)[:-1]:
                    sel = list(self.users)
                    self.lock = True
                    class MyDialog(simpledialog.Dialog):
                    
                        def body(self, master):
                            self.title('Choose Group')
                            Label(master, text="Group: ").grid(row=0, column = 0, sticky = E)
                            self.e1 = ttk.Combobox(master, state = 'readonly')
                            self.e1['values'] = groups
                            self.e1.current(0)
                            self.e1.grid(row=0, column=1)
                            return self.e1
                    
                        def apply(self):
                            self.result = self.e1.get()
                                        
                    d = MyDialog(self.root)
                    self.lock = False
                    if d.result:
                        tkd = os.path.join(
                            'Telacc', 
                            self.chacc, 
                            d.result, 
                            f'{d.result.rpartition("_")[0]}.json'
                        )
                        with open(tkd, 'r') as us:
                            rd = dict(json.load(us))
                        unsen = [i for i in rd[d.result.rpartition("_")[0]] if i not in sel]
                        if unsen:
                            messagebox.showinfo(
                                'TeleTVG', 
                                f'There are {len(unsen)} user/s:\n{unsen}\nneed updated!', 
                                parent = self.root
                            )
                        else:
                            sen = [i for i in rd[d.result.rpartition("_")[0]] if i in sel]
                            if sen:
                                asyncio.get_event_loop().run_until_complete(self.mulsend(sen))
                            else:
                                messagebox.showinfo(
                                    'TeleTVG', 
                                    'This group is no longer exist, please delete it!', 
                                    parent = self.root
                                )
                else:
                    messagebox.showinfo('TeleTVG', 'No message to send?', parent = self.root)
                    
    def mulfile(self):
        # Send file to multi users.
        
        if self.lock is False:        
            groups = [ i  for i in os.listdir(os.path.join('Telacc', self.chacc)) if '_group' in i ]
            if groups:
                askfile = filedialog.askopenfilename(
                    initialdir = os.path.join(
                        self.orip.parent, 
                        'TVGPro'
                        ), 
                    filetypes = [("All files","*.*")], 
                    parent = self.root
                )
                if askfile:
                    sel = list(self.users)
                    self.lock = True
                    class MyDialog(simpledialog.Dialog):
                    
                        def body(self, master):
                            self.title('Choose Group')
                            Label(master, text="Group: ").grid(row=0, column = 0, sticky = E)
                            self.e1 = ttk.Combobox(master, state = 'readonly')
                            self.e1['values'] = groups
                            self.e1.current(0)
                            self.e1.grid(row=0, column=1)
                            return self.e1
                    
                        def apply(self):
                            self.result = self.e1.get()
                                        
                    d = MyDialog(self.root)
                    self.lock = False
                    if d.result:
                        tkd = os.path.join(
                            'Telacc', 
                            self.chacc, 
                            d.result, 
                            f'{d.result.rpartition("_")[0]}.json'
                        )
                        with open(tkd, 'r') as us:
                            rd = dict(json.load(us))
                        unsen = [i for i in rd[d.result.rpartition("_")[0]] if i not in sel]
                        if unsen:
                            messagebox.showinfo(
                                'TeleTVG', 
                                f'There are {len(unsen)} user/s:\n{unsen}\nneed updated!', 
                                parent = self.root
                            )
                        else:
                            sen = [i for i in rd[d.result.rpartition("_")[0]] if i in sel]
                            if sen:
                                asyncio.get_event_loop().run_until_complete(
                                    self.mulsend(sen, askfile)
                                )
                            else:
                                messagebox.showinfo(
                                    'TeleTVG', 
                                    'This group is no longer exist, please delete it!', 
                                    parent = self.root
                                )
                else:
                    messagebox.showinfo('TeleTVG', 'Send files aborted!', parent = self.root)
                    
    async def logout(self):
        # Log out from Telegram.
        
        try:
            async with TelegramClient('ReminderTel', self.api_id, self.api_hash) as client:
                self.result = await client.log_out()
        except Exception as e:
            messagebox.showerror('TeleTVG', f'{e}')
            
    def lg(self):
        # Call Async Log Out from Telegram.
        
        ask = messagebox.askyesno(
            'TeleTVG', 
            'Do you really want to log-out?\n[You have to log-in again next time, all over again!]'
        )
        if ask:
            asyncio.get_event_loop().run_until_complete(self.logout())
            if self.result:
                ask = messagebox.askyesno(
                    'TeleTVG', 
                    'Delete account folder and its sub-folders?', 
                    parent = self.root
                )
                if ask: shutil.rmtree(os.path.join('Telacc', self.chacc))
                self.winexit()
                
    def opfold(self):
        # Open folder for all downloaded files folders.
        
        path = os.path.join(self.orip.parent, 'TeleTVGPro')
        if os.listdir(path):
            if self.plat.startswith('win'):
                os.startfile(path)
            else:
                os.system(f'open "{path}"')
        else:
            messagebox.showinfo('TeleTVG', 'No downloded files yet!')

    def help(self, event = None):
        # Help function, that open tutorial pdf.
        
        pth = Path(__file__)
        if os.path.exists(pth.joinpath(pth.parent, 'TeleTVG.pdf')):
            if self.plat.startswith('win'):
                os.startfile(os.path.join(pth.parent, 'TeleTVG.pdf'))
            else:
                os.system(f'open "{os.path.join(pth.parent, "TeleTVG.pdf")}"')
        del pth

def bepath():
    # checking path.
    
    if platform.startswith('win'):
        chpth = Path(os.path.expanduser('~')).joinpath('appdata', 'local', 'TTVG')
    else:
        chpth = Path(os.path.expanduser('~')).joinpath('TTVG')
    if os.path.isdir(chpth):
        os.chdir(chpth)
    else:
        os.mkdir(chpth)
        os.chdir(chpth)
    del chpth

def dial(root, b: int = 0):
    # SimpleDialog for Log-in.
    
    if b and b <= 2:
        txt = 'Code: ' if b == 1 else 'Password: '
    else:
        txt = 'Telephone: '
        
    class MyDialog(simpledialog.Dialog):
                
        def body(self, master):
            Label(master, text = txt).grid(row=0, column = 0, sticky = E)
            self.e1 = ttk.Entry(master, show = '●')
            self.e1.grid(row=0, column=1)
            return self.e1
    
        def apply(self):
            self.result = self.e1.get()
                        
    d = MyDialog(root)
    if (a := d.result if d.result else None):
        del d
        return a
    del d

def cenen(root):
    # Creating Telegram APIs with encryption to environment.
    
    if os.environ.get('TELE_API') and os.environ.get('TELE_HASH'):
        class MyDialog(simpledialog.Dialog):

            def body(self, master):
                Label(master, text = 'Password: ').grid(row=0, column = 0, sticky = E)
                self.e1 = ttk.Entry(master, show = '●')
                self.e1.grid(row = 0, column = 1)
                return self.e1
    
            def apply(self):
                self.result = self.e1.get()
                
        d = MyDialog(root)
        if d.result:
            v = io.StringIO()
            with redirect_stdout(v):
                ta = reading(os.environ.get('TELE_API'), d.result)
                th = reading(os.environ.get('TELE_HASH'), d.result)
            v.flush()
            if ta and th:
                del d
                return ta, th
            else:
                del d
                return None
        else:
            del d
            return None
    else:
        class ApiDialog(simpledialog.Dialog):
                
            def body(self, master):
                Label(master, text = 'API: ').grid(row=0, column = 0, sticky = E)
                self.e1 = ttk.Entry(master, show = '●')
                self.e1.grid(row = 0, column = 1)
                Label(master, text = 'Hash: ').grid(row=1, column = 0, sticky = E)
                self.e2 = ttk.Entry(master, show = '●')
                self.e2.grid(row = 1, column = 1)
                Label(master, text = 'Password: ').grid(row=2, column = 0, sticky = E)
                self.e3 = ttk.Entry(master, show = '●')
                self.e3.grid(row = 2, column = 1)
                return self.e1
        
            def apply(self):
                self.result = self.e1.get(), self.e2.get(), self.e3.get() 
                        
        d = ApiDialog(root)
        if d.result:
            if all([d.result[0], d.result[1], d.result[2]]):
                v = io.StringIO()
                with redirect_stdout(v):                
                    cmsk(d.result[0], d.result[2], 'TELE_API')
                    cmsk(d.result[1], d.result[2], 'TELE_HASH')
                messagebox.showinfo(
                    'TeleTVG', 
                    f'{v.getvalue()}\nPlease restart again!'
                )
                v.flush()
                root.destroy()
            else:
                messagebox.showinfo('TeleTVG', 'Incomplete!!!')
                root.destroy()
        else:
            root.destroy()
            
def main():
    # Start app.
    # Please create encryption for app_id and app_hash for security.
    
    bepath()
    if all(i in os.environ for i in ['TELE_API', 'TELE_HASH']):
        ope = os.path.join(os.getcwd(), 's_error.tvg')
        if not 'TeleTVGPro' in os.listdir():
            os.mkdir('TeleTVGPro')
        if 'Tele_TVG' in os.listdir():
            os.chdir('Tele_TVG')
        else:
            os.mkdir('Tele_TVG')
            os.chdir('Tele_TVG')
        root = Tk()
        root.withdraw()
        
        if os.path.exists(ope):
            try:
                if os.path.exists('ReminderTel.session'): 
                    os.remove('ReminderTel.session')
                os.remove(ope)
            except Exception as e:
                messagebox.showerror('TeleTVG', f'{e}', parent = root)
                root.destroy()
        if not os.path.exists('Telacc'):
            os.mkdir('Telacc')
        getah = cenen(root)
        if getah:
            api = getah[0]
            hash_ = getah[1]
            Reminder.API = api
            Reminder.HASH_ = hash_
            del getah
            begin = Reminder(root)
            if not os.path.exists('ReminderTel.session'):
                if (ask := dial(begin.root)):
                    try:
                        # Reference stdout to variable:
                        # https://stackoverflow.com/questions/16571150/
                        # how-to-capture-stdout-output-from-a-python-function-call
                        v = io.StringIO()
                        with redirect_stdout(v):
                            client = TelegramClient(
                                'ReminderTel', 
                                api, 
                                hash_
                                ).start(
                                    ask, 
                                    lambda: dial(begin.root, 2),
                                    code_callback = lambda: dial(begin.root, 1)
                            )
                        client.disconnect()
                        messagebox.showinfo('TeleTVG', f'{v.getvalue()[:-1]}')
                        v.flush()
                        try:
                            del api, hash_
                            asyncio.get_event_loop().run_until_complete(
                                begin.acc()
                            )
                            asyncio.get_event_loop().run_until_complete(
                                begin.filcomb()
                            )
                            begin.entto.focus_force()
                            begin.root.deiconify()
                            begin.root.mainloop()
                        except:
                            with open(ope, 'w') as ers:
                                ers.write(str(sys.exc_info()))                    
                            messagebox.showerror('TreeViewGui', f'{sys.exc_info()}')
                            begin.winexit()                    
                    except:
                        with open(ope, 'w') as ers:
                            ers.write(str(sys.exc_info()))
                        messagebox.showinfo('TeleTVG', sys.exc_info())
                        begin.winexit()
                else:
                    messagebox.showinfo('TeleTVG', 'Log-in Aborted!!!')
                    begin.winexit()                
            else:
                try:
                    del api, hash_
                    asyncio.get_event_loop().run_until_complete(
                        begin.acc()
                    )
                    asyncio.get_event_loop().run_until_complete(
                        begin.filcomb()
                    )
                    begin.entto.focus_force()
                    begin.root.deiconify()
                    begin.root.mainloop()
                except:
                    with open(ope, 'w') as ers:
                        ers.write(str(sys.exc_info()))                    
                    messagebox.showerror(
                        'TreeViewGui', 
                        f'{sys.exc_info()}', 
                        parent = begin.root
                    )
                    begin.winexit()
        else:
            messagebox.showinfo('TeleTVG', 'Please give right password!!!')
            root.destroy()
    else:
        root = Tk()
        root.withdraw()
        cenen(root)

if __name__ == '__main__':
    main()
    