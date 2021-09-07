# DO NOT EDIT!!! built with `python _building/build_setup.py`
import setuptools
setuptools.setup(
    name="k3modutil",
    packages=["k3modutil"],
    version="0.1.0",
    license='MIT',
    description='Submodule Utilities.',
    long_description="# k3modutil\n\n[![Action-CI](https://github.com/pykit3/k3modutil/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3modutil/actions/workflows/python-package.yml)\n[![Build Status](https://travis-ci.com/pykit3/k3modutil.svg?branch=master)](https://travis-ci.com/pykit3/k3modutil)\n[![Documentation Status](https://readthedocs.org/projects/k3modutil/badge/?version=stable)](https://k3modutil.readthedocs.io/en/stable/?badge=stable)\n[![Package](https://img.shields.io/pypi/pyversions/k3modutil)](https://pypi.org/project/k3modutil)\n\nSubmodule Utilities.\n\nk3modutil is a component of [pykit3] project: a python3 toolkit set.\n\n\nSubmodule Utilities.\n\n\n\n\n# Install\n\n```\npip install k3modutil\n```\n\n# Synopsis\n\n```python\n\nimport k3modutil\nimport pykit\n\nk3modutil.submodules(pykit)\n# {\n#    'modutil': <module> pykit.modutil,\n#    ... ...\n# }\n\nk3modutil.submodule_tree(pykit)\n# {\n#    'modutil': {'module': <module> pykit.modutil,\n#                'children': {\n#                            'modutil': {\n#                                    'module': <module> pykit.modutil.modutil,\n#                                    'children': None,\n#                                    },\n#                            'test': {\n#                                    'module': <module> pykit.modutil.test,\n#                                    'children': {\n#                                        'test_modutil': {\n#                                            'module': <module> pykit.modutil.test.test_modutil,\n#                                            'children': None,\n#                                        },\n#                                    },\n#                            }\n#                },\n#               }\n#    ... ...\n# }\n\nk3modutil.submodule_leaf_tree(pykit)\n# {\n#    'modutil': {\n#                'modutil': <module> pykit.modutil.modutil,\n#                'test': {'test_modutil': <module> pykit.modutil.test.test_modutil},\n#                }\n#    ... ...\n# }\n\n```\n\n#   Author\n\nZhang Yanpo (张炎泼) <drdr.xp@gmail.com>\n\n#   Copyright and License\n\nThe MIT License (MIT)\n\nCopyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>\n\n\n[pykit3]: https://github.com/pykit3",
    long_description_content_type="text/markdown",
    author='Zhang Yanpo',
    author_email='drdr.xp@gmail.com',
    url='https://github.com/pykit3/k3modutil',
    keywords=['python', 'modutils'],
    python_requires='>=3.0',

    install_requires=['k3ut>=0.1.15,<0.2'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
    ] + ['Programming Language :: Python :: 3'],
)
