# ------------------------------------------------------------ Imports ----------------------------------------------------------- #

# System
from enum import Enum

# -------------------------------------------------------------------------------------------------------------------------------- #



# -------------------------------------------------------- enum: FileValue ------------------------------------------------------- #

class FileValue(Enum):
    COMMENT_LINE_IMPORTS    = 'Imports'
    COMMENT_LINE_CLASS_NAME = 'class: {}'
    COMMENT_LINE_ENUM_NAME  = 'enum: {}'

    COMMENT_LINE_INIT               = 'Init'
    COMMENT_LINE_OVERRIDES          = 'Overrides'
    COMMENT_LINE_PUBLIC_PROPERTIES  = 'Public properties'
    COMMENT_LINE_PUBLIC_METHODS     = 'Public methods'
    COMMENT_LINE_PRIVATE_PROPERTIES = 'Private properties'
    COMMENT_LINE_PRIVATE_METHODS    = 'Private methods'

    # file
    COMMENT_LINE_PUBLIC_VARS  = 'Public vars'
    COMMENT_LINE_PRIVATE_VARS = 'Private vars'

    # flow
    COMMENT_LINE_METHODS = 'Methods'
    COMMENT_LINE_PATHS   = 'Paths'
    COMMENT_LINE_VARS    = 'Vars'
    COMMENT_LINE_FLOW    = 'Flow'


# -------------------------------------------------------------------------------------------------------------------------------- #