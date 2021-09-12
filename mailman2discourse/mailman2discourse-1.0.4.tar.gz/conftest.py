def pytest_addoption(parser):
    parser.addoption(
        "--discourse",
        required=True,
        help="coma separated list of discourse versions v2.8.0,v2.7.8"
    )


#
# https://docs.pytest.org/en/stable/example/parametrize.html
#
def pytest_generate_tests(metafunc):
    if "version" in metafunc.fixturenames:
        versions = metafunc.config.getoption("discourse").split(',')
        metafunc.parametrize("version", versions)
