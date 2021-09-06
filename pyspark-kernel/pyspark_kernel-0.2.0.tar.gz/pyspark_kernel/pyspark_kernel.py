from __future__ import print_function

from metakernel import MetaKernel
import sys
from .pyspark_magic import PySparkMagic
from inspect import getmembers, isfunction

class PySparkKernel(MetaKernel):
    implementation = 'PySpark MetaKernel'
    implementation_version = '0.2.0'
    language = 'python'
    language_version = '0.1'
    banner = "PySpark Kernel - Inititlaizes PySpark on kernel initialization utilizing MetaKernel"
    language_info = {
        'mimetype': 'text/x-python',
        'name': 'python',
        'file_extension': '.py',
        'help_links': MetaKernel.help_links,
    }
    kernel_json = {
        "argv": [
            sys.executable, "-m", "pyspark_kernel", "-f", "{connection_file}"],
        "display_name": "PySpark (python)",
        "language": "python",
        "name": "pyspark_kernel"
    }

    def __init__(self, *args, **kwargs):
        super(PySparkKernel, self).__init__(*args, **kwargs)
        
        self._pysparkmagic = None

        # Register the %%scala and %%init_spark magics
        # The %%scala one is here only because this classes uses it
        # to interact with the ScalaInterpreter instance
        self.register_magics(PySparkMagic)
        self._pysparkmagic = self.line_magics['pyspark']

    def get_usage(self):
        return ("This is MetaKernel PySaprk. It implements a Python " +
                "interpreter.")

    def set_variable(self, name, value):
        """
        Set a variable in the kernel language.
        """
        python_magic = self.line_magics['python']
        python_magic.env[name] = value

    def get_variable(self, name):
        """
        Get a variable from the kernel language.
        """
        python_magic = self.line_magics['python']
        return python_magic.env.get(name, None)

    def do_execute_direct(self, code):
        self._pysparkmagic._initiliaze_pyspark()
        python_magic = self.line_magics['python']
        if not self._pysparkmagic.magic_called:
            return python_magic.eval(code.strip())

    def get_completions(self, info):
        python_magic = self.line_magics['python']
        return python_magic.get_completions(info)

    def get_kernel_help_on(self, info, level=0, none_on_fail=False):
        python_magic = self.line_magics['python']
        return python_magic.get_help_on(info, level, none_on_fail)


