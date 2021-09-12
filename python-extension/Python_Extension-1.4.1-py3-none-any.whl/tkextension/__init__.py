# -*- coding:utf-8  -*-

import sys
if sys.version_info[0] != 3 or sys.version_info[1] < 4:
    raise SystemExit('This module needs Python 3.4 or more later')

class AV:
    finish = ''
def s1(event):
    AV.finish = None
def s2(event):
    AV.finish = False
def s3(event):
    AV.finish = True
# Askyesnocancel Value

from tkinter import *
from tkinter.messagebox import *
from tkinter.filedialog import *
import tkextension.tix as tix
import platform
import pickle
import time

def askvalue(title='', msg='', args=(0, 100), lock=True):
    tk = Tk()
    tk.title(title)
    tk.resizable(0, 0)
    if platform.system() == 'Windows' and lock == True:
        tk.attributes('-disabled', True)
    # Tkinter
    if msg != '':
        Label(tk, text=msg).pack()
    if type(args[0]) == type(0):
        sb = Scale(tk, from_=args[0], to=args[1], orient='horizontal')
    elif type(args[0]) == type('0'):
        sb = Spinbox(tk, values=args, wrap=True)
    else:
        raise TypeError('%s\'s items must be int or string')
    sb.pack()
    Button(tk, text='OK', command=tk.quit).pack()
    # Window
    tk.mainloop()
    # Mainloop
    get = sb.get()
    tk.destroy()
    return get
# Askvalue
def askitem(title='', msg='', items=[], number=1, normal=0, lock=True):
    tk = Tk()
    tk.title(title)
    if platform.system() == 'Windows' and lock == True:
        tk.attributes('-disabled', True)
    # Tkinter
    if msg != '':
        Label(tk, text=msg).place(relx=0.5, rely=0.05, relwidth=1, relheight=0.1, anchor='center')#, selectmode='multiple')
    lb = Listbox(tk)
    lb.place(relx=0.5, rely=0.5, relwidth=0.8, relheight=0.8, anchor='center')
    lb.selection_set(normal)
    Button(tk, text='OK', command=tk.quit).place(relx=0.5, rely=0.95, relwidth=1, relheight=0.1, anchor='center')
    # Window
    for x in range(0, len(items)):
        lb.insert('end', items[x])
    # Load
    tk.mainloop()
    # Mainloop
    finish = False
    get = []
    while not finish:
        tk.mainloop()
        for x in range(0, len(items)):
            if lb.selection_includes(x) == 1:
                get.append(x)
        # Get
        if len(get) == number:
            finish = True
        else:
            get.append(normal)
    # Check & Get
    tk.destroy()
    return get
# Askitem
def askyesnocancel(title='', msg='', lock=True):
    tk = Tk()
    tk.title(title)
    tk.resizable(0, 0)
    if platform.system() == 'Windows' and lock == True:
        tk.attributes('-disabled', True)
    # Tkinter
    if msg != '':
        Label(tk, text=msg).grid(column=0, row=0, columnspan=4)
    b1 = Button(tk, text='Cancel')
    b1.grid(column=0, row=1)
    b2 = Button(tk, text='No')
    b2.grid(column=2, row=1)
    b3 = Button(tk, text='Yes')
    b3.grid(column=3, row=1)
    # Tkinter
    b1.bind('<Button-1>', s1)
    b2.bind('<Button-1>', s2)
    b3.bind('<Button-1>', s3)
    # Bind
    while AV.finish == '':
        tk.update()
        time.sleep(0.01)
    # Mainloop
    tk.destroy()
    return AV.finish
# Askyesnocancel
def askanswer(title='', msg='', lock=True, validate=None, validatecommand=None, invalidcommand=None):
    tk = Tk()
    tk.title(title)
    tk.resizable(0, 0)
    if platform.system() == 'Windows' and lock == True:
        tk.attributes('-disabled', True)
    # Tkinter
    if msg != '':
        Label(tk, text=msg).pack()
    if validate != None:
        entry = Entry(tk, width=30)
    else:
        if invalidcommand == None:
            entry = Entry(tk, width=30, validate=validate, validatecommand=validatecommand)
        else:
            entry = Entry(tk, width=30, validate=validate, validatecommand=validatecommand, invalidcommand=invalidcommand)
    entry.pack()
    Button(tk, text='Finish', command=tk.quit).pack()
    # Window
    tk.mainloop()
    # Mainloop
    get = entry.get()
    tk.destroy()
    return get
# Askanswer
def controlboard(title='', msg='', item=[('scale', '', 1, 100), ('listbox', '', [1, 2, 3]), ('radiobutton', '', '1', '<IntVar>', 1)], lock=True):
    tk = Tk()
    tk.title(title)
    tk.minsize(width=100, height=100)
    if platform.system() == 'Windows' and lock == True:
        tk.attributes('-disabled', True)
    # Tkinter
    text = Text(tk)
    text.pack()
    # Text
    if msg != '':
        label = Label(tk, text=msg)
        text.window_create('end', window=label)
        text.insert('end', '\n')
    # Label
    window = []
    window_list = []
    value_list = []
    for x in item:
        if x[0] == 'scale':
            window.append(Scale(tk, from_=x[2], to=x[3], orient='horizontal'))
            window_list.append('scale')
        elif x[0] == 'listbox':
            window.append(Listbox(tk))
            window_list.append('listbox')
            for y in x[2]:
                window[-1].insert('end', y)
        elif x[0] == 'radiobutton':
            value_list.append(x[3])
            window.append(Radiobutton(tk, text=x[2], variable=x[3], value=x[4]))
            window_list.append('radiobutton')
    for x in range(0, len(item)):
        if item[x][1] != '':
            text.insert('end', item[x][1])
        text.window_create('end', window=window[x])
        text.insert('end', '\n')
    # Scale & Listbox & Radobutton
    text.config(state='disabled')
    # Text
    button = Button(tk, text='Finish', command=tk.quit)
    text.window_create('end', window=button)
    # Button
    # Window
    tk.mainloop()
    # Mainloop
    result = []
    for x in (0, len(window) - 1):
        if window_list[x] == 'scale':
            result.append(window[x].get())
        elif window_list[x] == 'listbox':
            for y in range(0, len(item[x][2])):
                if window[x].selection_includes(y) == 1:
                    result.append(item[x][2][y])
                    break
            if len(result) < x + 1:
                result.append(item[x][2][0])
        elif window_list[x] == 'radiobutton':
            result.append(item[x][3].get())
        else:
            raise SystemExit
    tk.destroy()
    return result
# Controlboard
def singlechoices(title='', msg='', args=(('a', 'b', 'c'), ('e', 'f', 'g')), lock=True):
    tk = Tk()
    tk.title(title)
    tk.resizable(0, 0)
    if platform.system() == 'Windows' and lock == True:
        tk.attributes('-disabled', True)
    # Tkinter
    a = tix.SingleChoices(tk, msg=msg, args=args)
    a.pack()
    Button(tk, text='Finish', command=tk.quit).pack()
    # Window
    tk.mainloop()
    # Mainloop
    get = a.get()
    tk.destroy()
    return get
# Singlechoices
def answersheet(title='', msg='', args=[('a', 'b', 'c')], answer=['a'], points=[1], lock=True):
    tk = Tk()
    tk.title(title)
    tk.resizable(0, 0)
    if platform.system() == 'Windows' and lock == True:
        tk.attributes('-disabled', True)
    # Tkinter
    a = tix.AnswerSheet(tk, msg=msg, args=args, answer=answer, points=points)
    a.pack()
    Button(tk, text='Finish', command=tk.quit).pack()
    # Window
    tk.mainloop()
    # Mainloop
    get = a.get()
    tk.destroy()
    return get
# Answersheet
def create(tkinter_attribute, mode='menu', args=[('1', '<function>')], AddToTkinter=(False, 'grid', 0, 0, 0, 0, 'center'), note='''Args of option menu only takes strings, likes: arg=['a', 'b', 'c']'''):
    tk = tkinter_attribute
    if mode == 'menu':
        a = Menu(tk)
        for x in args:
            a.add_command(label=x[0], command=x[1])
        if AddToTkinter[0] == True:
            tk.config(menu=a)
        return a
    elif mode == 'option menu':
        v = StringVar()
        a = 'OptionMenu(tk, v, '
        for x in arg:
            a = a + '\'' + x + '\''
            if x != args[-1]:
                a = a + ', '
        a = a + ')'
        b = exec(a)
        if AddToTkinter[0] == True:
            if AddToTkinter[1] == 'pack':
                b.pack()
            elif AddToTkinter[1] == 'grid':
                if AddToTkinter[4] == 0:
                    AddToTkinter[4] = 1
                if AddToTkinter[5] == 0:
                    AddToTkinter[5] = 1
                if AddToTkinter[6] == 'center':
                    AddToTkinter[6] = 'w'
                b.grid(column=AddToTkinter[2], row=AddToTkinter[3],
                       columnspan=AddToTkinter[4], rowspan=AddToTkinter[5],
                       sticky=AddToTkinter[6])
            elif AddToTkinter[1] == 'place':
                if AddToTkinter[4] != 0 and AddToTkinter[5] != 0:
                    b.place(relx=AddToTkinter[2], rely=AddToTkinter[3],
                            relwidth=AddToTkinter[4], relheight=AddToTkinter[5],
                            anchor=AddToTkinter[6])
                elif AddToTkinter[4] == 0 and AddToTkinter[5] == 0:
                    b.place(relx=AddToTkinter[2], rely=AddToTkinter[3],
                            anchor=AddToTkinter[6])
                else:
                    raise ValueError('Both relwidth and relheight must be 0 or not 0')
        return b
# Create
