from distutils.command.install import install
from distutils import log
import json
import sys
import os
from setuptools import setup, find_packages

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except Exception:
    long_description = open('README.md').read()

kernel_json = {
 "argv":[
    "python","-m","pyspark_kernel", "-f", "{connection_file}"
    ],
 "language": "python",
 "display_name":"PySpark",
 "name": "pyspark_kernel"
}


class install_with_kernelspec(install):
    def run(self):
        install.run(self)
        from IPython.kernel.kernelspec import install_kernel_spec
        from IPython.utils.tempdir import TemporaryDirectory
        with TemporaryDirectory() as td:
            os.chmod(td, 0o755) # Starts off as 700, not user readable
            with open(os.path.join(td, 'kernel.json'), 'w') as f:
                json.dump(kernel_json, f, sort_keys=True)
            log.info('Installing kernel spec')
            try:
                install_kernel_spec(td, 'pyspark_kernel', user=self.user,
                                    replace=True)
            except:
                install_kernel_spec(td, 'pyspark_kernel', user=not self.user,
                                    replace=True)

svem_flag = '--single-version-externally-managed'
if svem_flag in sys.argv:
    # Die, setuptools, die.
    sys.argv.remove(svem_flag)


setup(name='pyspark_kernel',
      version='0.2.0',
      description='A PySpark kernel for Jupyter/IPython',
      long_description=long_description,
      url='https://gitlab.com/teia_engineering/pyspark_kernel',
      author='David Fernandez',
      author_email='teia.eng.14@gmail.com',
      install_requires=['IPython',  'findspark', 'metakernel', 'pandas', 'ipydatatable'],
      packages=list(find_packages()),
      cmdclass={'install': install_with_kernelspec},
      classifiers = [
          'Framework :: IPython',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 2',
          'Topic :: System :: Shells',
      ]
)