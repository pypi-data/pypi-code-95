from .utils import get_gitignored


EXCLUDE_DOC = {'*.md', '*.doc', '*.docx', '*.txt', '*.pdf', }

EXCLUDE_CONFIG = {'*.cfg', '*.ini', '*.conf', }
EXCLUDE_YAML = {'*.yml', '*.yaml', }

EXCLUDE_BASH = {'*.sh', }
EXCLUDE_GIT = {'.git', '.gitignore', }
EXCLUDE_DOCKER = {'Dockerfile', '.dockerignore', }
EXCLUDE_VIRTUALENV = {'venv', 'virtualenv'}
EXCLUDE_DEVELOPMENT_TOOLS = {'.idea', }

EXCLUDE_IMAGES = {'*.png', '*.jpg', '*.jpeg', '*.bmp', '*.gif', }
EXCLUDE_AUDIO = {'*.png', '*.jpg', '*.jpeg', '*.bmp', '*.gif', }
EXCLUDE_VIDEO = {'*.mkv', '*.avi', }
EXCLUDE_MEDIA = EXCLUDE_AUDIO | EXCLUDE_IMAGES | EXCLUDE_VIDEO

EXCLUDE_PYCOMPILE = {'*.pyc', '__pycache__', }
EXCLUDE_SETUPTOOLS_FILES = {'build', 'dist', '*.egg-info', }
EXCLUDE_PYTHON_BUILD_FILES = EXCLUDE_PYCOMPILE | EXCLUDE_SETUPTOOLS_FILES

EXCLUDE_GITIGNORED = get_gitignored()

EXCLUDE_RECOMMENDED = EXCLUDE_DOC | EXCLUDE_GIT | EXCLUDE_DEVELOPMENT_TOOLS | EXCLUDE_VIRTUALENV | \
    EXCLUDE_MEDIA | EXCLUDE_PYTHON_BUILD_FILES | EXCLUDE_GITIGNORED
