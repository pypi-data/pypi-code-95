import os

from .filemanager import FileGenerator
from .utils import get_random_string
from .structure import Structure


class BaseDockerAPPStructure(Structure):
    templates_path: str = ''

    def __init__(
        self, project_name: str, struct_type: str, registry: str, network: str
    ):
        self.project_name = project_name
        self.struct_type = struct_type
        self.registry = registry
        self.network = network
        self._tempalte_params = self.__generate_defualt_template_params()
        if not self.templates_path:
            raise ValueError('miss template path')

    def __generate_defualt_template_params(self) -> dict:
        params = {
            'project_name': self.project_name,
            'registry': self.registry,
            'network': self.network,
        }
        return params

    def generate_gitlab_ci_file(self):
        lib_path = self.get_lib_path()
        templates_path = lib_path + '/smart_cli/templates/gitlab-ci'
        file_path = f'{templates_path}/gitlab-ci.tpl'
        generator = FileGenerator(file_path, f'.gitlab-ci.yml', self._tempalte_params)
        generator.write_file()

    def generate_docker_compose_file(self):
        lib_path = self.get_lib_path()
        for filename in ('docker-compose.tpl', 'docker-stack.tpl'):
            templates_path = lib_path + self.templates_path
            file_path = f'{templates_path}/{filename}'
            generator = FileGenerator(
                file_path, f'{filename.replace(".tpl", ".yml")}', self._tempalte_params
            )
            generator.write_file()
        self.generate_ignore_files()

    def generate_ignore_files(self):
        lib_path = self.get_lib_path()
        for filename in ('gitignore.tpl', 'dockerignore.tpl'):
            templates_path = lib_path + self.templates_path
            file_path = f'{templates_path}/{filename}'
            generator = FileGenerator(
                file_path, f'.{filename.replace(".tpl", "")}', self._tempalte_params
            )
            generator.write_file()

    def generate_docker_folder(self):
        os.mkdir('docker')
        os.chdir('docker')
        self._genereate_dev_docker_files()
        self._genereate_prod_docker_files()
        os.chdir('..')

    def _genereate_dev_docker_files(self):
        os.mkdir('local')
        os.chdir('local')
        os.mkdir('python')
        os.chdir('python')
        self.__gen_file_by_list(['Dockerfile_dev.tpl', 'entrypoint.sh.tpl'])
        os.chdir('..')
        os.chdir('..')

    def _genereate_prod_docker_files(self):
        os.mkdir('prod')
        os.chdir('prod')
        os.mkdir('python')
        os.chdir('python')
        self.__gen_file_by_list(['Dockerfile_prod.tpl', 'entrypoint_prod.sh.tpl'])
        os.chdir('..')
        os.chdir('..')

    def __gen_file_by_list(self, list_of_file_names: list):
        lib_path = self.get_lib_path()
        templates_path = lib_path + self.templates_path + '/docker'
        for filename in list_of_file_names:
            file_path = f'{templates_path}/{filename}'
            new_file_name = (
                filename.replace("_prod.tpl", "")
                .replace("_dev.tpl", "")
                .replace(".tpl", "")
                .replace("_nginx", "")
                .replace("_prod", "")
            )
            generator = FileGenerator(file_path, new_file_name, self._tempalte_params)
            generator.write_file()


class DjangoDockerAPPStructure(BaseDockerAPPStructure):
    templates_path: str = '/smart_cli/templates/django_docker_files'

    def install_dependencies(self):
        dependencies = [
            'asgiref==3.2.7',
            'boto==2.49.0',
            'boto3==1.7.54',
            'botocore==1.10.84',
            'config-field',
            'Click==7.0',
            'django-cors-headers',
            'django-storages',
            'drf-dynamicfieldserializer',
            'Django==3.0.4',
            'pytz==2019.3',
            'sqlparse==0.3.1',
            'psycopg2-binary==2.8.4',
            'smart-integration-utils',
            'Jinja2',
            'celery==4.4.2',
            'requests',
            'validators',
        ]
        with open('.req.txt', 'a') as f:
            for d in dependencies:
                f.write(d + '\n')
        os.system('pip install -r .req.txt')
        os.remove('.req.txt')

    def generate_requirements_files(self):
        os.mkdir('requirements')
        os.chdir('requirements')

        dependencies = [
            'asgiref==3.2.7',
            'boto==2.49.0',
            'boto3==1.7.54',
            'botocore==1.10.84',
            'config-field',
            'Click==7.0',
            'django-cors-headers',
            'django-storages',
            'drf-dynamicfieldserializer',
            'Django==3.0.4',
            'pytz==2019.3',
            'sqlparse==0.3.1',
            'psycopg2-binary==2.8.4',
            'smart-integration-utils',
            'Jinja2',
            'celery==4.4.2',
            'requests',
            'validators',
        ]

        with open('requirements.txt', 'a') as f:
            for d in dependencies:
                f.write(d + '\n')

        local_dep = [
            '-r requirements.txt',
            'django-debug-toolbar',
        ]
        with open('local_requirements.txt', 'a') as f:
            for d in local_dep:
                f.write(d + '\n')

        prod_dep = [
            '-r requirements.txt',
            'gunicorn',
        ]
        with open('prod_requirements.txt', 'a') as f:
            for d in prod_dep:
                f.write(d + '\n')
        os.chdir('..')

    def generate_api_apps_files(self):
        return self._generate_app('api', 'core')

    def generate_settings_folder(self):
        os.mkdir('settings')
        os.chdir('settings')
        with open('__init__.py', 'w') as f:
            f.write('')
        lib_path = self.get_lib_path()
        templates_path = lib_path + self.templates_path + '/settings'
        params = {**self._tempalte_params, 'secret_key': get_random_string()}
        for name in os.listdir(templates_path):
            if name.endswith('.tpl'):
                self._gen_file(templates_path, name, params)
        os.chdir('..')

    def init_django_app(self):
        os.system(f'django-admin startproject {self.project_name}')

    def _rewrite_manage_py_file(self):
        lib_path = self.get_lib_path()
        templates_path = lib_path + self.templates_path
        self._gen_file(templates_path, 'manage.py.tpl', self._tempalte_params)

    def rewrite_basic_files(self, default: bool = True):
        super().rewrite_basic_files(False)
        self._rewrite_manage_py_file()
        os.chdir(self.project_name)
        self._rewrite_init_file_for_celery()
        os.system('rm settings.py')
        self.generate_settings_folder()
        os.chdir('..')

    def _rewrite_init_file_for_celery(self):
        lib_path = self.get_lib_path()
        template_path = lib_path + self.templates_path + '/celery_init.tpl'
        generator = FileGenerator(template_path, '__init__.py', self._tempalte_params)
        generator.write_file()


class FastAPIDockerAPPStructure(BaseDockerAPPStructure):
    templates_path: str = '/smart_cli/templates/fastapi_docker_files'
    dependencies: list = [
        'asgiref==3.2.7',
        'starlette==0.13.6',
        'typed-ast==1.4.1',
        'typing-extensions==3.7.4.3',
        'urllib3==1.25.10',
        'uvicorn==0.11.8',
        'uvloop==0.14.0',
        'smart-manage-crypt',
        'celery==4.4.2',
        'fastapi==0.61.1',
        'h11==0.9.0',
        'httptools==0.1.1',
        'aiohttp==3.6.2',
        'async-timeout==3.0.1',
        'cryptography==2.9.2',
        'bcrypt==3.2.0',
        'passlib==1.7.2',
        '',
    ]

    def init_app(self):
        os.mkdir('src')
        os.chdir('src')
        os.mkdir('app')
        os.chdir('app')

    def generate_requirements_files(self):
        os.mkdir('requirements')
        os.chdir('requirements')

        with open('requirements.txt', 'a') as f:
            for d in self.dependencies:
                f.write(d + '\n')

        local_dep = [
            '-r requirements.txt',
            'mypy==0.782',
            'mypy-extensions==0.4.3',
        ]
        with open('local_requirements.txt', 'a') as f:
            for d in local_dep:
                f.write(d + '\n')

        prod_dep = [
            '-r requirements.txt',
            'gunicorn',
        ]
        with open('prod_requirements.txt', 'a') as f:
            for d in prod_dep:
                f.write(d + '\n')
        os.chdir('..')

    def install_dependencies(self):
        with open('.req.txt', 'a') as f:
            for d in self.dependencies:
                f.write(d + '\n')
        os.system('pip install -r .req.txt')
        os.remove('.req.txt')

    def write_main_files(self):
        lib_path = self.get_lib_path()
        templates_path = lib_path + '/smart_cli/templates/fastapi_docker_files'
        params = {
            'project_name': self.project_name,
            'secret_key': get_random_string(),
        }
        for name in os.listdir(templates_path):
            if name.startswith('base_'):
                self._gen_file(templates_path, name, params)
        # os.chdir('..')

    def generate_core_files(self):
        return self._generate_app(
            'core',
            template_path=f'/smart_cli/templates/fastapi_docker_files/',
            with_migrations=False,
        )

    def generate_config_files(self):
        return self._generate_app(
            'config',
            template_path=f'/smart_cli/templates/fastapi_docker_files/',
            with_migrations=False,
        )

