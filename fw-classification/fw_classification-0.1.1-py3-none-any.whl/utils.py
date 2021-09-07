"""Logging for the CLI."""
import logging

import typer


def configure_logging(verbose: bool):  # pragma: no cover
    """Intercept log and echo them to console."""
    log = logging.getLogger()
    log.setLevel(0)
    cli_handler = CLIHandler()
    cli_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    log.addHandler(cli_handler)


class CLIHandler(logging.Handler):  # pragma: no cover
    """Handler to redirect logs to echo."""

    def emit(self, record):
        """Redirect logs to echo to console."""
        msg = record.getMessage()
        typer.echo(f"{record.name}:\t{msg}")
