#!/usr/bin/python
# -*- coding: utf-8 -*-
# editor: mufei(ypdh@qq.com tel:+086 15712150708)
'''
Mufei _ __ ___   ___   ___  / _| ___(_)
| '_ ` _ \ / _ \ / _ \| |_ / _ \ |
| | | | | | (_) | (_) |  _|  __/ |
|_| |_| |_|\___/ \___/|_|  \___|_|
'''
__all__ = ['app']

#: python -m pip install python-dotenv
#：python -m moofei.find 127.0.0.1:5000 --webbrowser
#：python find 127.0.0.1:5000 --webbrowser
    

import os, sys, time, re, json
from moofei.valid.flask_valid import *
try:
    from _app import static_file, finds, stopPros, infoPros, pageView
    from valid.flask_httpauth import HTTPDigestAuth
    from app import app,auth    
except:
    from moofei._app import static_file, finds, stopPros, infoPros, pageView
    from moofei.valid.flask_httpauth import HTTPDigestAuth
    from moofei.app import app,auth
from flask import Flask, request, render_template
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

              
@app.route("/")
@app.route("/<path>")
@auth.login_required
def index(path=""): 
    return static_file(path)
       
@app.route("/get_find", methods=["POST"])
@auth.login_required
def get_find(): 
    return call_request_wrap(infoPros)()    
    
@app.route("/stop_find", methods=["POST"])
@auth.login_required
def stop_find(): 
    return call_request_wrap(stopPros)() 
               
@app.route("/find", methods=["POST"])
@auth.login_required
def find_files_or_words():
    backupdir = './.backup'
    return call_request_wrap(finds)(backupdir=backupdir)
       
@app.route("/find_download", methods=["POST","GET"])
@auth.login_required
def find_download(): 
    fpath = request.args.get('file')
    is_zip = request.args.get('is_zip')
    as_attachment = False if  request.args.get('is_view') else True
    if not is_zip and not as_attachment:
        if os.path.isfile(fpath) and os.stat(fpath).st_size>3*1024: #*1024:
            return page_view()
    return static_file(fpath, is_static=0, is_zip=is_zip, as_attachment=as_attachment) 

@app.route("/view.html", methods=["POST","GET"])
@auth.login_required
def page_view():
    context = valid.request(pageView,  request)
    if context is None:
        return render_template('cat_view.html')
    return render_template('view.html', rs=context)

if __name__ == "__main__":
    try:
        import colorama; colorama.init(autoreset=True, wrap=True)
    except ImportError:
        pass    
    app.run() #host='0.0.0.0', debug=True

    