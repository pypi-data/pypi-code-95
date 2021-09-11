from pylint_exception_var_name_plugin.checker import ExceptionVarNameChecker


def register(linter):
    linter.register_checker(ExceptionVarNameChecker(linter))
