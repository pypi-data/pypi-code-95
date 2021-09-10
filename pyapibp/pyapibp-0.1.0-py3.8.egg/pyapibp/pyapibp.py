import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

import os, uuid, shutil
from PyInquirer import prompt

from ._style import STYLE
from ._questions import *
from ._blueprints import *

class pyapibp:
    def __init__(self, test_mode=False) -> None:
        logging.info(f'Welcome to the Python boilerplate code generator for API\'s')

        _base_cwd = os.getcwd()
        self._flask_d = os.path.join(_base_cwd, 'pyapibp/_flask')

        existing = prompt(FOLDER, style=STYLE)['existing']
        if existing:
            logging.info(f'Make sure to navigate to it')
            answers = prompt(GENERAL[1:], style=STYLE)
        else:
            answers = prompt(GENERAL, style=STYLE)

        if not existing:
            os.makedirs(answers['title'])
            os.chdir(answers['title'])

        if answers['framework'] == 'flask':
            self._flask_bp()
        elif answers['framework'] == 'fastapi':
            raise NotImplementedError('FastAPI is not implemented yet')
        elif answers['framework'] == 'django':
            raise NotImplementedError('Django is not implemented yet')

        os.chdir(_base_cwd)
        if test_mode:
            shutil.rmtree(answers['title'])

    def _flask_bp(self) -> None:
        logging.info(f'Using Flask Blueprint')

        answers = prompt(FLASK, style=STYLE)

        cwd = os.getcwd()
        app_cwd = os.path.join(cwd, 'app')
        os.makedirs(app_cwd, exist_ok=True)

        with open(os.path.join(cwd, '.env'), 'w') as f:
            f.write(f'SECRET_KEY = {uuid.uuid4().hex}\nDATABASE_URL = sqlite:///.db')
        with open(os.path.join(cwd, 'wsgi.py'), 'w') as f:
            f.write(BLUEPRINTS['flask']['wsgi'])

        if 'Database' in answers['options']:
            with open(os.path.join(app_cwd, '__init__.py'), 'w') as f:
                f.write(BLUEPRINTS['flask']['__init__']['db'])
            with open(os.path.join(app_cwd, 'routes.py'), 'w') as f:
                f.write(BLUEPRINTS['flask']['routes']['db'])
            with open(os.path.join(app_cwd, 'models.py'), 'w') as f:
                f.write(BLUEPRINTS['flask']['models'])
        else:
            with open(os.path.join(app_cwd, '__init__.py'), 'w') as f:
                f.write(BLUEPRINTS['flask']['__init__']['nodb'])
            with open(os.path.join(app_cwd, 'routes.py'), 'w') as f:
                f.write(BLUEPRINTS['flask']['routes']['nodb'])

        if 'Forms' in answers['options']:
            with open(os.path.join(app_cwd, 'forms.py'), 'w') as f:
                f.write(BLUEPRINTS['flask']['forms'])

        if 'Templates Folder' in answers['options']:
            os.makedirs(os.path.join(app_cwd, 'templates'), exist_ok=True)

        if 'Static Folder' in answers['options']:
            os.makedirs(os.path.join(app_cwd, 'static'), exist_ok=True)
            os.makedirs(os.path.join(app_cwd, 'static/css'), exist_ok=True)
            os.makedirs(os.path.join(app_cwd, 'static/img'), exist_ok=True)
            os.makedirs(os.path.join(app_cwd, 'static/js'), exist_ok=True)
