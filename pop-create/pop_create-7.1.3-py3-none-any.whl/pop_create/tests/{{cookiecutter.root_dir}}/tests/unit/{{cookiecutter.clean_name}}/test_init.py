def test_cli(mock_hub, hub):
    mock_hub.{{cookiecutter.clean_name}}.init.cli = hub.{{cookiecutter.clean_name}}.init.cli
    mock_hub.{{cookiecutter.clean_name}}.init.cli()
    mock_hub.pop.config.load.assert_called_once_with(
        ["{{cookiecutter.clean_name}}"], "{{cookiecutter.clean_name}}"
    )
