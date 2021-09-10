from setuptools import setup, find_packages
from setuptools.command.install_scripts import install_scripts
from contextlib import suppress
from pathlib import Path
import os
import sys

pkg_name = "MLatom"
mlatom_script = 'mlatom'
site_pkg = ''
def modify_mlatom_script(script_path: str):
    global site_pkg
    for path in sys.path:
        with suppress(BaseException):
            for path_dir in os.listdir(path):
                if pkg_name in path_dir:
                    site_pkg = path
                    print(site_pkg)
    MLatom_py_file = os.path.join(site_pkg, pkg_name, 'MLatom.py')
    content = f"""#!/bin/bash
    export mlatom='{MLatom_py_file}'
    $mlatom "$@"
    """
    with open(script_path, 'w') as f:
        f.write(content)

def chmod_py(path):
    for py_file in Path(path).glob('*.py'):
        py_file.chmod(0o755)

class InstallScripts(install_scripts):
    def run(self):
        install_scripts.run(self)

        # Rename some script files
        for script in self.get_outputs():
            if script.endswith('mlatom'):
                modify_mlatom_script(script)

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()

setup(
    name = pkg_name,
    version = "2.0.2",
    author = "Pavlo O. Dral",
    author_email = "admin@mlatom.com",
    license = 'CC BY-NC-ND 4.0',  # https://creativecommons.org/licenses/by-nc-nd/4.0/
    description = "A Package for Atomistic Simulations with Machine Learning",
    long_description = README,
    long_description_content_type = 'text/markdown',
    url = "http://mlatom.com",
    python_requires='>=3.7',
    packages = find_packages('src'),
    package_dir = {'' : 'src'},
    scripts = ['mlatom', 'MLatomF'],
    package_data = {"": ['MLatomF', '*.json', 'cs.so']},
    classifiers = [
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Fortran",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Environment :: Console",
    ],
    install_requires = ['numpy', 'matplotlib'],
    # entry_points = {
    #     'console_scripts' : ['mlatom=MLatom.MLatom:MLatomMainCls']
    # }
    # cmdclass = {
    #     "install_scripts": InstallScripts
    # }
)

# bin_path = os.path.dirname(sys.executable)
# modify_mlatom_script(os.path.join(bin_path, mlatom_script))
# chmod_py(os.path.join(site_pkg, pkg_name))
