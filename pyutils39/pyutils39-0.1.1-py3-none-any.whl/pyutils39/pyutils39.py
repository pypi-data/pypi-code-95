#WHY WON"T IT UPLOAD RIGHT!?!
from tkinter import Tk, messagebox
def reverse(data):
    x = str(data)
    datalen = len(data)
    x = x[datalen::-1]
    return x
def consoleask(question):
    while True:
        print(str(question)+' (Y/N)')
        x = input()
        if x.lower().startswith('y'):
            return True
            break
        elif x.lower().startswith('n'):
            return False
            break
def error(message,title='Error'):
    title = str(title)
    message = str(message)
    Tk().withdraw()
    messagebox.showerror(title,message)
def toplevelerror(message,title='Error'):
    title = str(title)
    message = str(message)
    root = Tk()
    root.wm_attributes("-topmost",True)
    root.withdraw()
    messagebox.showerror(title,message)
        

def question(message,title='Question'):
    title = str(title)
    message = str(message)
    Tk().withdraw()
    x = messagebox.askyesno(title,message)
    return x
def toplevelquestion(message,title='Question'):
    title = str(title)
    message = str(message)
    root = Tk()
    root.wm_attributes("-topmost",True)
    root.withdraw()
    x = messagebox.askyesno(title,message)
    return x
        