"""
Perform time simulation, using scheduled tasks to update current state
"""
# {# pkglts, src
# FYEO
# #}
# {# pkglts, version, after src
from . import version

__version__ = version.__version__
# #}

from datetime import timedelta

from .scheduler import Scheduler
from .task import Task, TaskRecord

one_day = timedelta(days=1)
one_hour = timedelta(hours=1)
