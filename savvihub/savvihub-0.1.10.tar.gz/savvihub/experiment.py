from typing import Dict, List, Tuple

from openapi_client.models import (
    CliExperimentPlotsFilesUpdateAPIPayload,
    CliExperimentPlotsMetricsUpdateAPIPayload,
    ExperimentCreateAPIPayload,
    InfluxdbExperimentPlotFile,
    InfluxdbExperimentPlotMetric,
    InfluxdbWorkloadLog,
    OrmEnvVar,
    ResponseExperimentInfo,
    ResponseExperimentListResponse,
    ResponseFileMetadata,
)
from savvihub import vessl_api
from savvihub.kernel_cluster import read_cluster
from savvihub.kernel_resource_spec import (
    _configure_custom_kernel_resource_spec,
    read_kernel_resource_spec,
)
from savvihub.organization import _get_organization_name
from savvihub.project import _get_project_name
from savvihub.util import logger
from savvihub.util.constant import MOUNT_PATH_OUTPUT, MOUNT_TYPE_OUTPUT
from savvihub.volume import (
    _configure_volume_mount_requests,
    copy_volume_file,
    list_volume_files,
)


def read_experiment(experiment_name_or_number: str, **kwargs) -> ResponseExperimentInfo:
    """Read experiment

    Keyword args:
        organization_name (str): override default organization
        project_name (str): override default project
    """
    return vessl_api.experiment_read_api(
        experiment=experiment_name_or_number,
        organization_name=_get_organization_name(**kwargs),
        project_name=_get_project_name(**kwargs),
    )


def read_experiment_by_id(experiment_id: int, **kwargs) -> ResponseExperimentInfo:
    return vessl_api.experiment_read_by_idapi(experiment_id=experiment_id)


def list_experiments(**kwargs) -> List[ResponseExperimentListResponse]:
    """List experiments

    Keyword args:
        organization_name (str): override default organization
        project_name (str): override default project
    """
    return vessl_api.experiment_list_api(
        organization_name=_get_organization_name(**kwargs),
        project_name=_get_project_name(**kwargs),
    ).results


def create_experiment(
    cluster_name: str,
    start_command: str,
    kernel_resource_spec_name: str = None,
    processor_type: str = None,
    cpu_limit: float = None,
    memory_limit: float = None,
    gpu_type: str = None,
    gpu_limit: int = None,
    kernel_image_url: str = None,
    *,
    message: str = None,
    termination_protection: bool = False,
    env_vars: List[Tuple[str, str]] = None,
    dataset_mounts: List[Tuple[str, str]] = None,
    root_volume_size: str = None,
    working_dir: str = None,
    output_dir: str = MOUNT_PATH_OUTPUT,
    local_project_url: str = None,
    **kwargs,
) -> ResponseExperimentInfo:
    """Create experiment

    Keyword args:
        organization_name (str): override default organization
        project_name (str): override default project
        git_branch (str): override current git branch
        git_ref (str): override current git commit
        use_git_diff (bool): run experiment with uncommitted changes
        use_git_diff_untracked (bool): run with untracked changed (only valid if `use_git_diff` is set)
    """
    cluster = read_cluster(cluster_name)

    kernel_resource_spec = kernel_resource_spec_id = None
    if cluster.is_savvihub_managed:  # TODO: rename to vessl
        kernel_resource_spec_id = read_kernel_resource_spec(
            kernel_resource_spec_name
        ).id
    else:
        kernel_resource_spec = _configure_custom_kernel_resource_spec(
            processor_type,
            cpu_limit,
            memory_limit,
            gpu_type,
            gpu_limit,
        )

    volume_mount_requests = _configure_volume_mount_requests(
        dataset_mounts=dataset_mounts,
        root_volume_size=root_volume_size,
        working_dir=working_dir,
        output_dir=output_dir,
        local_project_url=local_project_url,
        **kwargs,
    )

    return vessl_api.experiment_create_api(
        organization_name=_get_organization_name(**kwargs),
        project_name=_get_project_name(**kwargs),
        experiment_create_api_payload=ExperimentCreateAPIPayload(
            cluster_name=cluster_name,
            env_vars=[OrmEnvVar(key, str(value)) for key, value in (env_vars or [])],
            image_url=kernel_image_url,
            message=message,
            resource_spec=kernel_resource_spec,
            resource_spec_id=kernel_resource_spec_id,
            start_command=start_command,
            termination_protection=termination_protection,
            volumes=volume_mount_requests,
        ),
    )


def list_experiment_logs(
    experiment_name: str, tail: int = 200, **kwargs
) -> List[InfluxdbWorkloadLog]:
    """List experiment logs

    Args:
        tail (int): number of lines to display from the end. Display all if -1.

    Keyword args:
        organization_name (str): override default organization
        project_name (str): override default project
    """
    if tail == -1:
        tail = None

    return vessl_api.experiment_logs_api(
        experiment=experiment_name,
        limit=tail,
        organization_name=_get_organization_name(**kwargs),
        project_name=_get_project_name(**kwargs),
    ).logs


def list_experiment_output_files(
    experiment_name: str,
    need_download_url: bool = False,
    recursive: bool = False,
    **kwargs,
) -> List[ResponseFileMetadata]:
    """List experiment output files

    Keyword args:
        organization_name (str): override default organization
        project_name (str): override default project
    """
    experiment_name = read_experiment(experiment_name, **kwargs)

    for volume_mount in experiment_name.volume_mounts.mounts:
        if volume_mount.source_type == MOUNT_TYPE_OUTPUT:
            return list_volume_files(
                volume_id=volume_mount.volume.volume_id,
                need_download_url=need_download_url,
                path="",
                recursive=recursive,
            )

    logger.info("No output volume mounted")


def download_experiment_output_files(
    experiment_name: str, dest_path: str = "./output", **kwargs
) -> None:
    """Download experiment output files

    Keyword args:
        organization_name (str): override default organization
        project_name (str): override default project
    """
    experiment = read_experiment(experiment_name, **kwargs)
    for volume_mount in experiment.volume_mounts.mounts:
        if volume_mount.source_type == MOUNT_TYPE_OUTPUT:
            return copy_volume_file(
                source_volume_id=volume_mount.volume.volume_id,
                source_path="",
                dest_volume_id=None,
                dest_path=dest_path,
                recursive=True,
            )

    logger.info("No output volume mounted")


def update_experiment_plots_files(
    experiment_id: int, files: List[InfluxdbExperimentPlotFile], type: str
) -> object:
    return vessl_api.cli_experiment_plots_files_update_api(
        experiment_id=experiment_id,
        cli_experiment_plots_files_update_api_payload=CliExperimentPlotsFilesUpdateAPIPayload(
            files=files,
            type=type,
        ),
    )


def update_experiment_plots_metrics(
    experiment_id: int, metrics: Dict[str, List[InfluxdbExperimentPlotMetric]]
) -> object:
    return vessl_api.cli_experiment_plots_metrics_update_api(
        experiment_id=experiment_id,
        cli_experiment_plots_metrics_update_api_payload=CliExperimentPlotsMetricsUpdateAPIPayload(
            metrics=metrics,
        ),
    )
