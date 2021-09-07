import subprocess
from typing import List

from openapi_client.models import (
    CLIProjectCreateAPIPayload,
    GitHubProjectCreateAPIPayload,
    ResponseProjectInfo,
)
from savvihub import vessl_api
from savvihub.organization import _get_organization_name
from savvihub.util import logger
from savvihub.util.constant import PROJECT_TYPE_CLI_DRIVEN, PROJECT_TYPE_VERSION_CONTROL
from savvihub.util.exception import InvalidProjectError


def read_project(project_name: str, **kwargs) -> ResponseProjectInfo:
    """Read project

    Keyword args:
        organization_name (str): override default organization
    """
    return vessl_api.project_read_api(
        organization_name=_get_organization_name(**kwargs),
        project_name=project_name,
    )


def list_projects(**kwargs) -> List[ResponseProjectInfo]:
    """List projects

    Keyword args:
        organization_name (str): override default organization
    """
    return vessl_api.project_list_api(
        organization_name=_get_organization_name(**kwargs),
    ).results


def create_project(
    project_type: str,
    project_name: str,
    description: str = None,
    github_owner: str = None,
    github_repo: str = None,
    **kwargs,
) -> ResponseProjectInfo:
    if project_type == PROJECT_TYPE_VERSION_CONTROL:
        return vessl_api.git_hub_project_create_api(
            organization_name=_get_organization_name(**kwargs),
            git_hub_project_create_api_payload=GitHubProjectCreateAPIPayload(
                name=project_name,
                description=description,
                github_owner=github_owner,
                github_repo=github_repo,
            ),
        )

    if project_type == PROJECT_TYPE_CLI_DRIVEN:
        return vessl_api.c_li_project_create_api(
            organization_name=_get_organization_name(**kwargs),
            cli_project_create_api_payload=CLIProjectCreateAPIPayload(
                name=project_name,
                description=description,
            ),
        )

    raise InvalidProjectError(
        f"Invalid project type: {project_type}. Must be version-control or cli-driven."
    )


def clone_project(project_name: str, **kwargs) -> None:
    """Clone project

    Keyword args:
        organization_name (str): override default organization
    """
    project = read_project(project_name, **kwargs)

    if project.type != PROJECT_TYPE_VERSION_CONTROL:
        raise InvalidProjectError("Project type must be version-control.")

    github_token = vessl_api.cli_git_hub_token_api().token

    dirname = project.cached_git_repo_slug
    git_url = f"https://{github_token}@github.com/{project.cached_git_owner_slug}/{project.cached_git_repo_slug}.git"
    try:
        subprocess.check_output(["git", "clone", git_url])
    except subprocess.CalledProcessError:
        dirname = f"savvihub-{project.cached_git_repo_slug}"
        logger.info(f"Falling back to '{dirname}'...")
        subprocess.check_output(["git", "clone", git_url, dirname])

    subprocess.check_output(["rm", "-rf", f"{dirname}/.git"])


def _get_project_name(**kwargs) -> str:
    project_name = kwargs.get("project_name")
    if project_name is not None:
        return project_name
    if vessl_api.project is not None:
        return vessl_api.project.name
    raise InvalidProjectError("No project selected.")


def _get_project(**kwargs) -> ResponseProjectInfo:
    project_name = kwargs.get("project_name")
    if project_name is not None:
        return read_project(project_name)
    if vessl_api.project is not None:
        return vessl_api.project
    raise InvalidProjectError("No project selected.")
