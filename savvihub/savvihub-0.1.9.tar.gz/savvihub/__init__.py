import functools
import inspect

import savvihub
from savvihub._version import __VERSION__
from savvihub.util import logger
from savvihub.util.api import VesslApi
from savvihub.util.constant import VESSL_LOG_LEVEL

__version__ = __VERSION__

# Execution mode
EXEC_MODE = "SDK"

# Make API calls using `vessl_api`
vessl_api = VesslApi()


# Expose functions
init = vessl_api.initialize
update_access_token = vessl_api.update_access_token
update_organization = vessl_api.update_default_organization
update_project = vessl_api.update_default_project

from savvihub.dataset import (
    copy_dataset_volume_file,
    create_dataset,
    delete_dataset_volume_file,
    download_dataset_volume_file,
    list_dataset_volume_files,
    list_datasets,
    read_dataset,
    read_dataset_version,
    upload_dataset_volume_file,
)
from savvihub.experiment import (
    create_experiment,
    download_experiment_output_files,
    list_experiment_logs,
    list_experiment_output_files,
    list_experiments,
    read_experiment,
    read_experiment_by_id,
    update_experiment_plots_files,
    update_experiment_plots_metrics,
)
from savvihub.kernel_cluster import (
    delete_cluster,
    list_cluster_nodes,
    list_clusters,
    read_cluster,
    rename_cluster,
)
from savvihub.kernel_image import list_kernel_images, read_kernel_image
from savvihub.kernel_resource_spec import (
    list_kernel_resource_specs,
    read_kernel_resource_spec,
)
from savvihub.model import (
    create_model,
    delete_model,
    list_models,
    read_model,
    update_model,
)
from savvihub.organization import (
    create_organization,
    list_organizations,
    read_organization,
)
from savvihub.project import clone_project, create_project, list_projects, read_project
from savvihub.ssh_key import create_ssh_key, delete_ssh_key, list_ssh_keys
from savvihub.sweep import (
    create_sweep,
    list_sweep_logs,
    list_sweeps,
    read_sweep,
    terminate_sweep,
)
from savvihub.volume import (
    copy_volume_file,
    create_volume_file,
    delete_volume_file,
    list_volume_files,
    read_volume_file,
)
from savvihub.workspace import (
    backup_workspace,
    connect_workspace_ssh,
    list_workspaces,
    read_workspace,
    restore_workspace,
    update_vscode_remote_ssh,
)

# Expose others
from savvihub.integration.common import log  # isort:skip
from savvihub.util.image import Image  # isort:skip


# Suppress all exceptions during SDK mode
def suppress_sdk_exception(f):
    @functools.wraps(f)
    def func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            if EXEC_MODE == "SDK":
                # Temporarily disable all exceptions that occur within the SDK
                # TODO (VSSL-1992): raise appropriate errors
                exc_info = e if VESSL_LOG_LEVEL == "DEBUG" else False
                logger.exception(f"{e.__class__.__name__}: {str(e)}", exc_info=exc_info)
            else:
                raise e

    return func


# SDK functions that the user may interact with
for name, value in inspect.getmembers(
    savvihub, predicate=lambda x: inspect.ismethod(x) or inspect.isfunction(x)
):
    vars()[name] = suppress_sdk_exception(value)

# Other classes that the user may interact with
user_classes = [Image]
for user_class in user_classes:
    for name, value in inspect.getmembers(
        user_class, predicate=lambda x: inspect.ismethod(x) or inspect.isfunction(x)
    ):
        setattr(user_class, name, suppress_sdk_exception(value))
