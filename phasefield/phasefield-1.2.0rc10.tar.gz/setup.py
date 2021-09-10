import os, sys
from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext

builddir = os.path.abspath(os.getcwd())

def inVEnv():
    # if sys.real_prefix exists, this is a virtualenv set up with the virtualenv package
    if hasattr(sys, 'real_prefix'):
        return 1
    # if a virtualenv is set up with pyvenv, we check for equality of base_prefix and prefix
    if hasattr(sys, 'base_prefix'):
        return (sys.prefix != sys.base_prefix)
    # if none of the above conditions triggered, this is probably no virtualenv interpreter
    return 0

def get_install_prefix():
    # test if in virtual env
    if inVEnv():
        return sys.prefix
    # use system default
    return None

class BuildExt(build_ext):
    def build_extensions(self):
        path = get_install_prefix()
        if path is None:
            raise RuntimeError("Need to install 'phasefield' package in python virtual environment - exiting")
        addModules = 'bash ./addModules.sh ' + get_install_prefix()
        status = os.system(addModules)
        if status != 0: raise RuntimeError(status)
        self.extensions.pop(0) # empty extension was added to run `dunecontrol`
        for ext in self.extensions:
            ext.extra_compile_args += ['-std=c++17', '-fvisibility=hidden']
        build_ext.build_extensions(self)

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name="phasefield",
    version="1.2.0rc10",
    author="Matthew Collins, Andreas Dedner, and Bjoern Stinner",
    author_email="a.s.dedner@warwick.ac.uk",
    description="Interface problem solver based on the phase-field methodology",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.dune-project.org/dune-fem/phasefield",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent"],
    zip_safe = 0,
    package_data = {'': ['*.cc','tutorial/*.py','tutorial/data/*']},
    ext_modules=[Extension("", [])],
    cmdclass={'build_ext': BuildExt},
    install_requires=["dune-fem==2.8.0rc1","matplotlib"]
  )
