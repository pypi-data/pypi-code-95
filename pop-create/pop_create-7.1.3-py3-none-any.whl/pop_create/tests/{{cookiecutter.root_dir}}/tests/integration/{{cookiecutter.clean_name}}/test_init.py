from unittest import mock


def test_cli(hub):
    with mock.patch("sys.argv", ["{{cookiecutter.project_name}}"]):
        hub.{{cookiecutter.clean_name}}.init.cli()
