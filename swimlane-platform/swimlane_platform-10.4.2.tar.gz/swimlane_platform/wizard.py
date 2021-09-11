from swimlane_platform import install
from swimlane_platform.lib import Configuration, Actions, BaseWithLog, ExpectedException, \
    automation_questions, logging_questions, dev_question
from swimlane_platform import upgrade
from swimlane_platform.backup import backup
from swimlane_platform.backup import restore


class SwimlaneWizard(BaseWithLog):

    def __init__(self, config):
        # type: (Configuration) -> None
        super(SwimlaneWizard, self).__init__(config)

    # noinspection PyBroadException
    def run(self):
        command = self.config.args.command
        try:
            if command == Actions.Install:
                install.run(self.config)
            elif command == Actions.Upgrade:
                upgrade.run(self.config)
            elif command == Actions.Backup:
                backup.run(self.config)
            elif command == Actions.Restore:
                restore.run(self.config)
        except ExpectedException as e:
            self.logger.error(e.message)
        except Exception:
            self.logger.exception("Unexpected error.")


def run():
    auto_config = Configuration()
    auto_config.collect(automation_questions)
    config = Configuration(auto_config.args.automation, auto_config.args.automation_file)
    questions = [
        {
            'type': 'list',
            'name': 'command',
            'message': 'What action do you want to perform?',
            'choices': [
                {
                    'name': 'Install:   Install Swimlane.',
                    'value': Actions.Install
                },
                {
                    'name': 'Upgrade:   Upgrade to a newer version of Swimlane.',
                    'value': Actions.Upgrade
                },
                {
                    'name': 'Backup:    Create a backup of Swimlane data.',
                    'value': Actions.Backup
                },
                {
                    'name': 'Restore:   Restore Swimlane data from backup.',
                    'value': Actions.Restore
                }
            ]
        }
    ]
    questions.extend(dev_question)
    questions.extend(logging_questions)
    config.collect(questions)
    SwimlaneWizard(config).run()
