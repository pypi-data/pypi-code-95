"""
Main training CLI

"""
import json

from click import (
    UNPROCESSED,
    File,
    argument,
    command,
    option,
)
from microcosm.loaders import load_from_dict
from microcosm.loaders.compose import merge
from microcosm.object_graph import ObjectGraph

from microcosm_sagemaker.app_hooks import create_train_app
from microcosm_sagemaker.artifact import RootOutputArtifact
from microcosm_sagemaker.commands.config import load_config_from_command_line_arguments
from microcosm_sagemaker.commands.evaluate import run_evaluate
from microcosm_sagemaker.commands.options import input_data_option, output_artifact_option
from microcosm_sagemaker.exceptions import raise_sagemaker_exception
from microcosm_sagemaker.input_data import InputData


@command(
    context_settings=dict(
        ignore_unknown_options=True,
    )
)
@option(
    "--configuration",
    type=File('r'),
    help="Manual import of configuration file, used for local testing",
)
@input_data_option()
@output_artifact_option()
@option(
    "--auto-evaluate/--no-auto-evaluate",
    default=True,
    help="Whether to automatically evaluate after the training has completed",
)
@option(
    "--testing/--no-testing",
    default=False,
    help="Whether the training is for testing purposes"
)
@argument('command_line_config', nargs=-1, type=UNPROCESSED)
def main(configuration, input_data, output_artifact, auto_evaluate, testing, command_line_config):
    try:

        extra_config_from_file = json.load(configuration) if configuration else dict()
        extra_config_from_command_line = load_config_from_command_line_arguments(command_line_config)
        extra_config = merge([extra_config_from_file, extra_config_from_command_line])

        graph = create_train_app(
            extra_loader=load_from_dict(extra_config),
            testing=testing,
        )

        run_train(
            graph=graph,
            input_data=input_data,
            root_output_artifact=output_artifact,
        )

        if auto_evaluate:
            run_evaluate(graph, input_data)

    except Exception as e:
        raise_sagemaker_exception(e)


def run_train(
    graph: ObjectGraph,
    input_data: InputData,
    root_output_artifact: RootOutputArtifact,
) -> None:
    root_output_artifact.init()

    graph.experiment_metrics.init()

    root_output_artifact.save_config(graph.config)

    graph.bundle_and_dependencies_trainer(
        bundle=graph.active_bundle,
        input_data=input_data,
        root_output_artifact=root_output_artifact,
    )
