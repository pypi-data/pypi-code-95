"""
Service Common Exceptions
"""


class BaseServiceException(Exception):
    """Base Service Exception --- all service exception base class"""
    msg: str = 'base service exception'
    status: int = 400

    def __init__(self, msg: str = "", status: int = 400):

        if msg:
            self.msg = msg

        if status:
            self.status = status

    def __str__(self):
        return self.msg

    def __repr__(self) -> str:
        return self.msg
        

class ServiceErrorException(BaseServiceException):
    """Service Error Exception"""

    msg = 'service error exception'


class ServiceException(BaseServiceException):
    """Service Exception"""

    msg = 'service exception'


class ServiceConfigException(ServiceException):
    """Service Config Exception"""

    msg = 'service config exception'


class ValidationException(ServiceException):
    """Validation Exception"""

    msg = 'validation failed'


class ParameterException(ServiceException):
    """Parameter Exception"""

    msg = 'invalid parameter'


class UniqueException(ServiceException):
    """Unique Exception"""
    msg = '对象已存在，无法创建'
    status = 400


class MultiObjectReturnException(ServiceException):
    """Multi Object Return Exception"""
    msg = '违反唯一条件，返回多个对象'
    status = 500


class UniqueTogetherException(UniqueException):
    """Unique Together Exception"""
    pass


class ObjectAlreadyExists(ServiceException):
    """Object Already Exists"""
    msg = '对象已存在'
    status = 400


class PKMissing(ServiceException):
    """PK missing"""
    msg = '主键信息缺失'
    status = 400


class ObjectDoesNotExist(ServiceException):
    """Object not exist"""

    msg = '对象不存在'
    status = 400


class NotFound(ServiceException):
    """Not found"""

    msg = '未找到对象'
    status = 400


class DBException(ServiceException):
    """DB Exception"""

    msg = "database error"
    status = 500


class InvalidConfigError(ServiceErrorException):
    """Invalid Config"""

    msg = "invalid config"
    status = 500
    