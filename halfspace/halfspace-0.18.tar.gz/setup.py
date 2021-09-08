from setuptools import setup
from glob import glob

setup(
    name="halfspace",
    version="0.18",
    author="Andreas Sogaard",
    author_email="as@halfspace.io",
    description=("Core Halfspace python library"),
    keywords="halfspace",
    include_package_data=True,
    url="https://halfspace.ai/",
    packages=['halfspace'],
    # data_files=[
    #     ('images', glob('images/*.png')),
    #     ('fonts/inter', glob('fonts/inter/*.ttf')),
    #     ('fonts/playfair', glob('fonts/playfair/*.ttf'))
    # ],
    install_requires=[
        'matplotlib',
        'seaborn'
    ]
)
