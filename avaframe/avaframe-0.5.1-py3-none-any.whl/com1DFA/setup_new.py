from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import numpy


from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

# # Compiler directives documentation
# # https://github.com/cython/cython/wiki/enhancements-compilerdirectives

# ext_modules = [Extension("DFAfunctionsCython",
#                          ["avaframe/com1DFA/DFAfunctionsCython.pyx"])]

# # This is the important part. By setting this compiler directive, cython will
# # embed signature information in docstrings. Sphinx then knows how to extract
# # and use those signatures.
# for e in ext_modules:
#     e.cython_directives = {"embedsignature": True,'language_level': "3" }


# setup(
#     name='DFAFunctions',
#     cmdclass={'build_ext': build_ext},
#     ext_modules=ext_modules
# )





setup(
    ext_modules=cythonize("avaframe/com1DFA/DFAfunctionsCython.pyx",
                          compiler_directives={'linetrace': True},
                          language_level=3),
    include_dirs=[numpy.get_include(),'.']
)
