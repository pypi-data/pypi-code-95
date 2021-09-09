from rich.logging import RichHandler
import pretty_errors
import sys
def get_logger():
    from loguru import logger
    logger.remove()
    logger.add(sys.stdout, colorize=True)
    logger.configure(handlers=[{"sink": RichHandler(markup=True),
                                "format": "[red]{function}[/red] {message}"}])

    logger.remove()
    logger.add(sys.stdout, colorize=True)
    return logger


pretty_errors.configure(
    separator_character = '*',
    filename_display    = pretty_errors.FILENAME_EXTENDED,
    line_number_first   = True,
    display_link        = True,
    lines_before        = 5,
    lines_after         = 2,
    line_color          = pretty_errors.RED + '> ' + pretty_errors.default_config.line_color,
    code_color          = '  ' + pretty_errors.default_config.line_color,
    truncate_code       = True,
    display_locals      = True
)
