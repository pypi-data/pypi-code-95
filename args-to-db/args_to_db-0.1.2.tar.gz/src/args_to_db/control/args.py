import warnings


def _is_list_of_str(obj):
    if obj == []:
        return True

    if not isinstance(obj, (tuple, list)):
        return False

    return all((isinstance(elem, str) for elem in obj))


class Command():
    def __init__(self, args, dependencies=None):

        if isinstance(args, str):
            args = [args]

        assert _is_list_of_str(args)
        self._args = args

        if dependencies is None:
            dependencies = []

        assert _is_list_of_str(dependencies)
        self._dependencies = dependencies

        if dependencies != []:
            warnings.warn("Dependencies are currently only placeholders.")

    def args(self):
        return self._args

    def dependencies(self):
        return self._dependencies

    def __add__(self, other):
        assert isinstance(other, Command)
        # how shoudl dependencies get 'added'?
        return Command([*self.args(), *other.args()])

    def __eq__(self, other) -> bool:
        assert isinstance(other, Command)

        args_eq = (self.args() == other.args())
        dependencies_eq = (self.dependencies() == other.dependencies())
        return args_eq and dependencies_eq

    def __repr__(self) -> str:
        return ' '.join(self._args)


class CommandList():
    def __init__(self, commands):
        assert isinstance(commands, (tuple, list))
        assert all((isinstance(cmd, Command) for cmd in commands))

        self._commands = commands

    def __add__(self, other):
        assert isinstance(other, CommandList)

        commands = [s + o for s in self.commands() for o in other.commands()]
        return CommandList(commands)

    def commands(self) -> list:
        return self._commands

    def __eq__(self, other) -> bool:
        assert isinstance(other, CommandList)

        return self._commands == other.commands()

    def __len__(self) -> int:
        return len(self._commands)

    def __repr__(self) -> str:
        return str(self._commands)


def arg(args):
    """Creates a single or multiple value argument object for command
       contruction.

    Args:
        options (str, list): Command or list of commands

    Returns:
        _Arg: 2D array of commands.
    """
    is_list = isinstance(args, list)
    is_str = isinstance(args, str)

    assert is_list or is_str, 'Passed argument must be a list or string.'
    if is_list:
        assert all(isinstance(option, str) for option in args), \
            'All argument options must be strings.'
    else:
        args = [args]

    return CommandList([Command(arg) for arg in args])


def flag(identifier, vary=True):
    """Creates a flag object for command construction.

    Args:
        identifier (str): string of the actual flag to be added to the command
        vary (bool, optional): Wether this flag is to be understood as an
            optional one. Defaults to True.

    Returns:
        _Arg: 2D array of commands.
    """
    assert isinstance(identifier, str), 'Flag identifier must be of type str.'
    assert isinstance(vary, bool), 'Vary argument takes a bool as parameter.'

    options = [Command([identifier])]
    if vary:
        options.insert(0, Command([]))

    return CommandList(options)


def option(identifier, values):
    """Creates a option object for command construction.

    Args:
        identifier (str): String of the option identifier.
        values (list): Possible values of the option.

    Returns:
        _Arg: 2D array of commands.
    """
    assert isinstance(identifier, str), 'Identifier must be of type str.'

    is_list = isinstance(values, list)
    is_str = isinstance(values, str)
    assert is_list or is_str, 'Values type must be either str or list.'
    if is_list:
        assert all(isinstance(option, str) for option in values), \
            'All possible values must be of type str.'

    if is_list and len(values) == 0:
        return CommandList([])

    return CommandList([Command([identifier])]) + \
        CommandList([Command(value) for value in values])
