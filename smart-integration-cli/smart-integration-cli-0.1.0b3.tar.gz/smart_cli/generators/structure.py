import os
import sys
from typing import Optional

from .filemanager import FileGenerator
from .utils import get_random_string


class Structure(object):
    def __init__(self, project_name: str, struct_type: str):
        self.project_name = project_name
        self.struct_type = struct_type

    def get_lib_path(self):
        for path in sys.path:
            if 'site-packages' in path:
                return path

    def install_dependencies(self):
        dependencies = [
            'zappa>=0.50.0',
            'requests>=2.18.1',
            'validators',
            'pytz>=2018.4',
            'six==1.11.0',
            'boto',
            'boto3',
            'django>=2.2.7,<=3.0.5',
            'django-storages',
            'django-cors-headers',
            'cfn-flip==1.0.2',
            'eventmonitoring-client',
            'smart-integration-utils',
        ]
        with open('.req.txt', 'a') as f:
            for d in dependencies:
                f.write(d + '\n')
        os.system('pip install -r .req.txt')
        os.remove('.req.txt')

    def _generate_gitignore_file(self):
        lib_path = self.get_lib_path()
        templates_path = lib_path + '/smart_cli/templates'
        file_path = f'{templates_path}/gitignore.tpl'
        generator = FileGenerator(file_path, '.gitignore', {})
        generator.write_file()

    def init_django_app(self):
        os.system(f'django-admin startproject {self.project_name}')
        os.chdir(self.project_name)
        os.system('pip freeze | grep -v "pkg-resources" > requirements.txt')
        self._generate_gitignore_file()
        os.chdir('..')

    def _gen_file(self, templates_path: str, name: str, params: Optional[dict] = None):
        file_path = f'{templates_path}/{name}'
        if '__init__' in name:
            new_file_name = name.replace('.tpl', '').replace('py', '.py')
        elif 'gitignore' in name:
            return None
        else:
            new_file_name = (
                name.replace('base_', '')
                .replace('oauth_', '')
                .replace('basic_', '')
                .replace('.tpl', '')
                .replace('_', '.')
            )
        generator = FileGenerator(file_path, new_file_name, params)
        generator.write_file()

    def rewrite_basic_files(self, default: bool = True):
        os.chdir(self.project_name)
        os.chdir(self.project_name)
        lib_path = self.get_lib_path()
        templates_path = (
            lib_path + '/smart_cli/templates'
            if default
            else lib_path + '/smart_cli/templates/django_docker_files'
        )
        params = {
            'project_name': self.project_name,
            'secret_key': get_random_string(),
            'app_name': 'api',
        }
        if not default:
            params['app_name'] = 'core'
        for name in os.listdir(templates_path):
            if name.startswith('base_'):
                self._gen_file(templates_path, name, params)
        os.chdir('..')

    def _generate_app(
        self,
        folder: str,
        finish_folder: Optional[str] = None,
        template_path: Optional[str] = None,
        with_migrations: bool = True,
    ):
        os.mkdir(folder if not finish_folder else finish_folder)
        os.chdir(folder if not finish_folder else finish_folder)
        if with_migrations:
            os.mkdir('migrations')
            os.chdir('migrations')
            with open('__init__.py', 'w') as f:
                f.write('')
            os.chdir('..')
        lib_path = self.get_lib_path()
        if not template_path:
            templates_path = lib_path + f'/smart_cli/templates/{folder}/'
        else:
            templates_path = lib_path + f'{template_path}{folder}/'
        params = {'app_name': folder if not finish_folder else finish_folder}

        for name in os.listdir(templates_path):
            if self.struct_type == 'oauth':
                if 'basic' in name:
                    continue
                self._gen_file(templates_path, name, params)
            else:
                if 'oauth' in name:
                    continue
                self._gen_file(templates_path, name, params)
        os.chdir('..')

    def generate_api_apps_files(self):
        return self._generate_app('api')
