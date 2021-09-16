from typing import Any, Dict, List, Tuple

import click

from savvihub.cli._base import VesslGroup, vessl_argument, vessl_option
from savvihub.cli._util import (
    Endpoint,
    choices_prompter,
    format_string,
    generic_prompter,
    print_data,
    print_logs,
    print_table,
    prompt_choices,
    truncate_datetime,
)
from savvihub.cli.experiment import (
    cluster_option,
    command_option,
    cpu_limit_option,
    dataset_option,
    env_var_option,
    gpu_limit_option,
    gpu_type_option,
    image_url_option,
    local_project_option,
    memory_limit_option,
    message_option,
    output_dir_option,
    processor_option,
    resource_option,
    root_volume_size_option,
    working_dir_option,
)
from savvihub.cli.organization import organization_name_option
from savvihub.cli.project import project_name_option
from savvihub.sweep import (
    create_sweep,
    list_sweep_logs,
    list_sweeps,
    read_sweep,
    terminate_sweep,
)
from savvihub.util.constant import (
    SWEEP_ALGORITHM_TYPES,
    SWEEP_OBJECTIVE_TYPE_MAXIMIZE,
    SWEEP_OBJECTIVE_TYPES,
    SWEEP_PARAMETER_RANGE_TYPE_LIST,
    SWEEP_PARAMETER_RANGE_TYPE_SPACE,
    SWEEP_PARAMETER_RANGE_TYPES,
    SWEEP_PARAMETER_TYPES,
)


class SweepParameterType(click.ParamType):
    name = "Parameter type"

    def convert(self, raw_value: Any, param, ctx) -> Any:
        tokens = raw_value.split()

        if len(tokens) < 4:
            raise click.BadOptionUsage(
                option_name="parameter",
                message=f"Invalid value for [PARAMETER]: '{raw_value}' must be of form [name] [type] [range type] [values...].",
            )

        name = tokens[0]
        type = click.Choice(SWEEP_PARAMETER_TYPES).convert(tokens[1], param, ctx)
        range_type = click.Choice(SWEEP_PARAMETER_RANGE_TYPES).convert(
            tokens[2], param, ctx
        )
        values = tokens[3:]

        parameter = {"name": name, "type": type}

        if range_type == SWEEP_PARAMETER_RANGE_TYPE_LIST:
            parameter["range"] = {"list": values}
            return parameter

        if len(values) < 3:
            raise click.BadOptionUsage(
                option_name="parameter",
                message=f"Invalid value for [PARAMETER]: range type '{SWEEP_PARAMETER_RANGE_TYPE_SPACE}' must have min, max, step values.",
            )

        parameter["range"] = {
            "min": values[0],
            "max": values[1],
            "step": values[2],
        }
        return parameter


def sweep_name_prompter(ctx: click.Context, param: click.Parameter, value: str) -> str:
    sweeps = list_sweeps()
    return prompt_choices("Sweep", [x.name for x in sweeps])


def parameter_prompter(ctx: click.Context, param: click.Parameter, value: str) -> str:
    parameters = []

    while True:
        index = len(parameters) + 1
        name = click.prompt(f"Parameter #{index} name")
        type = prompt_choices(f"Parameter #{index} type", SWEEP_PARAMETER_TYPES)
        range_type = prompt_choices(
            f"Parameter #{index} range type", SWEEP_PARAMETER_RANGE_TYPES
        )

        if range_type == SWEEP_PARAMETER_RANGE_TYPE_LIST:
            values = click.prompt(f"Parameter #{index} values (space separated)")
        else:
            values = click.prompt(f"Parameter #{index} values ([min] [max] [step])")

        parameters.append(f"{name} {type} {range_type} {values}")

        if not click.prompt("Add another parameter (y/n)", type=click.BOOL):
            break

    return parameters


@click.command(name="sweep", cls=VesslGroup)
def cli():
    pass


@cli.vessl_command()
@vessl_argument("name", type=click.STRING, required=True, prompter=sweep_name_prompter)
@organization_name_option
@project_name_option
def read(name: str):
    sweep = read_sweep(sweep_name=name)
    print_data(
        {
            "ID": sweep.id,
            "Name": sweep.name,
            "Status": sweep.status,
            "Created": truncate_datetime(sweep.created_dt),
            "Message": format_string(sweep.message),
            "Source Code": sweep.source_code_link[0].url,
            "Objective": (
                f"{sweep.objective.type}"
                f"{' > ' if sweep.objective.metric == SWEEP_OBJECTIVE_TYPE_MAXIMIZE else ' < '}"
                f"{sweep.objective.goal}"
            ),
            "Common Parameters": {
                "Max Experiment Count": sweep.max_experiment_count,
                "Parallel Experiment Count": sweep.parallel_experiment_count,
                "Max Failed Experiment Count": sweep.max_failed_experiment_count,
            },
            "Algorithm": sweep.algorithm,
            "Parameters": [
                {
                    "Name": x.name,
                    "Type": x.type,
                    "Values": {
                        "Min": x.range.min,
                        "Max": x.range.max,
                        "Step": x.range.step,
                    }
                    if x.range.list is None
                    else {
                        "List": x.range.list,
                    },
                }
                for x in sweep.search_space.parameters
            ],
            "Experiments": f"{sweep.experiment_summary.total}/{sweep.max_experiment_count}",
            "Kernel Image": {
                "Name": sweep.kernel_image.name,
                "URL": sweep.kernel_image.image_url,
            },
            "Resource Spec": {
                "Name": sweep.kernel_resource_spec.name,
                "CPU Type": sweep.kernel_resource_spec.cpu_type,
                "CPU Limit": sweep.kernel_resource_spec.cpu_limit,
                "Memory Limit": sweep.kernel_resource_spec.memory_limit,
                "GPU Type": sweep.kernel_resource_spec.gpu_type,
                "GPU Limit": sweep.kernel_resource_spec.gpu_limit,
            },
            "Start command": sweep.start_command,
        }
    )
    print(
        f"For more info: {Endpoint.sweep.format(sweep.organization.name, sweep.project.name, sweep.name)}"
    )


@cli.vessl_command()
@organization_name_option
@project_name_option
def list():
    sweeps = list_sweeps()
    print_table(
        sweeps,
        ["ID", "Name", "Status", "Created", "Experiments"],
        lambda x: [
            x.id,
            x.name,
            x.status,
            truncate_datetime(x.created_dt),
            f"{x.experiment_summary.total}/{x.max_experiment_count}",
        ],
    )


@cli.vessl_command()
@vessl_option(
    "-T",
    "--objective-type",
    type=click.Choice(SWEEP_OBJECTIVE_TYPES),
    required=True,
    prompter=choices_prompter("Objective type", SWEEP_OBJECTIVE_TYPES),
)
@vessl_option(
    "-G",
    "--objective-goal",
    type=click.FLOAT,
    required=True,
    prompter=generic_prompter("Objective goal", click.FLOAT),
)
@vessl_option(
    "-M",
    "--objective-metric",
    type=click.STRING,
    required=True,
    prompter=generic_prompter("Objective metric", click.STRING),
)
@vessl_option(
    "--num-experiments",
    type=click.INT,
    required=True,
    prompter=generic_prompter("Maximum number of experiments", click.INT),
    help="Maximum number of experiments.",
)
@vessl_option(
    "--num-parallel",
    type=click.INT,
    required=True,
    prompter=generic_prompter("Number of experiments to be run in parallel", click.INT),
    help="Number of experiments to be run in parallel.",
)
@vessl_option(
    "--num-failed",
    type=click.INT,
    required=True,
    prompter=generic_prompter(
        "Maximum number of experiments to allow to fail", click.INT
    ),
    help="Maximum number of experiments to allow to fail.",
)
@vessl_option(
    "-a",
    "--algorithm",
    type=click.Choice(SWEEP_ALGORITHM_TYPES),
    required=True,
    prompter=choices_prompter("Sweep algorithm", SWEEP_ALGORITHM_TYPES),
    help="Sweep algorithm.",
)
@vessl_option(
    "-p",
    "--parameter",
    type=SweepParameterType(),
    multiple=True,
    prompter=parameter_prompter,
    help="Search space parameters (at least one required). Format: [name] [type] [range type] [values...], ex. `-p epochs int space 5 10 15 20`.",
)
@cluster_option
@command_option
@resource_option
@processor_option
@cpu_limit_option
@memory_limit_option
@gpu_type_option
@gpu_limit_option
@image_url_option
@vessl_option("--early-stopping-name", type=str, help="Early stopping algorithm name.")
@vessl_option(
    "--early-stopping-settings",
    type=click.Tuple([str, str]),
    multiple=True,
    help="Early stopping algorithm settings. Format: [key] [value], ex. `--early-stopping-settings start_step 4`.",
)
@message_option
@env_var_option
@dataset_option
@root_volume_size_option
@working_dir_option
@output_dir_option
@local_project_option
@organization_name_option
@project_name_option
def create(
    objective_type: str,
    objective_goal: str,
    objective_metric: str,
    num_experiments: int,
    num_parallel: int,
    num_failed: int,
    algorithm: str,
    parameter: List[Dict[str, Any]],
    cluster: str,
    command: str,
    resource: str,
    processor: str,
    cpu_limit: float,
    memory_limit: float,
    gpu_type: str,
    gpu_limit: int,
    image_url: str,
    early_stopping_name: str,
    early_stopping_settings: List[Tuple[str, str]],
    message: str,
    env_var: List[Tuple[str, str]],
    dataset: List[Tuple[str, str]],
    root_volume_size: str,
    working_dir: str,
    output_dir: str,
    local_project: str,
):
    sweep = create_sweep(
        objective_type=objective_type,
        objective_goal=objective_goal,
        objective_metric=objective_metric,
        max_experiment_count=num_experiments,
        parallel_experiment_count=num_parallel,
        max_failed_experiment_count=num_failed,
        algorithm=algorithm,
        parameters=parameter,
        cluster_name=cluster,
        start_command=command,
        kernel_resource_spec_name=resource,
        processor_type=processor,
        cpu_limit=cpu_limit,
        memory_limit=memory_limit,
        gpu_type=gpu_type,
        gpu_limit=gpu_limit,
        kernel_image_url=image_url,
        early_stopping_name=early_stopping_name,
        early_stopping_settings=early_stopping_settings,
        message=message,
        env_vars=env_var,
        dataset_mounts=dataset,
        root_volume_size=root_volume_size,
        working_dir=working_dir,
        output_dir=output_dir,
        local_project_url=local_project,
    )
    print(
        f"Created '{sweep.name}'.\n"
        f"For more info: {Endpoint.sweep.format(sweep.organization.name, sweep.project.name, sweep.name)}"
    )


@cli.vessl_command()
@vessl_argument("name", type=click.STRING, required=True, prompter=sweep_name_prompter)
@organization_name_option
@project_name_option
def terminate(name: str):
    sweep = terminate_sweep(sweep_name=name)
    print(
        f"Terminated '{sweep.name}'.\n"
        f"For more info: {Endpoint.sweep.format(sweep.organization.name, sweep.project.name, sweep.name)}"
    )


@cli.vessl_command()
@vessl_argument("name", type=click.STRING, required=True, prompter=sweep_name_prompter)
@click.option(
    "--tail",
    type=click.INT,
    default=200,
    help="Number of lines to display (from the end).",
)
@organization_name_option
@project_name_option
def logs(name: str, tail: int):
    logs = list_sweep_logs(sweep_name=name, limit=tail)
    print_logs(logs)
    print(f"Displayed last {len(logs)} lines of '{name}'.")
