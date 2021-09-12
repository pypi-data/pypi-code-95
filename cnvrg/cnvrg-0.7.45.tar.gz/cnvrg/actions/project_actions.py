from cnvrg.modules.storage import Storage
from cnvrg.modules.project import Project
from cnvrg.modules.storage import storage_factory
from cnvrg.helpers.status_helpers import CommitStatus
from cnvrg.actions import check_if_path_exists
import os
from cnvrg.helpers import log_message
from cnvrg.modules.commituploader import CommitUploader


def clone(project_url, commit_sha1=None, working_dir=None):
    ## creating project
    project = Project(project_url=project_url, working_dir=working_dir)
    log_message("Cloning {project}".format(project=project.get_project_name()))
    project_path = os.path.join(working_dir or os.curdir, project.get_project_name())
    project._set_working_dir(project_path)

    ## handle already exists
    check_if_path_exists(project_path)
    os.makedirs(project_path, exist_ok=True)

    #init storage
    storage = storage_factory(project, working_dir=project_path)
    commit = project.fetch_commit(commit_sha1 or "latest")
    #download
    storage.download_dirs(commit.get("trees"))
    storage.download_files(commit.get("blobs"))

    #post download
    project._clone_finish(commit.get("sha1"), project_path)

    log_message("{project} cloned successfuly".format(project=project.get_project_name()))
    return project_path


def download(storage: Storage=None, commit_sha1=None, force=False):
    storage = storage or storage_factory(Project())
    element = storage.element
    status_o = element.status(to_commit=commit_sha1)
    files_to_download = status_o[CommitStatus.UPDATED_ON_SERVER]
    files_to_delete = status_o[CommitStatus.DELETED_ON_REMOTE]

    ####
    # we need to rename all the delete with conflicts to FILENAME.deleted
    # we need to download all the files from updated on server with the name of FILENAME.conflict
    ####
    files_to_delete_with_conflict = status_o[CommitStatus.DELETED_CONFLICTS] if not force else []
    conflicts = status_o[CommitStatus.CONFLICTS] if not force else []
    ####

    ### Latest commit or commit to download
    commit_sha1 = status_o[CommitStatus.COMMIT_SHA1]
    if commit_sha1 == element.get_current_commit():
        log_message("Already up to date")
        return

    if len(files_to_download) > 0:
        files = storage.element.get_commit_files(commit_sha1=commit_sha1, files=files_to_download)
        log_message("Downloading {count} files".format(count=len(files)))
        storage.download_files(files, conflicts=conflicts)
    if len(files_to_delete) > 0:
        storage.delete_files(files_to_delete, conflicts=files_to_delete_with_conflict)
    storage.element._download_finish(commit_sha1)
    log_message("Project downloaded successfuly")


def upload(storage: Storage=None, force=False, new_branch=False):
    storage = storage or storage_factory(Project())
    status_o = storage.element.status(force=force, new_branch=new_branch)
    CommitUploader(storage, status_o)


