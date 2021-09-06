# ------------------------------------------------------------ Imports ----------------------------------------------------------- #

# System
from enum import Enum

# -------------------------------------------------------------------------------------------------------------------------------- #



# -------------------------------------------------------- class: FileKeys ------------------------------------------------------- #

class FileKey(Enum):
    COMMENT_LINE_IMPORTS    = '[COMMENT_LINE_IMPORTS]'
    COMMENT_LINE            = '[COMMENT_LINE]'
    COMMENT_LINE_CLASS_NAME = '[COMMENT_LINE_CLASS_NAME]'
    CLASS_NAME              = '[CLASS_NAME]'

    COMMENT_LINE_INIT               = '[COMMENT_LINE_INIT]'
    COMMENT_LINE_OVERRIDES          = '[COMMENT_LINE_OVERRIDES]'
    COMMENT_LINE_PUBLIC_PROPERTIES  = '[COMMENT_LINE_PUBLIC_PROPERTIES]'
    COMMENT_LINE_PUBLIC_METHODS     = '[COMMENT_LINE_PUBLIC_METHODS]'
    COMMENT_LINE_PRIVATE_PROPERTIES = '[COMMENT_LINE_PRIVATE_PROPERTIES]'
    COMMENT_LINE_PRIVATE_METHODS    = '[COMMENT_LINE_PRIVATE_METHODS]'
    TAB                             = '[TAB]'

    # install dependencies
    COMMANDS = '[COMMANDS]'

    # file
    COMMENT_LINE_PUBLIC_VARS          = '[COMMENT_LINE_PUBLIC_VARS]'
    COMMENT_LINE_FILE_PUBLIC_METHODS  = '[COMMENT_LINE_FILE_PUBLIC_METHODS]'
    COMMENT_LINE_PRIVATE_VARS         = '[COMMENT_LINE_PRIVATE_VARS]'
    COMMENT_LINE_FILE_PRIVATE_METHODS = '[COMMENT_LINE_FILE_PRIVATE_METHODS]'

    # flow
    COMMENT_LINE_METHODS = '[COMMENT_LINE_METHODS]'
    COMMENT_LINE_PATHS   = '[COMMENT_LINE_PATHS]'
    COMMENT_LINE_VARS    = '[COMMENT_LINE_VARS]'
    COMMENT_LINE_FLOW    = '[COMMENT_LINE_FLOW]'


    # license
    YEAR        = '[YEAR]'
    AUTHOR_NAME = '[AUTHOR_NAME]'

    # readme
    SHIELDS      = '[SHIELDS]'
    PACKAGE_NAME = '[PACKAGE_NAME]'
    DESCRIPTION  = '[DESCRIPTION]'
    DEPENDENCIES = '[DEPENDENCIES]'

    # json class
    INIT_JSON_VARS = '[INIT_JSON_VARS]'

    # setup.py
    AUTHOR             = '[AUTHOR]'
    GIT_URL            = '[GIT_URL]'
    PACKAGE_VERSION    = '[PACKAGE_VERSION]'
    SHORT_DESCRIPTION  = '[SHORT_DESCRIPTION]'
    PYTHON_CLASSIFIERS = '[PYTHON_CLASSIFIERS]'
    MIN_PYTHON_VERSION = '[MIN_PYTHON_VERSION]'


# -------------------------------------------------------------------------------------------------------------------------------- #