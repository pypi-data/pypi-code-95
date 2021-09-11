from .teallevel import TealLevel
from .tealprintbuffer import TealPrintBuffer


class TealPrint:
    _buffer = TealPrintBuffer()

    @staticmethod
    def error(
        message: str,
        push_indent: bool = False,
        exit: bool = False,
        print_exception: bool = False,
        print_report_this: bool = False,
    ):
        """Recommendation: Only use this when an error occurs and you have to exit the program
           Prints an error message in red, can quit and print an exception.
           Also prints a "Please report this and paste the above message"

        Args:
            message (str): The message to print
            push_indent (bool): If messages after this should be indented by one level. Call pop_indent() to unindent
            exit (bool): If the program should exit after printing the error
            print_exception (bool): Set to true to print an exception
            print_report_this (bool): Set to true to add an "Please report this..." message at the end
        """
        TealPrint._buffer.error(message, push_indent, exit, print_exception, print_report_this)
        TealPrint._buffer.flush()

    @staticmethod
    def warning(message: str, push_indent: bool = False, exit: bool = False):
        """Prints an orange warning message message

        Args:
            message (str): The message to print
            push_indent (bool): If messages after this should be indented by one level. Call pop_indent() to unindent
            exit (bool): If the program should exit after printing the warning
        """
        TealPrint._buffer.warning(message, push_indent, exit)
        TealPrint._buffer.flush()

    @staticmethod
    def info(message: str, push_indent: bool = False, color: str = ""):
        """Print a message if TealPrint.level has been set to debug/verbose/info

        Args:
            message (str): The message to print
            push_indent (bool): If messages after this should be indented by one level. Call pop_indent() to unindent
            color (str): Optional color of the message
        """
        TealPrint._buffer.info(message, push_indent, color)
        TealPrint._buffer.flush()

    @staticmethod
    def verbose(message: str, push_indent: bool = False, color: str = ""):
        """Prints a message if TealPrint.level has been set to debug/verbose

        Args:
            message (str): The message to print
            push_indent (bool): If messages after this should be indented by one level. Call pop_indent() to unindent
            color (str): Optional color of the message
        """
        TealPrint._buffer.verbose(message, push_indent, color)
        TealPrint._buffer.flush()

    @staticmethod
    def debug(message: str, push_indent: bool = False, color: str = ""):
        """Prints a message if the TealPrint.level has been set to debug

        Args:
            message (str): The message to print
            push_indent (bool): If messages after this should be indented by one level. Call pop_indent() to unindent
            color (str): Optional color of the message
        """
        TealPrint._buffer.debug(message, push_indent, color)
        TealPrint._buffer.flush()

    @staticmethod
    def push_indent(level: TealLevel) -> None:
        """Add indentation for all messages, but only if level is would be shown"""
        TealPrint._buffer.push_indent(level)

    @staticmethod
    def pop_indent() -> None:
        """
        Remove indentation for all messages. Note that nothing will happen if push_indent() was
        called with a level that wouldn't be shown.

        For example:
            TealConfig.level = TealLevel.info
            TealPrint.push_indent(TealLevel.warning)
            TealPrint.info("Will be indented by 1 level")
            TealPrint.push_indent(TealLevel.verbose)
            TealPrint.info("Will still be indented by 1 level")
            TealPrint.pop_indent()
            TealPrint.info("Will still be indented by 1 level...")
            TealPrint.pop_indent()
            TealPrint.info("Not indentend")
        """
        TealPrint._buffer.pop_indent()

    @staticmethod
    def clear_indent() -> None:
        """
        Removes all indentation. Note that calling pop() will throw an exception now.
        Recommended to use before exiting the app or returning from an excetpion.
        """
        TealPrint._buffer.clear_indent()
