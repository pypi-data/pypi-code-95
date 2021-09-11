import os.path
from pathlib import Path
from subprocess import call, check_output, run
from time import sleep


def before_all(context):
    context.examples_path = Path("/code/tests/e2e/examples")
    context.local_exmples_path = Path(
        os.path.abspath(str(context.examples_path).replace("/code/", "./"))
    )
    context.docker_command = [
        "docker-compose",
        "-f",
        "tests/e2e/docker/docker-compose.yml",
    ]
    call(context.docker_command + ["up", "-d"])
    result = 1
    for _ in range(10):
        result = run(
            context.docker_command + ["exec", "shell", "kvack"], capture_output=True
        ).returncode
        if not result:
            break
        sleep(1)


# def after_all(context):
#     call(context.docker_command + ["down"])


def before_scenario(context, scenario):
    output_dir = check_output(
        context.docker_command
        + ["exec", "shell", "mktemp", "-d", "-p", "/code/tests/e2e/docker/output/"]
    )
    output_dir = output_dir.decode("utf-8")
    context.output_path = Path(output_dir.strip())
    context.local_output_path = Path(
        os.path.abspath(str(context.output_path).replace("/code/", "./"))
    )


# def after_scenario(context, scenario):
#     output_dir = check_output(
#         context.docker_command + ["exec", "shell", "rm", "-r", context.output_path]
#     )
