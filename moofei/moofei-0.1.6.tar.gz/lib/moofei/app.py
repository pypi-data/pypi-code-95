#!/usr/bin/python
# -*- coding: utf-8 -*-
# editor: mufei(ypdh@qq.com tel:+086 15712150708)
'''
Mufei _ __ ___   ___   ___  / _| ___(_)
| '_ ` _ \ / _ \ / _ \| |_ / _ \ |
| | | | | | (_) | (_) |  _|  __/ |
|_| |_| |_|\___/ \___/|_|  \___|_|
'''
__all__ = ['app', 'auth']

#: python -m pip install python-dotenv
#：python -m moofei.find 127.0.0.1:5000 --webbrowser
#：python find 127.0.0.1:5000 --webbrowser
    

import os, sys, time, re, json
from moofei.valid.flask_valid import *
try:
    from _app import static_file, finds, stopPros, infoPros, pageView
    from valid.flask_httpauth import HTTPDigestAuth 
except:
    from moofei._app import static_file, finds, stopPros, infoPros, pageView
    from moofei.valid.flask_httpauth import HTTPDigestAuth
from flask import Flask, request, render_template
import uuid
from random import choice
from string import ascii_letters, digits
all_chs = ascii_letters + digits

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
Conf_Pth = os.path.join(BASE_DIR, '.conf')
app = Flask(__name__)
app.config['SECRET_KEY'] = str(uuid.uuid1())

config = None
if os.path.isfile(Conf_Pth):
    config = json.loads(open(Conf_Pth).read())
users = config and config.get('users') or {"admin": ''.join([choice(all_chs) for i in range(8)])}    
print(' * Login username And password For:', users)
auth = HTTPDigestAuth(realm='moofei')
    
@auth.get_password
def get_pw(username): 
    return users.get(username)
    
@auth.get_has_ignore
def has_ignore():
    #return False
    return request.remote_addr=='127.0.0.1'

    