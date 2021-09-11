from swimlane_platform.lib import Automation, LogFileOptional
from swimlane_platform.lib.args_config_questions import AnswerRequiredValidator, \
    PathExistsValidator, \
    VersionValidator, \
    DnsValidator

automation_questions = [
    {
        'type': 'list',
        'name': 'automation',
        'message': 'Do you want to save your configuration selections for future use, or load previously saved '
                   'selections?',
        'choices': [
            {
                'name': 'No thanks',
                'value': Automation.Normal
            },
            {
                'name': 'Save',
                'value': Automation.Save
            },
            {
                'name': 'Load',
                'value': Automation.Load
            }
        ]
    },
    {
        'type': 'input',
        'name': 'automation_file',
        'message': 'Specify the full path to your configuration file.',
        'when': lambda a: 'automation' in a and a['automation'] != Automation.Normal
    }
]

logging_questions = [
    {
        'type': 'list',
        'message': 'What logging level do you want?',
        'name': 'verbose',
        'default': 0,
        'choices': [
            {
                'name': 'Info',
                'value': 0
            },
            {
                'name': 'Verbose',
                'value': 1
            },
            {
                'name': 'Debug',
                'value': 2
            }
        ]
    },
    {
        'type': 'input',
        'name': 'log',
        'message': 'If you would like program output written to a file, specify the path to the log '
                   'file (leave your answer blank if no log file is needed).',
        'validate': LogFileOptional
    }
]

dev_question = [
    {
        'type': 'confirm',
        'name': 'dev',
        'message': 'hidden question for cli overwrite only',
        'default': False,
        'when': lambda a: False
    }
]

web_ssl_questions = [
    {
        'type': 'confirm',
        'message': 'Do you want to use a self-signed certificate for SSL web connections? '
                   'If not, you must provide your own certificates.',
        'name': 'web_ssl_self_signed',
        'default': True
    },
    {
        'type': 'input',
        'name': 'web_ssl_certificate',
        'message': 'Specify the full path to your .crt certificate.',
        'when': lambda a: not a['web_ssl_self_signed'],
        'validate': PathExistsValidator
    },
    {
        'type': 'input',
        'name': 'web_ssl_key',
        'message': 'Specify the full path to your .key certificate.',
        'when': lambda a: not a['web_ssl_self_signed'],
        'validate': PathExistsValidator
    }]

ssl_questions = [
    {
        'type': 'input',
        'name': 'ssl_country',
        'message': 'Specify country.',
        'default': u'US',
        'validate': lambda a: a and 3 > len(a) > 1
    },
    {
        'type': 'input',
        'name': 'ssl_state',
        'message': 'Specify state.',
        'default': u'CO',
        'validate': lambda a: a and 3 > len(a) > 1
    },
    {
        'type': 'input',
        'name': 'ssl_location',
        'message': 'Specify location/city.',
        'default': u'Louisville',
        'validate': AnswerRequiredValidator
    },
    {
        'type': 'input',
        'name': 'ssl_company',
        'message': 'Specify company.',
        'default': u'Swimlane Inc',
        'validate': AnswerRequiredValidator
    },
    {
        'type': 'input',
        'name': 'ssl_application',
        'message': 'Specify application name.',
        'default': u'local.swimlane.io',
        'validate': AnswerRequiredValidator
    },
    {
        'type': 'input',
        'name': 'ssl_dns',
        'message': 'Specify at least one DNS name to store in the Subject Alternative Name (comma-separated).',
        'default': u'*.swimlane.io',
        'validate': DnsValidator
    }
]

database_encryption_key_question = {
    'type': 'input',
    'name': 'db_encryption_key',
    'message': 'Enter database encryption key?',
    'validate': AnswerRequiredValidator
}

mongo_admin_password_question = {
    'type': 'password',
    'name': 'mongo_admin_password',
    'message': 'MongoDB Admin user password?',
    'validate': AnswerRequiredValidator
}

mongo_sw_password_question = {
    'type': 'password',
    'name': 'mongo_sw_password',
    'message': 'MongoDB Swimlane user password?',
    'validate': AnswerRequiredValidator
}

turbine_enable_questions = [
    {
        'type': 'confirm',
        'message': 'Do you want to enable Turbine as your tasks execution engine.',
        'name': 'turbine_enable',
        'default': False,
        'when': lambda a: False
    },
    {
        'type': 'input',
        'message': 'What version of Turbine images you want to use?',
        'name': 'turbine_image_version',
        'when': lambda a: a.get('turbine_enable') and a.get('dev'),
        'validate': VersionValidator
    }
]

offline_questions = [
    {
        'type': 'confirm',
        'name': 'installer_is_offline',
        'message': 'Are you installing offline?'
    },
    {
        'type': 'input',
        'name': 'extracted_files_folder',
        'message': 'Please specify the path to the folder containing the extracted installer files.',
        'when': lambda a: 'installer_is_offline' in a and a['installer_is_offline'],
        'default': u'.',
        'validate': PathExistsValidator
    }
]
