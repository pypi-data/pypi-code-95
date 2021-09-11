from subprocess import STDOUT, CalledProcessError, call, check_output

from behave import given, then, when


@given("there is a config file with {tool} config")
def step_impl(context, tool):
    context.tool = tool
    call(
        context.docker_command
        + [
            "exec",
            "shell",
            "cp",
            context.examples_path / context.tool / "kvack.toml",
            context.output_path / "pyproject.toml",
        ]
    )


@when("I run 'kvack gen' in shell")
def step_impl(context):  # noqa
    try:
        output = check_output(
            context.docker_command
            + ["exec", "-w", str(context.output_path), "shell", "kvack", "gen"],
            stderr=STDOUT,
        )
    except CalledProcessError as exception:
        output = exception.output

    str_output = output.decode("utf-8").strip()
    assert str_output == f"Tool configs generated: {context.tool}", str_output


@then("Black configuration file should be generated")
def step_impl(context):  # noqa
    pyproject = check_output(
        context.docker_command
        + ["exec", "-w", str(context.output_path), "shell", "cat", "pyproject.toml"]
    )

    expected = check_output(
        context.docker_command
        + [
            "exec",
            "shell",
            "cat",
            str(context.examples_path / context.tool / "expected.toml"),
        ]
    )

    print(pyproject)
    print(expected)
    assert pyproject == expected, (pyproject, expected)
