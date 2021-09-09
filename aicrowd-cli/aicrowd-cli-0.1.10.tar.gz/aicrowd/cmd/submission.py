"""
Submission subcommand
"""
import os
import sys

import click

from aicrowd.contexts import (
    pass_config,
    ConfigContext,
    pass_challenge,
    ChallengeContext,
)
from aicrowd.errors import INVALID_FILE
from aicrowd.utils import AliasedGroup
from aicrowd.utils.utils import exception_handler


@click.group(name="submission", cls=AliasedGroup)
def submission_command():
    """
    Create and view submissions
    """


@click.command(name="create")
@click.option(
    "-c",
    "--challenge",
    type=str,
    help="Specify challenge explicitly",
)
@click.option(
    "-f",
    "--file",
    "file_path",
    type=click.Path(),
    default="",
    help="The file to submit",
)
@click.option(
    "-d",
    "--description",
    type=str,
    help="Description",
    default="",
)
@pass_challenge
@pass_config
@exception_handler
def create_subcommand(
    config_ctx: ConfigContext,
    challenge_ctx: ChallengeContext,
    challenge: str,
    file_path: str,
    description: str,
):
    """
    Create a submission on AIcrowd
    """
    if not os.path.exists(file_path):
        click.echo(
            click.style(f"Submission file {file_path} does not exist", fg="red"),
            err=True,
        )
        sys.exit(INVALID_FILE)

    from aicrowd.submission import create_submission

    print(
        create_submission(
            challenge,
            file_path,
            description,
            True,
            config_ctx,
            challenge_ctx,
        )
    )


submission_command.add_command(create_subcommand)
