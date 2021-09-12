from typing import Callable, Any
from cp93pytools.methodtools import cached_property


class PosetException(Exception):
    message = 'Dummy exception for the poset class'

    def __init__(self, *hooks: Callable[[], Any], message=None, args=None):
        self.hooks = hooks
        if message is not None:
            self.message = message
        if args != None:
            self.args = args

    def __str__(self):  # When raised to the top
        for hook in self.hooks:
            hook()
        return repr(self)


# Not poset
class NotPosetException(PosetException):
    message = 'Given relation is not a poset'


class NotTransitiveException(NotPosetException):
    message = 'Given relation is not transitive'


class NotReflexiveException(NotPosetException):
    message = 'Given relation is not reflexive (i<=i)'


class NotAntisymmetricException(NotPosetException):
    message = ('Given relation is not antisymmetric '
               '(antisymmetry: i<=j and j<=i imply j=i)\n'
               'There is a cycle')


class NoBottomsException(NotPosetException):
    message = 'No bottom element found'


class NoTopsException(NotPosetException):
    message = 'No top element found'


# Not lattice
class NotLatticeException(PosetException):
    message = 'Given poset is not a lattice'


class NoLUBException(NotLatticeException):
    message = 'Given poset has pairs with no common upper bounds'


class NotUniqueLUBException(NotLatticeException):
    message = 'Given poset has pairs with non-unique minimal upper bounds'


class NotUniqueBottomException(NotLatticeException):
    message = 'Given poset has multiple bottom elements'


class NotUniqueTopException(NotLatticeException):
    message = 'Given poset has multiple top elements'


class NotCompleteException(PosetException):
    message = 'Given poset is not complete'


class NotDistributiveException(PosetException):
    message = 'Given lattice is not distributive'


class PosetExceptions:
    PosetException = PosetException
    NotPosetException = NotPosetException
    NotTransitiveException = NotTransitiveException
    NotReflexiveException = NotReflexiveException
    NotAntisymmetricException = NotAntisymmetricException
    NotLatticeException = NotLatticeException
    NoLUBException = NoLUBException
    NotUniqueLUBException = NotUniqueLUBException
    NotUniqueBottomException = NotUniqueBottomException
    NotUniqueTopException = NotUniqueTopException
    NotCompleteException = NotCompleteException
    NotDistributiveException = NotDistributiveException
    NoBottomsException = NoBottomsException
    NoTopsException = NoTopsException
