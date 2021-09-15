#
# Utilitary functions
#
from functools import reduce

__all__ = ['rgetattr', 'get_summary']


def rgetattr(obj, attr, *args):
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)
    return reduce(_getattr, [obj] + attr.split('.'))


def get_summary(docstring, indent='        '):
    if docstring is None:
        return ''

    summary = docstring.split('\n\n')[0]
    summary = f'\n{indent}'.join(s.lstrip() for s in summary.splitlines())

    return summary
