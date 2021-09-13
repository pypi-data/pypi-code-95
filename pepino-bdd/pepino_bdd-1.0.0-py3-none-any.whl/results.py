import abc
from datetime import datetime, timedelta
from typing import Optional, Tuple, List
from .enums import Result


class StepResult:

    def __init__(self, step):
        self._result = Result.NOT_RUN
        self._start: Optional[datetime] = None
        self._stop: Optional[datetime] = None
        self._duration: Optional[timedelta] = None
        self._exc_info: Optional[Tuple[object, BaseException, List]] = None
        self.step = step

    @property
    def result(self) -> Result:
        return self._result

    @result.setter
    def result(self, value: Result):
        self._result = value

    @property
    def start(self) -> Optional[datetime]:
        return self._start

    @start.setter
    def start(self, value: datetime):
        self._start = value

    @property
    def stop(self) -> Optional[datetime]:
        return self._stop

    @stop.setter
    def stop(self, value: datetime):
        self._stop = value

    @property
    def duration(self) -> Optional[timedelta]:
        return self._duration

    @duration.setter
    def duration(self, value: timedelta):
        self._duration = value

    @property
    def exc_info(self) -> Optional[Tuple[object, BaseException, List]]:
        return self ._exc_info

    @exc_info.setter
    def exc_info(self, value: Optional[Tuple[object, BaseException, List]]):
        self._exc_info = value


class AbstractStepContainerResult(metaclass=abc.ABCMeta):

    def __init__(self, expected_steps: int):
        self._expected_steps = expected_steps
        self.results: List[StepResult] = []

    @property
    def result(self) -> Result:
        if not self.results:
            return Result.PENDING
        elif self.results[-1].result == Result.FAILED:
            return Result.FAILED
        elif len(self.results) < self._expected_steps:
            return Result.RUNNING
        return Result.PASSED

    @property
    def start(self) -> Optional[datetime]:
        if len(self.results) > 0:
            return self.results[0].start
        return None

    @property
    def stop(self) -> Optional[datetime]:
        if len(self.results) > 0:
            return self.results[-1].stop
        return None

    @property
    def duration(self) -> Optional[timedelta]:
        if len(self.results) > 0 and self.results[-1].stop and self.results[0].start:
            return self.results[-1].stop - self.results[0].start
        return None

    @property
    def exc_info(self) -> Optional[Tuple[object, BaseException, List]]:
        if len(self.results) > 0:
            return self.results[-1].exc_info
        return None


class BackgroundResult(AbstractStepContainerResult):

    ...


class ScenarioResult(AbstractStepContainerResult):
    ...


class AbsractScenarioContainerResult(metaclass=abc.ABCMeta):

    def __init__(self, expected: int) -> None:
        self.expected = expected
        self.results: List[AbstractStepContainerResult] = []

    def result(self) -> Result:
        if not self.results:
            return Result.PENDING
        elif self.results[-1] == Result.FAILED:
            return Result.FAILED
        elif len(self.results) < self.expected:
            return Result.RUNNING
        return Result.PASSED

    @property
    def start(self) -> Optional[datetime]:
        if len(self.results) > 0:
            return self.results[0].start
        return None

    @property
    def stop(self) -> Optional[datetime]:
        if len(self.results) > 0:
            return self.results[-1].stop
        return None

    @property
    def duration(self) -> Optional[timedelta]:
        if len(self.results) > 0 and self.results[-1].stop and self.results[0].start:
            return self.results[-1].stop - self.results[0].start
        return None

    @property
    def exc_info(self) -> List[Tuple[object, BaseException, List]]:
        return [result.exc_info for result in self.results if result.exc_info]


class RuleResult(AbsractScenarioContainerResult):
    ...


class FeatureResult(AbsractScenarioContainerResult):
    ...
