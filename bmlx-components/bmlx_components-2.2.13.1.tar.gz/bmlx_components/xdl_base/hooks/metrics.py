import xdl
import datetime
import logging

from xdl.python.framework.session import Hook
from xdl.python.training.training_utils import get_global_step


class XdlMetricsHook(Hook):
    def __init__(
        self, ts_tensor, other_tensors, collect_interval, log_interval, sinker,
    ):
        super(XdlMetricsHook, self).__init__()
        self._names = []
        self._values = []
        self._collect_interval = collect_interval
        self._log_interval = log_interval
        self._ts_tensor = ts_tensor
        self._other_tensors = []
        self._sinker = sinker
        self._lstep = 0

        logging.info(
            "create metrics interval: %s, log_interval: %s"
            % (self._collect_interval, self._log_interval)
        )

        for val in xdl.get_all_metrics():
            self._names.append(val.name)
            self._values.append(val.value)

        for name, tensor in other_tensors:
            self._names.append(name)
            self._values.append(tensor)

    def _p95(self, ts_tensor_value, key=lambda x: x):
        return sorted(ts_tensor_value, key=key)[
            int(len(ts_tensor_value) * 0.95)
        ]

    def before_run(self, v):
        return [get_global_step().value] + [self._ts_tensor] + self._values

    def after_run(self, v):
        self._lstep += 1
        current_step, sample_ts_value = v[0], v[1]
        if len(sample_ts_value) == 0:
            return

        # anchored ts 为这批样本锚定的时间戳，选取95分位样本作为代表
        anchor_ts = self._p95(sample_ts_value).item()
        if int(anchor_ts) > 32503651200 or int(anchor_ts) <= 0:
            logging.warning("sample anchor timestamp %s is strange, out of range (AD 1900 - AD 3000)", str(anchor_ts))
        current_step = current_step.item()

        if self._sinker is not None and xdl.get_task_index() == 0:
            if self._collect_interval.reached_threshold(
                current_ts=anchor_ts, current_step=current_step
            ):
                self._sinker(
                    ts=datetime.datetime.now(),
                    metrics=zip(self._names, v[2:]),
                    sample_ts=anchor_ts,
                    step=current_step,
                )

        if self._log_interval.reached_threshold(
            current_ts=anchor_ts, current_step=current_step
        ):
            ts_str = ",".join(
                [
                    "%s:%s" % (name, value)
                    for name, value in zip(self._names, v[2:])
                ]
            )
            logging.info(
                "ts:%s, lstep:%d, gstep:%s, sample_ts:%d\t%s"
                % (
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%s"),
                    self._lstep,
                    current_step,
                    anchor_ts,
                    ts_str,
                )
            )

    def end(self):
        if self._sinker is not None:
            self._sinker.close()

class XdlEvalMetricsHook(XdlMetricsHook):
    def after_run(self, v):
        self._lstep += 1
        current_step, sample_ts_value = v[0], v[1]
        if len(sample_ts_value) == 0:
            return

        # anchored ts 为这批样本锚定的时间戳，选取95分位样本作为代表
        anchor_ts = self._p95(sample_ts_value).item()
        if int(anchor_ts) > 32503651200 or int(anchor_ts) <= 0:
            logging.warning("sample anchor timestamp %s is strange, out of range (AD 1900 - AD 3000)", str(anchor_ts))
        current_step = current_step.item()

        now_timestamp = int(datetime.datetime.now().timestamp())

        if self._sinker is not None and xdl.get_task_index() == 0:
            if self._collect_interval.reached_threshold(
                current_ts=now_timestamp, current_step=self._lstep
            ):
                self._sinker(
                    ts=datetime.datetime.now(),
                    metrics=zip(self._names, v[2:]),
                    sample_ts=anchor_ts,
                    step=current_step,
                )

        if self._log_interval.reached_threshold(
            current_ts=anchor_ts, current_step=current_step
        ):
            ts_str = ",".join(
                [
                    "%s:%s" % (name, value)
                    for name, value in zip(self._names, v[2:])
                ]
            )
            logging.info(
                "ts:%s, lstep:%d, gstep:%s, sample_ts:%d\t%s"
                % (
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%s"),
                    self._lstep,
                    current_step,
                    anchor_ts,
                    ts_str,
                )
            )