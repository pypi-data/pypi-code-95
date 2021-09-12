# -*- coding:utf-8  -*-

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
    elif module == 'test':
        file = open('test.py')
        get = file.read()
        file.close()
        return get
    elif module == 'timer':
        file = open('timer.py')
        get = file.read()
        file.close()
        return get
    elif module == 'tix':
        file = open('tix/__init__.py')
        get = file.read()
        file.close()
        return get
    elif module == 'tix.filedialog' or module == 'filedialog':
        file = open('tix/filedialog.py')
        get = file.read()
        file.close()
        return get
    elif module == 'turtledrawer':
        file = open('turtledrawer.py')
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
