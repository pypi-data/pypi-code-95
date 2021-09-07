import os
import warnings
from collections import defaultdict
from datetime import datetime
from numbers import Number
from typing import Any, Dict, List, Union

from openapi_client.models import (
    InfluxdbExperimentPlotFile,
    InfluxdbExperimentPlotMetric,
    ResponseExperimentInfo,
)
from savvihub import vessl_api
from savvihub.experiment import (
    read_experiment_by_id,
    update_experiment_plots_files,
    update_experiment_plots_metrics,
)
from savvihub.util.constant import VESSL_IMAGE_PATH, VESSL_PLOTS_FILETYPE_IMAGE
from savvihub.util.exception import SavvihubApiException
from savvihub.util.image import Image
from savvihub.volume import copy_volume_file

ImageRowType = Dict[str, List[Image]]
MetricRowType = Dict[str, Number]
RowType = Union[ImageRowType, MetricRowType]

current_experiment: ResponseExperimentInfo = None


def _update_current_experiment():
    global current_experiment
    experiment_id = os.environ.get(
        "SAVVIHUB_EXPERIMENT_ID", None
    )  # TODO: rename on server
    access_token = os.environ.get(
        "SAVVIHUB_ACCESS_TOKEN", None
    )  # TODO: rename on server

    if experiment_id is None or access_token is None:
        return

    vessl_api.update_access_token(access_token)
    current_experiment = read_experiment_by_id(experiment_id)


def get_current_experiment() -> ResponseExperimentInfo:
    global current_experiment
    if current_experiment != None:
        return current_experiment

    _update_current_experiment()
    return current_experiment


def _update_images(row: ImageRowType):
    images = row.values()

    path_to_caption = {}
    for image in images:
        path_to_caption[image.path] = image.caption

    source_path = VESSL_IMAGE_PATH + "/"
    dest_volume_id = current_experiment.experiment_plot_volume
    dest_path = source_path

    files = copy_volume_file(
        source_volume_id=None,
        source_path=source_path,
        dest_volume_id=dest_volume_id,
        dest_path=dest_path,
        recursive=True,
    )

    plot_files = [
        InfluxdbExperimentPlotFile(
            step=None,
            path=file.path,
            caption=path_to_caption[file.path],
            timestamp=datetime.utcnow().timestamp(),
        )
        for file in files
    ]

    update_experiment_plots_files(
        experiment_id=current_experiment.id,
        files=plot_files,
        type=VESSL_PLOTS_FILETYPE_IMAGE,
    )

    for image in images:
        image.flush()


def _update_metrics(row: MetricRowType, step: int):
    plot_metrics: Dict[str, List[InfluxdbExperimentPlotMetric]] = defaultdict(list)

    for key, val in row.items():
        plot_metrics[key].append(
            InfluxdbExperimentPlotMetric(
                step=step,
                timestamp=datetime.utcnow().timestamp(),
                value=float(val),
            )
        )

    update_experiment_plots_metrics(
        experiment_id=current_experiment.id, metrics=plot_metrics
    )


def _log(row: RowType, step: int = None):
    # TODO: type validation? (ref: legacy client)
    # row, step = _refine(row, step)

    for val in row.values():
        if isinstance(val, list) and all(isinstance(i, Image) for i in val):
            _update_images(row)
        else:
            _update_metrics(row, step)
        break


def log(row: RowType, step: int = None):
    """Log a metric during a Vessl experiment.

    This function must be called on the Vessl infrastructure to log the metric.
    If not executed on Vessl's infrastructure, this function has no effect.

    :param row: a dictionary to log (required)
    :param step: a step(positive integer) for each iteration
    """

    _update_current_experiment()

    try:
        _log(row, step)

    except SavvihubApiException as e:
        warnings.warn(f"Cannot send metrics {row} for step {step}: {e.message}")
