import xdl
import json

from bmlx.utils import io_utils
from xdl.python.framework.session import Hook
from xdl.python.training.training_utils import get_global_step


class TimelineHook(Hook):
    def __init__(self, output_dir, interval_steps: int, total_count: int):
        super(TimelineHook, self).__init__()
        self._output_dir = output_dir
        self._run_option = xdl.RunOption()
        self._run_option.perf = True
        self._run_statistic = xdl.xdl.RunStatistic()
        self._interval_steps = interval_steps
        self._global_step = get_global_step()
        self._last_filter_step = 0
        self._gstep_val = 0
        self._timelines = []
        self._capacity = total_count
        self._has_dumped = False

    def run_option(self):
        return self._run_option

    def run_statistic(self):
        return self._run_statistic

    def before_run(self, v):
        return [self._global_step.value]

    def after_run(self, v):
        self._gstep_val = v[0] if isinstance(v, list) else v
        if self._last_filter_step == 0:
            self._last_filter_step = self._gstep_val
        if (
            self._gstep_val - self._last_filter_step >= self._interval_steps
            and len(self._timelines) < self._capacity
        ):
            self._timelines.append(
                xdl.Timeline(self._run_statistic.perf_result)
            )
            self._last_filter_step = self._gstep_val
        if len(self._timelines) >= self._capacity:
            self.dump_timeline()

    def dump_timeline(self):
        if self._has_dumped:
            return
        tl = []
        for t in self._timelines:
            data = json.loads(t.to_string())
            for e in data["traceEvents"]:
                tl.append(e)
        timelines = {"traceEvents": tl}

        fs, path = io_utils.resolve_filesystem_and_path(self._output_dir)

        with fs.open(path, "wb") as fd:
            fd.write(json.dumps(timelines).encode())

        self._has_dumped = True

    def end(self):
        self.dump_timeline()
