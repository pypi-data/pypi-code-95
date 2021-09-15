from clicasso import CommandParser

from apparatus.commands import COMMANDS
from apparatus.config import read_config


def main():
    parser = CommandParser.from_commands(*COMMANDS)
    command, remainder = parser.parse_known_args()
    config = read_config()
    command.run(config, remainder)


if __name__ == "__main__":
    main()
