import pygeoip
import tkinter
from tkinter import *


"""
Disclaimer this for educational purposes only I am not responsible for your actions
by using this program you accept sole responsibility

developed by clive hunt
"""

root = Tk()
label1 = Label(root, text='Enter Target IP :')
e = Entry(root)
label1.pack()
e.pack()


def click():
    try:
        gip = pygeoip.GeoIP('C:\\Users\\d\\geo2ip\\GeoLiteCity.dat')
        x = gip.record_by_addr(e.get())
        for key, val in x.items():
            print(key, val)
            label2 = Label(root, text=key)
            label0 = Label(root, text=val)
            label0.pack()
            label2.pack()
    except Exception:
        print("please enter a real ip: ")
        # runs programme until a correct ip is entered


button1 = Button(root, text='Submit', command=click)
button1.pack()
button1.bind('<Button-1>')
root.mainloop()
