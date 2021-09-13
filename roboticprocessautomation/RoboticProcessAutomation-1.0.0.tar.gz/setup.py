from setuptools import setup, find_packages

setup(
    name='RoboticProcessAutomation',
    version='1.0.0',
    description='Robotic Process Automation Python Package',
    long_description='Some handy functions especially useful while building Robotic Process Automations with Python.',
    url='https://github.com/bartmazur90/RoboticProcessAutomation',
    author='Bartosz Mazur',
    author_email='bartmazur90@gmail.com',
    packages=find_packages(),
    install_requires=[
        'pillow',
        'opencv-python',
        'pyautogui',
        'pyscreeze'
    ],
    keywords=['python', 'RPA', 'Robotic', 'Process', 'Automation', 'Image Recognition'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent'
    ],
)