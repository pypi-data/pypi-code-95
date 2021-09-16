# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

try:
    from trytond.modules.nereid.tests.test_nereid import suite
except ImportError:
    from .test_nereid import suite


__all__ = ['suite']
