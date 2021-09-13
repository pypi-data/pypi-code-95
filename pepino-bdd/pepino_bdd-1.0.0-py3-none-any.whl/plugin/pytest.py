from pepino.definitions import Scenario
from typing import Callable, Optional, Sequence

from termcolor import colored
import pytest
from _pytest.capture import CaptureManager
from _pytest.terminal import TerminalReporter
from _pytest._code import ExceptionInfo
from _pytest.fixtures import FuncFixtureInfo, FixtureDef

from pepino.enums import Hook
from pepino.gherkin.definitions import GherkinFeature, GherkinScenario, GherkinRule, Step
from pepino.results import StepResult, Result
from pepino.registry import registry


class ProxyPyItem:

    def __init__(self, scenario: "ScenarioItem", step: Callable, py_class: Optional[type] ) -> None:
        self.scenario = scenario
        self.step = step
        self.py_class = py_class
        self.funcargs = {}

    @property
    def _fixtureinfo(self):
        return self.scenario.session._fixturemanager.getfixtureinfo(self.scenario, self.step, self.py_class, funcargs=True)  # noqa

    def __getattr__(self, name):
        return getattr(self.scenario, name)


class GherkinReporter:

    def __init__(self, reporter: TerminalReporter, capture_manager: CaptureManager) -> None:
        self._reporter = reporter
        self._capture_manager = capture_manager
        registry.add_hook(Hook.pre_scenario, self.log_pre_scenario)
        registry.add_hook(Hook.post_scenario, self.log_post_scenario)
        registry.add_hook(Hook.pre_step, self.log_pre_step)
        registry.add_hook(Hook.post_step, self.log_post_step)
        self.in_scenario = False

    def log_pre_scenario(self, scenario: Scenario):
        self._capture_manager.suspend()
        print(f"\n  {colored('Scenario:', attrs=['bold'])} {scenario.name}\n")  # noqa
        self._capture_manager.resume()
        self.in_scenario = True

    def log_post_scenario(self, _):
        self.in_scenario = False

    def log_pre_step(self, step: Step):
        if self.in_scenario:
            self._capture_manager.suspend()
            print(f"\t{step.keyword} {step.text}", end="\r")  # noqa
            self._capture_manager.resume()

    def log_post_step(self, step_result: StepResult):
        if self.in_scenario:
            self._capture_manager.suspend()
            result = "OK" if step_result.result == Result.PASSED else "FAILED"
            colour = "green" if step_result.result == Result.PASSED else "red"
            print(f"\t{colored(step_result.step.keyword, colour, attrs=['bold'])} {step_result.step.text} [{colored(result, colour, attrs=['bold'])}] ({step_result.duration.total_seconds():.2f})s")  # noqa
            self._capture_manager.resume()


class FeatureCollector(pytest.Collector):

    current_item: Optional["ScenarioItem"] = None

    def __init__(self, parent, fspath) -> None:
        super().__init__(fspath.basename, parent=parent)
        self.fspath = fspath

    def collect(self):
        with self.fspath.open() as fp:
            feature = GherkinFeature.from_string(fp.read())
            for rule in feature.rules:
                for scenario in rule.scenarios:
                    yield ScenarioItem.from_parent(self, feature=feature, scenario=scenario, rule=rule)
            for scenario in feature.scenarios:
                yield ScenarioItem.from_parent(self, feature=feature, scenario=scenario)

    @classmethod
    def set_current_item(cls, value):
        cls.current_item = value


class ScenarioItem(pytest.Item):

    def __init__(self, parent: FeatureCollector, feature: GherkinFeature, scenario: GherkinScenario, rule: Optional[GherkinRule] = None) -> None:
        if rule:
            name = f"{feature.name}/{rule.name}/{scenario.name}"
            nodeid = f"{feature.name}/{rule.name}::{scenario.name}"
        else:
            name = f"{feature.name}/{scenario.name}"
            nodeid = f"{feature.name}::{scenario.name}"
        super(ScenarioItem, self).__init__(name, parent, nodeid=nodeid)
        self.feature = feature
        self.scenario = scenario
        for tag in self.feature.tags:
            self.add_marker(tag)
        for tag in self.scenario.tags:
            self.add_marker(tag)
        if rule:
            for tag in rule.tags:
                self.add_marker(tag)
        self.rule = rule

    def runtest(self):
        self.parent.set_current_item(self)
        if self.feature.background:
            result = self.feature.background.execute()
            if result.exc_info:
                raise PepinoException(result.exc_info)
        result = self.scenario.execute()
        if result.exc_info:
            raise PepinoException(result.exc_info)

    def repr_failure(self, excinfo):
        if isinstance(excinfo.value, PepinoException):
            return self._repr_failure_py(ExceptionInfo.from_exc_info(excinfo.value.exc_info), "short")
        return self._repr_failure_py(excinfo, "short")

    def reportinfo(self):
        if self.rule:                 
            return f"{self.feature.name}::{self.rule.name}", self.scenario.line, "Scenario:: %s" % self.scenario.name
        return f"{self.feature.name}", self.scenario.line, "Scenario: %s" % self.scenario.name

    def get_fixture_info(self, func: Callable, cls: Optional[type]) -> FuncFixtureInfo:
        return self.session._fixturemanager.getfixtureinfo(self, func, cls, funcargs=True)  # noqa

    def get_fixture_defs(self, arg: str) -> Optional[Sequence[FixtureDef]]:
        return self.session._fixturemanager.getfixturedefs(arg, self.nodeid)  # noqa


class PepinoException(Exception):

    def __init__(self, exc_info):
        super(PepinoException, self).__init__()
        self.exc_info = exc_info
