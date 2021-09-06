from enum_extend import AutoEnum


class ExAutoEnum(AutoEnum):
    '''
    This class inherits from :doc:`../class/AutoEnum` and is a just an example
    '''

    EX_ONE = 'This is a simple example of enum doc string'
    EX_TWO = '''
    Represents **TWO**.

        This is a multi-line `docstring <https://www.python.org/dev/peps/pep-0257/>`_

        Are there any questions?
    '''
    EX_THREE = '''
    .. include:: ../inc/ex/inc_ex.rst
    '''
    EX_FOUR = '''
    .. tip::
        This equals 4
    '''
    EX_FIVE = () # no doc string
    EX_TEN = (10, 'This value was set 10')