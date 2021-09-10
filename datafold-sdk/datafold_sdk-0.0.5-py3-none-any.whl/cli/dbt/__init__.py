import logging

import click

from datafold.sdk.dbt import submit_artifacts, wait_for_completion

logger = logging.getLogger(__file__)


@click.group()
@click.pass_context
def manager(ctx):
    """DBT integration with Datafold"""


@manager.command()
@click.option('--ci-config-id',
              help="The ID of the CI config in Datafold (see CI settings screen)",
              type=int,
              required=True)
@click.option('--run-type',
              help="Submit the manifest as either 'production' or 'pull_request'",
              type=str,
              required=True)
@click.option('--target-folder',
              help="Path to the target folder of the dbt run",
              required=True,
              default='./target/',
              type=click.Path(exists=True))
@click.option('--commit-sha',
              help="Override the commit sha",
              type=str,
              required=False)
@click.pass_context
def upload(ctx, ci_config_id: int, run_type: str, target_folder, commit_sha: str = None):
    """Uploads the artefacts of a dbt run."""

    run_types = {'production', 'pull_request'}
    if run_type not in run_types:
        raise ValueError(f"Run type {run_type} is not valid, should be {' or '.join(run_types)}")

    submit_artifacts(host=ctx.obj.host,
                     api_key=ctx.obj.api_key,
                     ci_config_id=ci_config_id,
                     run_type=run_type,
                     target_folder=click.format_filename(target_folder),
                     commit_sha=commit_sha)


@manager.command()
@click.option('--ci-config-id',
              help="The ID of the CI config in Datafold (see CI settings screen)",
              type=int,
              required=True)
@click.option('--run-type',
              help="Submit the manifest as either 'production' or 'pull_request'",
              type=str,
              required=True)
@click.option('--target-folder',
              help="Path to the target folder of the dbt run",
              required=True,
              type=click.Path(exists=True))
@click.option('--commit-sha',
              help="Override the commit sha",
              type=str,
              required=False)
@click.pass_context
def upload_and_wait(ctx, ci_config_id: int, run_type: str, target_folder, commit_sha: str = None):
    """Uploads the artefacts of dbt and waits for the data diff to complete"""
    sha = submit_artifacts(host=ctx.obj.host,
                           api_key=ctx.obj.api_key,
                           ci_config_id=ci_config_id,
                           run_type=run_type,
                           target_folder=click.format_filename(target_folder),
                           commit_sha=commit_sha)
    # This only makes sense for Pull Requests,
    # otherwise there won't be a PR
    if run_type == 'pull_request':
        wait_for_completion(
            host=ctx.obj.host,
            api_key=ctx.obj.api_key,
            ci_config_id=ci_config_id,
            commit_sha=sha
        )
