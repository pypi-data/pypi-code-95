from __init__ import *
from blackboard import *
from system import *
from timer import *
from tix import *
from tix.filedialog import *
from turtledrawer import *
import os

def _clear():
    try:
        for root, dirs, files in os.walk('__pycache__', topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
        os.rmdir('__pycache__')
    except OSError:
        pass
    return True

def _test_tkextension():
    askvalue()
    askitem()
    askanswer()
    askyesnocancel()
    controlboard()
    singlechoices()
    answersheet()
    _clear()
    return True

def _test_blackboard():
    tk = Tk()
    tk.title('_test_blackboard')
    # Tkinter
    x = tk.winfo_screenwidth()
    y = tk.winfo_screenheight()
    BlackBoard(tk, width=x - 100, height=y - 250).place(relx=0.5, rely=0.5, relheight=1, relwidth=1, anchor='center')
    tk.mainloop()
    _clear()
    return True

def _test_system():
    opensource('tkextension')
    opensource('blackboard')
    opensource('test')
    opensource('timer')
    opensource('tix')
    opensource('tix.filedialog')
    opensource('turtledrawer')
    _clear()
    return True

def _test_timer():
    tk = Tk()
    tk.title('_test_timer')
    # Tkinter
    Timer(tk, 'timer', 1)
    Timer(tk, 'down count', 1)
    Timer(tk, 'alarm clock', 1)
    _clear()
    return True

def _test_tix():
    tk = Tk()
    tk.title('_test_tix')
    # Tkinter
    AskValue(tk)
    AskItem(tk)
    AskAnswer(tk)
    v = IntVar()
    ControlBoard(tk)
    SingleChoices(tk)
    AnswerSheet(tk)
    _clear()
    return True

def _test_tix_filedialog():
    tk = Tk()
    tk.title('_test_tix_filedialog')
    # Tkinter
    FileTree(tk)
    _clear()
    return True

def _test_turtledrawer():
    a = Draw()
    a.create_triangle(5)
    a.create_rectangle(5, 5)
    a.create_pentagon(5)
    a.create_polygon(6, 5)
    a.create_pg(4, 5)
    a.create_pg1(4, 5)
    a.create_koch(3)
    a.create_koch_snowflake(3)
    _clear()
    return True

def _test(module='all'):
    if module == 'all':
        return (
            _test_tkextension(),
            _test_blackboard(),
            _test_system(),
            _test_timer(),
            _test_tix(),
            _test_tix_filedialog(),
            _test_turtledrawer()
            )
    elif module == 'tkextension':
        return _test_tkextension()
    elif module == 'blackboard':
        return _test_blackboard()
    elif module == 'system':
        return _test_system()
    elif module == 'timer':
        return _test_timer()
    elif module == 'tix':
        return _test_tix()
    elif module == 'tix.filedialog':
        return _test_tix_filedialog()
    elif module == 'turtledrawer':
        return _test_turtledrawer()
