import sys

from aws_hcs_cli import commands


class TestClickParsesCommandLineArguments:

    def test_parses_help_argument(self):
        # when executes aws-hcs-cli --help
        sys.argv = ['aws-hcs-cli', '--help']
        try:
            commands.cli()
        except SystemExit as e:
            # displays help description
            assert e.code == 0
