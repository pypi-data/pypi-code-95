from functools import partial
from typing import Optional

import pytest
from _pytest.terminal import TerminalReporter
from _pytest.fixtures import FixtureRequest, pytest_fixture_setup, SubRequest

from pepino.enums import Hook
from pepino.registry import registry

from .pytest import GherkinReporter, FeatureCollector, ProxyPyItem

@pytest.mark.trylast
def pytest_configure(config):
    reporter = config.pluginmanager.getplugin("terminalreporter")
    capture = config.pluginmanager.getplugin("capturemanager")
    registry.add_hook(Hook.call_step, pre_step)
    if config.option.verbose and isinstance(reporter, TerminalReporter):
        GherkinReporter(reporter=reporter, capture_manager=capture)
    registry.load_from_path("tests/.*steps.py$")


def pre_step(step: partial):
    pytest_cls = type(step.args[0]) if len(step.args) > 0 else None
    feature_item = FeatureCollector.current_item
    if feature_item:
        proxy = ProxyPyItem(feature_item, step, pytest_cls)
        request = FixtureRequest(proxy, _ispytest=True)
        fixture_info = feature_item.get_fixture_info(step, pytest_cls)
        kwargs = {}
        for idx, arg in enumerate(fixture_info.argnames):
            fixture_defs = feature_item.get_fixture_defs(arg)
            if fixture_defs:
                fixture_def = fixture_defs[-1]
                subrequest = SubRequest(request, fixture_def.scope, arg, idx, fixture_def,  _ispytest=True)
                kwargs[arg] = pytest_fixture_setup(fixture_def, subrequest)

        return partial(step, **kwargs)
    return step


def pytest_collect_file(path, parent) -> Optional[FeatureCollector]:
    if path.ext == ".feature":
        return FeatureCollector.from_parent(parent, fspath=path)
    return None
