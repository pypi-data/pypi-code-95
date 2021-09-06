# ------------------------------------------------------------ Imports ----------------------------------------------------------- #

# Local
from .texts.all_file_consts import AllFileConsts

# -------------------------------------------------------------------------------------------------------------------------------- #



# ------------------------------------------------------- class: Constants ------------------------------------------------------- #

class Constants:
    CONFIG_FILE_NAME                 = '.kcliutils.json'
    GITIGNORE_FILE_NAME              = '.gitignore'
    DEMO_FILE_NAME                   = 'demo.py'
    README_FILE_NAME                 = 'README.md'
    LICENSE_FILE_NAME                = 'LICENSE'
    SETUP_FILE_NAME                  = 'setup.py'
    INIT_PY_FILE_NAME                = '__init__.py'
    INSTALL_DEPENDENCIES_FILE_NAME   = 'install_dependencies.sh'
    REQUIREMENTS_FILE_NAME           = 'requirements.txt'
    DEFAULT_COMMIT_MESSAGE           = 'Update'
    DEFAULT_SPACES_PER_TAB           = 4
    DEFAULT_COMMENT_LINE_LENGTH      = 140
    PYTHON_VERSIONS                  = ['3.4', '3.5', '3.6', '3.7', '3.8', '3.9']
    ALLOWED_EXPENSIONS_TO_CLEAN      = ['.py', '.ts', '.js']
    IGNORED_PATH_COMPONENTS_TO_CLEAN = ['node_modules']
    SUPPORTED_FILE_CONSTS            = [e.value for e in AllFileConsts.all()]


# -------------------------------------------------------------------------------------------------------------------------------- #