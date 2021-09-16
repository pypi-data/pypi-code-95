from microcosm.config.model import Configuration
from microcosm.loaders import expand_config
from microcosm.metadata import Metadata

from microcosm_sagemaker.constants import SagemakerPath


def load_default_microcosm_runserver_config(metadata: Metadata) -> Configuration:
    """
    Construct runserver default configuration.

    """

    config = Configuration(
        root_input_artifact_path=SagemakerPath.MODEL,
    )

    return config


def split_args_into_key_values(args):
    """
    Receives a list of string command line arguments.
    For the ones with the `--KEY=VALUE` format (which is the format used by wandb to inject hyperparameters),
    creates a {KEY: VALUE} dictionary and returns.

    """
    args = [
        arg.strip()[2:]
        for arg in args
        if arg.strip().startswith("--") and "=" in arg
    ]

    return {
        arg.split("=")[0]: arg.split("=")[1]
        for arg in args
    }


def value_func_with_quote_handling(value):
    """
    To pass values that include spaces through command line arguments, they must be quoted. For instance:
    --parameter='some value with space' or
    --parameter="some value with space".
    In this value parser, we remove the quotes to receive a clean string.

    """
    if value[0] == value[-1] and value[0] in ["'", '"']:
        return value[1:-1]
    return value


def load_config_from_command_line_arguments(command_line_config):
    """
    Load configuration from command line arguments.

    """
    config = expand_config(
        split_args_into_key_values(command_line_config),
        value_func=value_func_with_quote_handling
    )

    return Configuration(config)
