# -*- coding=utf-8 -*-

def opensource(module='tkextension'):
    if module == 'tkextension' or module == '__init__':
        file = open('__init__.py')
        get = file.read()
        file.close()
        return get
    elif module == 'blackboard':
        file = open('blackboard.py')
        get = file.read()
        file.close()
        return get
    elif module == 'timer':
        file = open('timer.py')
        get = file.read()
        file.close()
        return get
    elif module == 'tix':
        file = open('tix.py')
        get = file.read()
        file.close()
        return get
    elif module == 'ttk':
        file = open('ttk.py')
        get = file.read()
        file.close()
        return get
    elif module == 'turtle':
        file = open('tuter.py')
        get = file.read()
        file.close()
        return get
    elif module == 'system':
        file = open('system.py')
        get = file.read()
        file.close()
        return get
    else:
        raise AttributeError('\'opensource\' object has no attribute \'%s\'' % module)
