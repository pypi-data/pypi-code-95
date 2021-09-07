import json
import os
from typing import Any


# Default filename of the experiment metadata associated
# with an Akoya CODEX experiment.
EXPERIMENT_JSON = 'experiment.json'


def read_experiment_metadata(input_dir: str,
                             filename=EXPERIMENT_JSON) -> Any: 
    """Reads the metadata of an Akoya CODEX experiment into a dict.

    Args:
        input_dir: The directory that holds the metadata file, normally the CODEX experiment directory.
        filename: The name of the experiment metadata JSON file, normally "experiment.json".

    Returns:
        A dict mapping string keys to values: dict[str, Any].
        The dict contains metadata about the dataset for the CODEX experiment,
        such as number of tile rows and columns, number of experiment cycles, 
        amount of tile overlap, etc.
    """
    experiment_file = os.path.join(input_dir, filename)
    with open(experiment_file) as f:
        experiment = json.load(f)
    return experiment


def write_experiment_metadata(experiment: dict[str, Any], 
                              output_dir: str,
                              filename=EXPERIMENT_JSON) -> None:
    """Saves a CODEX experiment metadata dictionary to a JSON file.

    Args:
        experiment: The experiment metadata dictionary.
        output_dir: The directory to write the experiment metadata JSON file to.
        filename: The name of the JSON file to save the experiment metadata to, normally "experiment.json".
    """
    with open(os.path.join(output_dir, filename), 'w') as f:
        json.dump(experiment, f, indent=2)
