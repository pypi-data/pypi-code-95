import enum
import datetime


class IntervalChoice(enum.Enum):
    BY_TIME = 0
    BY_STEP = 1


class Interval:
    _interval_type: IntervalChoice = None
    _interval_value: int = None

    _last_value = None

    @property
    def interval_type(self):
        return self._interval_type

    @property
    def interval_value(self):
        return self._interval_value

    @classmethod
    def create_interval(cls, step=None, time=None):
        assert bool(step) != bool(time), "could only as time or step interval"
        if step:
            r = Interval()
            r._interval_type = IntervalChoice.BY_STEP
            r._interval_value = step
            r._last_value = 0
        else:
            r = Interval()
            r._interval_type = IntervalChoice.BY_TIME
            r._interval_value = time
            r._last_value = 0
        return r

    def reached_threshold(self, current_ts=None, current_step=None, reset=True) -> bool:
        if self.interval_type == IntervalChoice.BY_TIME:
            if self._last_value + self.interval_value <= current_ts:
                if reset:
                    self._last_value = current_ts
                return True
        elif self.interval_type == IntervalChoice.BY_STEP:
            if self._last_value + self.interval_value <= current_step:
                if reset:
                    self._last_value = current_step
                return True
        return False

    def __str__(self):
        return "Interval %s : %s" % (
            "step" if self.interval_type == IntervalChoice.BY_STEP else "time",
            self.interval_value
        )
