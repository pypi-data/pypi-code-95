import abc
import datetime
from functools import partial
import sys
from typing import List, Optional, Tuple, Callable, Dict, Type

from .enums import Hook, Result
from .exceptions import CucumberStepException
from .registry import registry
from .results import BackgroundResult, StepResult, ScenarioResult, FeatureResult, RuleResult


class Step(metaclass=abc.ABCMeta):

    @property
    def result_cls(self) -> Type[StepResult]:
        return StepResult

    @abc.abstractproperty
    def keyword(self) -> str:
        ...

    @abc.abstractproperty
    def text(self) -> str:
        ...

    @abc.abstractproperty
    def function(self) -> Callable:
        ...

    @abc.abstractproperty
    def kwargs(self) -> Dict:
        ...

    @abc.abstractproperty
    def args(self) -> Tuple:
        ...

    @abc.abstractproperty
    def location(self) -> str:
        ...

    def execute(self) -> StepResult:
        registry.run_hooks(Hook.pre_step, self)
        result = self.result_cls(self)
        result.start = datetime.datetime.now()
        result.result = Result.RUNNING
        try:
            func = self.function
            try:
                step_func = partial(func, *self.args, **self.kwargs)
                #step_func()
                registry.run_hooks(Hook.call_step, step_func)()
                result.result = Result.PASSED
            except Exception as e:
                raise CucumberStepException(self.text, self.location) from e
        except Exception:
            result.result = Result.FAILED
            result.exc_info = sys.exc_info()  # type: ignore
        result.stop = datetime.datetime.now()
        result.duration = result.stop - result.start
        registry.run_hooks(Hook.post_step, result)
        return result


class Background(metaclass=abc.ABCMeta):

    @property
    def result_cls(self) -> Type[BackgroundResult]:
        return BackgroundResult

    @abc.abstractproperty
    def name(self) -> str:
        ...

    @abc.abstractproperty
    def steps(self) -> List[Step]:
        ...

    def execute(self) -> BackgroundResult:
        registry.run_hooks(Hook.pre_background, self)
        result = self.result_cls(len(self.steps))
        for step in self.steps:
            step_result = step.execute()
            result.results.append(step_result)
            if step_result.result == Result.FAILED:
                break
        registry.run_hooks(Hook.post_background, result)
        return result


class Scenario(metaclass=abc.ABCMeta):

    @property
    def result_cls(self) -> Type[ScenarioResult]:
        return ScenarioResult

    @abc.abstractproperty
    def name(self) -> str:
        ...

    @property
    def tags(self) -> List[str]:
        ...

    @abc.abstractproperty
    def steps(self) -> List[Step]:
        ...

    def execute(self) -> ScenarioResult:
        registry.run_hooks(Hook.pre_scenario, self)
        result = self.result_cls(len(self.steps))
        for step in self.steps:
            step_result = step.execute()
            result.results.append(step_result)
            if step_result.result == Result.FAILED:
                break
        registry.run_hooks(Hook.post_scenario, result)
        return result


class Rule(metaclass=abc.ABCMeta):

    @property
    def result_cls(self) -> Type[RuleResult]:
        return RuleResult

    @abc.abstractproperty
    def name(self) -> str:
        ...

    @abc.abstractproperty
    def description(self) -> str:
        ...

    @abc.abstractproperty
    def tags(self) -> List[str]:
        ...

    @abc.abstractproperty
    def scenarios(self) -> List[Scenario]:
        ...

    def execute(self, background: Optional[Background]) -> RuleResult:
        registry.run_hooks(Hook.pre_rule, self)
        expected = len(self.scenarios) * 2 if background else len(self.scenarios)
        result = self.result_cls(expected)
        for child in self.scenarios:
            if background:
                bresult = background.execute()
                result.results.append(bresult)
                if bresult.result == Result.FAILED:
                    continue
            result.results.append(child.execute())
        registry.run_hooks(Hook.post_rule, result)
        return result


class Feature(metaclass=abc.ABCMeta):

    @property
    def result_cls(self) -> Type[FeatureResult]:
        return FeatureResult

    @abc.abstractproperty
    def name(self) -> str:
        ...

    @abc.abstractproperty
    def description(self) -> str:
        ...

    @abc.abstractproperty
    def tags(self) -> List[str]:
        ...

    @abc.abstractproperty
    def background(self) -> Optional[Background]:
        ...

    @abc.abstractproperty
    def rules(self) -> List[Rule]:
        ...

    @abc.abstractproperty
    def scenarios(self) -> List[Scenario]:
        ...

    def execute(self) -> FeatureResult:
        registry.run_hooks(Hook.pre_feature, self)
        expected = len(self.scenarios) * 2 if self.background else len(self.scenarios)
        expected += len(self.rules)
        result = self.result_cls(expected)
        for rule in self.rules:
            result.results.extend(rule.execute(self.background).results)
        for child in self.scenarios:
            if self.background:
                bresult = self.background.execute()
                result.results.append(bresult)
                if bresult.result == Result.FAILED:
                    continue
            result.results.append(child.execute())
        registry.run_hooks(Hook.post_feature, result)
        return result
