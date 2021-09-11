# pcrunner/exceteption.py
# vim: ai et ts=4 sw=4 sts=4 ft=python fileencoding=utf-8

'''
pcrunner.exceptions
-----------------------

All exceptions used in the PassiveCheckRunner code base are defined here.

'''


class PassiveCheckRunnerException(Exception):
    '''
    Base exception class. All PassiveCheckRunner specific exceptions should
    subclass this class.
    '''


class PostFailed(PassiveCheckRunnerException):
    '''
    Raised when an error occurs when posting results:
        * An error occurs while posting.
        * A non 200 HTTP return code.
    '''


class PostResultTooBig(PassiveCheckRunnerException):
    '''
    Raised when post result are bigger then max_post_size.
    '''
