# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2017 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/


__authors__ = ["Jérôme Kieffer", "Thomas Vincent", "Júlia Garriga"]
__license__ = "MIT"
__date__ = "10/09/2020"

import io
import logging
import os
import sys

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("darfix.setup")

from setuptools import find_packages
try:
    from setuptools import Command
    logger.info("Use setuptools")
except ImportError:
    try:
        from numpy.distutils.core import Command
    except ImportError:
        from distutils.core import Command
    logger.info("Use distutils")

try:
    import sphinx
    import sphinx.util.console
    sphinx.util.console.color_terminal = lambda: False
    from sphinx.setup_command import BuildDoc
except ImportError:
    sphinx = None

with open("README.rst", "r") as fh:
    long_description = fh.read()

PROJECT = "darfix"


def get_version():
    """Returns current version number from version.py file"""
    dirname = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, dirname)
    import darfix.version
    sys.path = sys.path[1:]
    return darfix.version.strictversion


classifiers = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Environment :: X11 Applications :: Qt',
    'Intended Audience :: Education',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: POSIX',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
]


def get_readme():
    """Returns content of README.rst file"""
    dirname = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(dirname, "README.rst")
    with io.open(filename, "r", encoding="utf-8") as fp:
        long_description = fp.read()
    return long_description


# ############################# #
# numpy.distutils Configuration #
# ############################# #

def configuration(parent_package='', top_path=None):
    """Recursive construction of package info to be used in setup().

    See http://docs.scipy.org/doc/numpy/reference/distutils.html#numpy.distutils.misc_util.Configuration
    """
    try:
        from numpy.distutils.misc_util import Configuration
    except ImportError:
        raise ImportError(
            "To install this package, you must install numpy first\n"
            "(See https://pypi.python.org/pypi/numpy)")
    config = Configuration(None, parent_package, top_path)
    config.set_options(
        ignore_setup_xxx_py=True,
        assume_default_configuration=True,
        delegate_options_to_subpackages=True,
        quiet=True)
    config.add_subpackage(PROJECT)
    return config


# ################### #
# build_doc command   #
# ################### #

if sphinx is None:
    class SphinxExpectedCommand(Command):
        """Command to inform that sphinx is missing"""
        user_options = []

        def initialize_options(self):
            pass

        def finalize_options(self):
            pass

        def run(self):
            raise RuntimeError(
                'Sphinx is required to build or test the documentation.\n'
                'Please install Sphinx (http://www.sphinx-doc.org).')


class BuildMan(Command):
    """Command to build man pages"""
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def entry_points_iterator(self):
        """Iterate other entry points available on the project."""
        entry_points = self.distribution.entry_points
        console_scripts = entry_points.get('console_scripts', [])
        gui_scripts = entry_points.get('gui_scripts', [])
        scripts = []
        scripts.extend(console_scripts)
        scripts.extend(gui_scripts)
        for script in scripts:
            # Remove ending extra dependencies
            script = script.split("[")[0]
            elements = script.split("=")
            target_name = elements[0].strip()
            elements = elements[1].split(":")
            module_name = elements[0].strip()
            function_name = elements[1].strip()
            yield target_name, module_name, function_name

    def run_targeted_script(self, target_name, script_name, env, log_output=False):
        """Execute targeted script using --help and --version to help checking
        errors. help2man is not very helpful to do it for us.
        :return: True is both return code are equal to 0
        :rtype: bool
        """
        import subprocess

        if log_output:
            extra_args = {}
        else:
            try:
                # Python 3
                from subprocess import DEVNULL
            except ImportError:
                # Python 2
                import os
                DEVNULL = open(os.devnull, 'wb')
            extra_args = {'stdout': DEVNULL, 'stderr': DEVNULL}

        succeeded = True
        command_line = [sys.executable, script_name, "--help"]
        if log_output:
            logger.info("See the following execution of: %s", " ".join(command_line))
        p = subprocess.Popen(command_line, env=env, **extra_args)
        status = p.wait()
        if log_output:
            logger.info("Return code: %s", status)
        succeeded = succeeded and status == 0
        command_line = [sys.executable, script_name, "--version"]
        if log_output:
            logger.info("See the following execution of: %s", " ".join(command_line))
        p = subprocess.Popen(command_line, env=env, **extra_args)
        status = p.wait()
        if log_output:
            logger.info("Return code: %s", status)
        succeeded = succeeded and status == 0
        return succeeded

    def run(self):
        build = self.get_finalized_command('build')
        path = sys.path
        path.insert(0, os.path.abspath(build.build_lib))

        env = dict((str(k), str(v)) for k, v in os.environ.items())
        env["PYTHONPATH"] = os.pathsep.join(path)

        import subprocess

        status = subprocess.call(["mkdir", "-p", "build/man"])
        if status != 0:
            raise RuntimeError("Fail to create build/man directory")

        import tempfile
        import stat
        script_name = None

        entry_points = self.entry_points_iterator()
        for target_name, module_name, function_name in entry_points:
            logger.info("Build man for entry-point target '%s'" % target_name)

            # help2man expect a single executable file to extract the help
            # we create it, execute it, and delete it at the end
            py3 = sys.version_info >= (3, 0)
            try:
                # create a launcher using the right python interpreter
                script_fid, script_name = tempfile.mkstemp(prefix="%s_" % target_name, text=True)
                script = os.fdopen(script_fid, 'wt')
                script.write("#!%s\n" % sys.executable)
                script.write("import %s as app\n" % module_name)
                script.write("app.%s()\n" % function_name)
                script.close()
                # make it executable
                mode = os.stat(script_name).st_mode
                os.chmod(script_name, mode + stat.S_IEXEC)

                # execute help2man
                man_file = "build/man/%s.1" % target_name
                command_line = ["help2man", script_name, "-o", man_file]
                if not py3:
                    # Before Python 3.4, ArgParser --version was using
                    # stderr to print the version
                    command_line.append("--no-discard-stderr")
                    # Then we dont know if the documentation will contains
                    # durtty things
                    succeeded = self.run_targeted_script(target_name, script_name, env, False)
                    if not succeeded:
                        logger.info("Error while generating man file for target '%s'.",
                                    target_name)
                        self.run_targeted_script(target_name, script_name, env, True)
                        raise RuntimeError("Fail to generate '%s' man documentation" % target_name)

                p = subprocess.Popen(command_line, env=env)
                status = p.wait()
                if status != 0:
                    logger.info("Error while generating man file for target '%s'.", target_name)
                    self.run_targeted_script(target_name, script_name, env, True)
                raise RuntimeError(
                    "Fail to generate '%s' man documentation" % target_name)
            finally:
                # clean up the script
                if script_name is not None:
                    os.remove(script_name)


if sphinx is not None:
    class BuildDocCommand(BuildDoc):
        """Command to build documentation using sphinx.

        Project should have already be built.
        """

        def run(self):
            # make sure the python path is pointing to the newly built
            # code so that the documentation is built on this and not a
            # previously installed version

            build = self.get_finalized_command('build')
            sys.path.insert(0, os.path.abspath(build.build_lib))

            # Build the Users Guide in HTML and TeX format
            for builder in ['html', 'latex']:
                self.builder = builder
                self.builder_target_dir = os.path.join(self.build_dir, builder)
                self.mkpath(self.builder_target_dir)
                BuildDoc.run(self)
            sys.path.pop(0)
else:
    BuildDocCommand = SphinxExpectedCommand


# ################### #
# test_doc command    #
# ################### #

if sphinx is not None:
    class TestDocCommand(BuildDoc):
        """Command to test the documentation using sphynx doctest.

        http://www.sphinx-doc.org/en/1.4.8/ext/doctest.html
        """
        def run(self):
            # make sure the python path is pointing to the newly built
            # code so that the documentation is built on this and not a
            # previously installed version

            build = self.get_finalized_command('build')
            sys.path.insert(0, os.path.abspath(build.build_lib))

            # Build the Users Guide in HTML and TeX format
            for builder in ['doctest']:
                self.builder = builder
                self.builder_target_dir = os.path.join(self.build_dir, builder)
                self.mkpath(self.builder_target_dir)
                BuildDoc.run(self)
            sys.path.pop(0)

else:
    TestDocCommand = SphinxExpectedCommand


# ##### #
# setup #
# ##### #

NAMESPACE_PACKAGES = ["orangecontrib", "ppfaddon"]

PACKAGES = find_packages()


def get_project_configuration(dry_run):
    """Returns project arguments for setup"""
    install_requires = [
        # for most of the computation
        "numpy",
        # for the script launcher
        "setuptools",
        # for input/output operations
        "silx"
    ]

    full_requires = [
        'matplotlib>=1.2.0',
        # for image processing
        "opencv-python==4.1.2.30",
        "scikit-image>=0.17.1",
        "PyQt5",
        "orange3",
        "pypushflow==0.2.0b2",
        "tqdm"
    ]

    test_requires = [
        "pillow==7.0.0",
    ]

    extras_require = {
        'full': full_requires,
        'test': test_requires
    }

    setup_requires = ["setuptools", "numpy"]

    cmdclass = dict(
        build_doc=BuildDocCommand,
        test_doc=TestDocCommand,
        build_man=BuildMan
    )

    package_data = {
        # Resources files for darfix orange add-on
        'darfix.resources': [
            'gui/icons/*.png',
            'gui/icons/*.svg'
        ],
        'orangecontrib.darfix': [
            'widgets/icons/*.png',
            'widgets/icons/*.svg',
        ]
    }

    entry_points = {
        # Entry points that marks this package as an orange add-on. If set, addon will
        # be shown in the add-ons manager even if not published on PyPi.
        'orange3.addon': (
            'darfix-add-on=orangecontrib.darfix',
        ),
        # Entry point used to specify packages containing widgets.
        'orange.widgets': (
            # Syntax: category name = path.to.package.containing.widgets
            # Widget category specification can be seen in
            'darfix=orangecontrib.darfix.widgets',
        ),

        # Register widget help
        "orange.canvas.help": (
            'html-index=orangecontrib.darfix.widgets:WIDGET_HELP_PATH',
        ),
    }

    if dry_run:
        # DRY_RUN implies actions which do not require NumPy
        #
        # And they are required to succeed without Numpy for example when
        # pip is used to install tomwer when Numpy is not yet present in
        # the system.
        setup_kwargs = {}
    else:
        config = configuration()
        setup_kwargs = config.todict()
    setup_kwargs.update(name=PROJECT,
                        version=get_version(),
                        url="https://gitlab.com/XRD/darfix",
                        author="data analysis unit",
                        author_email="julia.garriga@esrf.fr",
                        classifiers=classifiers,
                        description="Computer vision software for the interpretation of diffraction images",
                        long_description=get_readme(),
                        namespace_packages=NAMESPACE_PACKAGES,
                        packages=PACKAGES,
                        install_requires=install_requires,
                        setup_requires=setup_requires,
                        extras_require=extras_require,
                        cmdclass=cmdclass,
                        package_data=package_data,
                        zip_safe=False,
                        entry_points=entry_points,
                        license='MIT License',
                        platforms='linux'
                        )
    return setup_kwargs


def setup_package():
    """Run setup(**kwargs)

    Depending on the command, it either runs the complete setup which depends on numpy,
    or a *dry run* setup with no dependency on numpy.
    """

    # Check if action requires build/install
    dry_run = len(sys.argv) == 1 or (len(sys.argv) >= 2 and (
        '--help' in sys.argv[1:]
        or sys.argv[1] in ('--help-commands', 'egg_info', '--version',
                           'clean', '--name')))

    if dry_run:
        # DRY_RUN implies actions which do not require dependancies, like NumPy
        try:
            from setuptools import setup
            logger.info("Use setuptools.setup")
        except ImportError:
            from distutils.core import setup
            logger.info("Use distutils.core.setup")
    else:
        try:
            from setuptools import setup
        except ImportError:
            from numpy.distutils.core import setup
            logger.info("Use numpydistutils.setup")

    setup_kwargs = get_project_configuration(dry_run)
    setup(**setup_kwargs)


DATA_FILES = [
    # Data files that will be installed outside site-packages folder
]


def include_documentation(local_dir, install_dir):
    global DATA_FILES
    if 'bdist_wheel' in sys.argv and not os.path.exists(local_dir):
        print("Directory '{}' does not exist. "
              "Please build documentation before running bdist_wheel."
              .format(os.path.abspath(local_dir)))
        sys.exit(0)

    doc_files = []
    for dirpath, dirs, files in os.walk(local_dir):
        doc_files.append((dirpath.replace(local_dir, install_dir),
                          [os.path.join(dirpath, f) for f in files]))
    DATA_FILES.extend(doc_files)


if __name__ == "__main__":
    include_documentation('build/sphinx/html', 'help/darfix')
    setup_package()
