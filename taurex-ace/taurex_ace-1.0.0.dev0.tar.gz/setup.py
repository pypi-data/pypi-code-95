import setuptools
from setuptools import find_packages
from numpy.distutils.core import setup
from numpy.distutils.core import Extension
from numpy.distutils import log
from numpy.distutils.command.build_ext import build_ext
import os

plugin_name = 'taurex_ace'


packages = find_packages(exclude=('tests', 'doc'))
provides = [plugin_name, ]


requires = []
FORCE_COMPILER = os.environ.get('FORCE_COMPILER', None)
EXTRA_LINK_FLAGS = os.environ.get('EXTRA_LINK_FLAGS', None)

install_requires = []

install_requires = ['numpy',
                    'taurex']



def build_fortran(subpackage,package_name, fortran_sources, extra_compile_args=None, extra_link_args=None):
    ext = Extension(name='.'.join((plugin_name,subpackage,package_name)),
                    extra_compile_args=extra_compile_args,
                    extra_link_args=extra_link_args,
                    extra_f90_compile_args=extra_compile_args,
                    extra_f77_compile_args=extra_compile_args,
                    sources=fortran_sources)

    return ext

def build_libs():
    import platform
    sources = ['taurex_ace/external/ace.pyf',
    'src/ACE/Md_Types_Numeriques.f90',
                'src/ACE/Md_Constantes.f90',
                'src/ACE/Md_numerical_recipes.f90',
                'src/ACE/Md_Utilitaires.f90','src/ACE/Md_ACE.f90']

    compile_args=['-fdefault-real-8', '-fdefault-double-8','-O3']
    link_args=[]
    sysname = platform.system()
    if sysname == "Darwin":
        compile_args.append("-mmacosx-version-min=10.9")
        link_args+= ["-mmacosx-version-min=10.9"]
    if EXTRA_LINK_FLAGS:
        link_args.append(EXTRA_LINK_FLAGS)

    return build_fortran('external', 'ace', sources,extra_compile_args=compile_args, 
                         extra_link_args=link_args)



class _custom_buildext(build_ext):

    def run(self):
        self.compiler = FORCE_COMPILER
        super().run()



extensions = [build_libs(),]




entry_points = {'taurex.plugins': 'ace = taurex_ace'}

version = '1.0.0-dev0'

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='taurex_ace',
      author='Ahmed Faris Al-Refaie',
      author_email='ahmed.al-refaie.12@ucl.ac.uk',
      license="BSD",
      description='ACE equilibrium chemical scheme wrapper built on TauREx',
      packages=packages,
      include_package_data=True,
      entry_points=entry_points,
      version=version,
      keywords=['exoplanet',
                'chemistry'
                'taurex',
                'plugin',
                'taurex3',
                'atmosphere',
                'atmospheric'],
      provides=provides,
      requires=requires,
      long_description=long_description,
      long_description_content_type='text/markdown',
      install_requires=install_requires,
      ext_modules=extensions,
      cmdclass={'build_ext': _custom_buildext},
      package_data={'taurex_ace' : ['external/Data/**']},
      )