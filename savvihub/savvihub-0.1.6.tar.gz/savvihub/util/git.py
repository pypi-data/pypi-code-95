import os
from typing import Optional

from openapi_client.models import ResponseProjectInfo
from savvihub import vessl_api
from savvihub.util.constant import PROJECT_TYPE_CLI_DRIVEN
from savvihub.util.exception import GitError
from savvihub.util.git_repo import GitRepository
from savvihub.util.uploader import Uploader


def get_git_branch(project: ResponseProjectInfo, **kwargs) -> Optional[str]:
    if project.type == PROJECT_TYPE_CLI_DRIVEN:
        return None

    if "git_branch" in kwargs:
        return kwargs["git_branch"]
    if vessl_api.default_git_repo is not None:
        return vessl_api.default_git_repo.branch
    raise GitError("No git branch selected.")


def get_git_ref(project: ResponseProjectInfo, **kwargs) -> Optional[str]:
    if project.type == PROJECT_TYPE_CLI_DRIVEN:
        return None

    if vessl_api.default_git_repo is None:
        raise GitError("No git commit selected.")

    if "git_ref" in kwargs:
        git_ref = kwargs["git_ref"]
        if vessl_api.default_git_repo.check_revision_in_remote(git_ref):
            return git_ref
        raise GitError(f"Git commit does not exist in a remote repository: {git_ref}")

    return vessl_api.default_git_repo.commit_ref


def get_git_diff_path(project: ResponseProjectInfo, **kwargs) -> Optional[str]:
    use_git_diff = kwargs.get("use_git_diff", False)
    use_git_diff_untracked = kwargs.get("use_git_diff_untracked", False)

    if not use_git_diff or project.type == PROJECT_TYPE_CLI_DRIVEN:
        return None

    if vessl_api.default_git_repo is None:
        raise GitError("No git repo")

    local_file = GitRepository.get_current_diff_file(
        revision_or_branch=get_git_ref(project), with_untracked=use_git_diff_untracked
    )

    remote_file = Uploader.upload(
        local_path=local_file.name,
        volume_id=project.volume_id,
        remote_path=os.path.basename(local_file.name),
    )

    local_file.close()
    return remote_file.path
