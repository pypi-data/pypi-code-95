from unittest import mock
import pytest

@pytest.fixture(scope="session", name="hub")
def integration_hub(hub):
    for dyne in {{ cookiecutter.short_dyne_list if cookiecutter.vertical else cookiecutter.dyne_list }}:
        hub.pop.sub.add(dyne_name=dyne)

    with mock.patch("sys.argv", ["{{cookiecutter.get('entrypoint', cookiecutter.clean_name)}}"]):
        hub.pop.config.load(
            {{ cookiecutter.short_dyne_list if cookiecutter.vertical else cookiecutter.dyne_list }},
            cli="{{ cookiecutter.clean_name }}"
        )

    yield hub


async def _setup_hub(hub):
    # Set up the hub before each function here
    ...

async def _teardown_hub(hub):
    # Clean up the hub after each function here
    ...

@pytest.fixture(scope="function", autouse=True)
async def function_hub_wrapper(hub):
    await _setup_hub(hub)
    yield
    await _teardown_hub(hub)
