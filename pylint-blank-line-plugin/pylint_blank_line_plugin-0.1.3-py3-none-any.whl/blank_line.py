from pylint_blank_line_plugin.checker import BlankLineChecker


def register(linter):
    linter.register_checker(BlankLineChecker(linter))
