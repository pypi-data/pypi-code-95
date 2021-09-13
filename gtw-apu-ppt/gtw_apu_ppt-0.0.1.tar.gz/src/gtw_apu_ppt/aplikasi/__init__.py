import os
import yaml
import logging
import logging.config
from flask_cors import CORS
from flasgger import Swagger
from setting.config import Config
from importlib import import_module
from flask import g, Flask, request, jsonify


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    # CORS Headers
    CORS(app)
    # setup blueprint
    setup_blueprint(app)
    # setup swagger
    setup_swagger(app)
    # setup middleware
    setup_middleware(app)
    # setup logging
    setup_logger()
    return app

def is_valid_element(prime_fields, client_request):
    # Melakukan pengecekan mandatory field harus ada pada saat client request
    return not set(prime_fields) <= set(client_request)

def setup_logger():
    with open('setting/logging.yaml', 'r') as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
        f.close()


def setup_blueprint(app):
    """ Semua folder modul harus ada file __init__.py """
    base = os.path.abspath(os.path.dirname(__file__))
    listdir = [n for n in os.listdir(base) if os.path.isdir(f"{base}/{n}")]

    for modul in listdir:
        try:
            m = import_module(f"aplikasi.{modul}.routes")
            app.register_blueprint(m.blueprint)
        except ModuleNotFoundError:
            continue


def setup_swagger(app):
    # Setup Swagger
    app.config['SWAGGER'] = {
        'title': 'Gateway APU-PPT',
        'description': 'API Pendukung Gateway APU-PPT',
        'uiversion': 3
    }
    Swagger(app, template_file='../doc/apu_ppt.yaml')


def setup_middleware(app):
    @app.before_request
    def check_mode_aplikasi():
        if request.path.startswith('/apidocs'):
            # hanya mode development yag bisa buka dokumentasi
            if app.config['APP_MODE'].lower() == 'development':
                return
            return jsonify({'status': 'Ilegal Access'}), 405

        if request.path.startswith('/apispec_1.json'):
            # hanya mode development bisa membuka dokumentasi
            if app.config['APP_MODE'].lower() == 'development':
                return
            return jsonify({'status': 'Ilegal Access'}), 405

        if request.path.startswith('/flasgger_static'):
            return

    @app.after_request
    def after_request(response):
        response.headers['Cache-Control'] = 'public, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        return response

    @app.teardown_appcontext
    def close_context(error):
        """ Paksa tutup koneksi database, clean header dan cloud """
        if hasattr(g, 'db_rekonsiliasi'):
            try:
                g.db_rekon.close()
            except Exception:
                pass
