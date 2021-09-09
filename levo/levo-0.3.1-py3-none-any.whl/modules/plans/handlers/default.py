import click
from levo_commons import events

from ....handlers import EventHandler
from ..context import ExecutionContext


class TestPlanConsoleOutputHandler(EventHandler):
    def handle_event(self, context: ExecutionContext, event: events.Event) -> None:
        """Choose and execute a proper handler for the given event."""
        if isinstance(event, events.Initialized):
            click.echo("Start test session")
            click.echo(event.asdict())
        if isinstance(event, events.BeforeTestSuiteExecution):
            click.echo("Before test suite")
            click.echo(event.asdict())
        if isinstance(event, events.AfterTestSuiteExecution):
            click.echo("After test suite")
            click.echo(event.asdict())
        if isinstance(event, events.BeforeTestCaseExecution):
            click.echo("Before test case")
            click.echo(event.asdict())
        if isinstance(event, events.AfterTestCaseExecution):
            click.echo("After test case")
            click.echo(event.asdict())
        if isinstance(event, events.BeforeTestStepExecution):
            click.echo("Before test step")
            click.echo(event.asdict())
        if isinstance(event, events.AfterTestStepExecution):
            click.echo("After test step")
            click.echo(event.asdict())
        if isinstance(event, events.Finished):
            click.echo("Test session finished!")
            click.echo(event.asdict())
        if isinstance(event, events.Interrupted):
            click.echo("Interrupted!")
            click.echo(event.asdict())
        if isinstance(event, events.InternalError):
            click.echo("Internal error")
            click.echo(event.exception_with_traceback)
