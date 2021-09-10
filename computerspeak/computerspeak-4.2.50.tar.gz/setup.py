from setuptools import setup

setup(name='computerspeak',
    summary='This module makes th estring written in it speakaloud',
    version='4.2.50',
    author='Pratyush Jha',
    author_email='pratyush.jha299@gmail.com',
    install_requires='pyttsx3',
    description='This Module Helps A User To Use Computer Audio To Make The Computer Speak AnyThing You Want',
    long_description = '''First Of all to install this module copy the line above and paste it in a powershell window
This project requires the installation of pyttsx3, so to install that type
pip install pyttsx3
in powershell window


Now to use this, you will need to import this module
import speak
now as we have imported the module, we need to use it, so for using it type 
speak.speaker('The text you want to make the computer speak')

To Change The Voice Type "speak.change(0 or 1)"
0 for male 1 for female

Pls enjoy using this module 
Author = "Pratyush Jha"''',
    license="License.txt",
    packages=['speak']
)
