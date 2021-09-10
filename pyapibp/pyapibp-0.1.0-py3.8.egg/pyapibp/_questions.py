from . import __supported__
from ._validators import *

FOLDER = [
    {
        'type': 'confirm',
        'name': 'existing',
        'message': 'Do you have an existing project folder?',
        'default': False
    },
]

GENERAL = [
    {
        'type': 'input',
        'name': 'title',
        'message': 'Please enter the project name:',
        'validate': TitleValidator
    },
    {
        'type': 'list',
        'name': 'framework',
        'message': 'Choose the framework:',
        'choices': __supported__,
        'filter': lambda val: val.lower()
    },
]

FLASK = [
    {
        'type': 'checkbox',
        'name': 'options',
        'message': 'Blueprint options',
        'choices': [
            {
                'name': 'Database',
                'checked': True
            },
            {
                'name': 'Forms',
                'checked': False
            },
            {
                'name': 'Templates Folder',
                'checked': False
            },
            {
                'name': 'Static Folder',
                'checked': False
            },
        ],
    },
]
