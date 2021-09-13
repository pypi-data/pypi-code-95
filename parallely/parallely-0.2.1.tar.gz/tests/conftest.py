import pytest


@pytest.fixture(scope="session", autouse=True)
def single_arg():
    def inner(a):
        return a

    return inner


@pytest.fixture(scope="session", autouse=True)
def multi_kwarg():
    def inner(a, b):
        return a + b

    return inner


@pytest.fixture(scope="session", autouse=True)
def single_arg_async():
    async def inner(a):
        return a

    return inner


@pytest.fixture(scope="session", autouse=True)
def multi_kwarg_async():
    async def inner(a, b):
        return a + b

    return inner
