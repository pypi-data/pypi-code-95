from __init__ import *
from mathematics import *
from password import *
from word import *
from word_bank import *
import os

def _clear():
    try:
        for root, dirs, files in os.walk('__pycache__', topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
        os.rmdir('__pycache__')
    except OSError:
        pass
    try:
        for root, dirs, files in os.walk('word_bank/__pycache__', topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
        os.rmdir('word_bank/__pycache__')
    except OSError:
        pass
    return True

def _test_pyextension():
    computer
    computer()
    python
    python()
    opensource('pyextension')
    opensource('math')
    opensource('password')
    opensource('word bank')
    opensource('word bank data')
    opensource('word')
    message()
    description()
    license()
    word_bank()
    _clear()
    return True

def _test_math():
    floatdd(1.23)
    fibo(5)
    fibo(found=5)
    fibo(to=5)
    arithmetic_sequence('all', '12345')
    _clear()
    return True

def _test_password():
    decrypt1(encrypt1('abc', 'abcdefg')[0], encrypt1('abc', 'abcdefg')[1])
    decrypt2(encrypt2('abc', 'abcdefg', 5)[0], encrypt2('abc', 'abcdefg', 5)[1])
    decrypt3(encrypt3('abc', 'abcdefg', 'sky')[0], encrypt3('abc', 'abcdefg', 'sky')[1])
    _clear()
    return True

def _test_wordbank():
    a = Word()
    a.search('a')
    a.get()
    _clear()
    try:
        os.remove('word bank.dat')
    except OSError:
        pass
    return True

def _test_word():
    add_text('abc')
    add_heading('abc')
    _clear()
    return True

def _test(module='all'):
    if module == 'all':
        return (
            _test_pyextension(),
            _test_math(),
            _test_password(),
            _test_wordbank(),
            _test_word()
            )
    elif module == 'pyextension':
        return _test_pyextension()
    elif module == 'math':
        return _test_math()
    elif module == 'password':
        return _test_password()
    elif module == 'word bank' or module == 'word_bank':
        return _test_wordbank()
    elif module == 'word':
        return _test_word()

_test()
