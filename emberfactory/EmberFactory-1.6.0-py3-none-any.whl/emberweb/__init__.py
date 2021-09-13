# -*- coding: utf-8 -*-
__version__ = '1.6.0'
"""
                 EmberFactory / web application

This script creates the Flask web app.
The user interface is managed by the 'control.py' module
The drawing code is in the 'embermaker' package.

Copyright (C) 2020  philippe.marbaix@uclouvain.be
"""
import os
import sys
from flask import Flask
from emberweb import control, sitenav
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.middleware.profiler import ProfilerMiddleware
from embermaker import makember as mke
from apscheduler.schedulers.background import BackgroundScheduler

# There are two version numbers: the main one above, and a specific version for the embermaker part;
# the idea is that if the main version changes, but not the embermaker part, there is no change in the procuced
# graphics at all (=> there are only changes related to user interface, documentation, etc.)


def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    # Default configuration
    # Maximum size of uploaded files (as security measure, see
    # https://stackoverflow.com/questions/31873989/rejecting-files-greater-than-a-certain-amount-with-flask-uploads )
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
    # A secret key is needed to store the user's preference about deleting his/her files in a cookie
    # You may change this in your emberfactory.cfg file (below), but afaik the only thing we are protecting here is
    # a choice made by the user, so I guess that it is not really important to have a hard-to-guess real 'secret' key.
    app.config["SECRET_KEY"] = "default-EF-key"
    app.config['SESSION_COOKIE_SAMESITE'] = "Strict"
    app.config['UI_PREFERRED_COLOR_SPACE'] = "standard"

    # Read configuration from a file in the instance folder if it exists (silent = may fail)
    app.config.from_pyfile(os.path.join(app.instance_path, 'emberfactory.cfg'), silent=True)

    # By default, the root path for this app will be '/', this is practical to run it locally;
    # However, if you want to have a different root path, such as '/embermaker' just put it in the config
    # file read above, using the configuration parameter APPLICATION_ROOT.
    # Note that this is not the standard use of APPLICATION ROOT (it normally does not apply inside requests,
    # see https://flask.palletsprojects.com/en/1.1.x/config/ )
    app_root = app.config["APPLICATION_ROOT"]
    # The Dispatcher may combine several apps with different root path; here we have only one app,
    # so either the url starts with app_root and this app will process it, or it fails ('dummy_app').
    # https://flask.palletsprojects.com/en/1.1.x/patterns/appdispatch/#app-dispatch
    # AFAIK, the following combines our app (for app_root based urls) and a dummy app (for other cases)
    if app_root != '/':
        app.wsgi_app = DispatcherMiddleware(Flask('dummy_app'), {app_root: app.wsgi_app})

    # Ensure the instance directory and subdirectories exists
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(os.path.join(app.instance_path, 'in/'), exist_ok=True)

    # Set version information in the app's Jinja context => available in the base template and all pages
    @app.context_processor
    def inject_version():
        version = {'main': __version__,
                   'embermaker': mke.__version__,
                   'isbeta': 'b' in mke.__version__ or 'b' in __version__,
                   'isalpha': 'a' in mke.__version__ or 'a' in __version__}
        return dict(version=version)

    # Set jinja2 options to avoid blank lines in the html output where the template contains jinja code blocks:
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    # Register blueprints
    app.register_blueprint(control.bp)
    app.register_blueprint(sitenav.bp)

    app.add_url_rule("/", endpoint="sitenav.index")

    # If debugger is active, add profiling:
    gettrace = getattr(sys, 'gettrace', None)
    if gettrace():
        # Enable profiling
        app.config["PROFILE"] = True
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=['EmberFactory', 30], sort_by=('tottime', 'time'))

    app.scheduler = BackgroundScheduler()
    app.scheduler.start()

    return app
