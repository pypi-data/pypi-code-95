from setuptools import setup, find_packages
from os.path import join, dirname

__PACKAGE__='weboa'
__DESCRIPTION__='weboa is a cli tool to create templates for websites and preprocessors'
__VERSION__="0.5.7"

setup(
    name=__PACKAGE__,
    version=__VERSION__,
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "": ["*"],
        "weboa_res":["weboa_res/*"]
    },
    description=__DESCRIPTION__,
    long_description=open(join(dirname(__file__), 'README.rst')).read(),
    author="lonagi",
    install_requires=["pillow","ply","six","lesscpy","libsass","coverage","coverage-enable-subprocess","pre-commit","pytest","werkzeug>=0.9","requests"],
    author_email='lonagi22@gmail.com',
    url="https://github.com/lonagi/weboa",
    entry_points = {
              'console_scripts': [
                  'weboa = weboa.run:runcli',
              ],
          },
)
