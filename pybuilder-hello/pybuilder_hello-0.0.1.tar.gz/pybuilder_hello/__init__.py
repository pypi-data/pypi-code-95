from __future__ import print_function
from pybuilder.core import task, init, use_plugin

use_plugin("python.core")

from pybuilder.core import task

@task
def hello():
    print("hello")
