from setuptools import setup

setup(
    include_package_data=True,
    entry_points={
        'console_scripts': ['quillbot = quillbot.cli:execute']
    },
)
