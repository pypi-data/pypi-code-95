import xdl
import tensorflow as tf
import random
import logging
import functools
import datetime

from typing import Dict, Text, List
from bmlx.flow import Artifact
from bmlx.utils import var_utils, import_utils, io_utils
from xdl.python.framework.session import Hook
from xdl.python.training.training_utils import get_global_step
from xdl.python.utils.config import get_app_id, get_task_index
from xdl.python.pybind import set_task_name, set_worker_id
from bmlx_components.xdl_base.runner import XdlRunner
from bmlx_components.xdl_base.model import ProcessResult
from bmlx_components.xdl_base.hooks import XdlEvalMetricsHook
from bmlx_components.xdl_base.interval import Interval


# 同时支持 xdl eval 和 xdl eval slots
class XdlEvalRunner(XdlRunner):
    def gen_metrics_hook(self, ts_tensor, additional_metrics=[]):
        log_interval = Interval.create_interval(
            step=self._parameters["log_interval"].as_number()
        )
        metrics_step_interval = self._parameters["metrics_interval"].as_number()
        metrics_step_interval_for_eval = None
        if "eval_metrics_interval" in self._parameters:
            try:
                metrics_step_interval_for_eval = self._parameters["eval_metrics_interval"].as_number()
                logging.info("[GenMetricsHook for Eval] metrics use eval_step_interval, is %s", metrics_step_interval_for_eval)
            except Exception as e:
                metrics_step_interval_for_eval = None
                logging.info(
                    "[GenMetricsHook for Eval] metrics use step_interval, is %s, due to eval_step_interval exception: %s",
                    metrics_step_interval_for_eval,
                    e
                )
        else:
            logging.info("[GenMetricsHook for Eval] metrics use step_interval, is %s", metrics_step_interval)
        collect_interval = (
            Interval.create_interval(step=metrics_step_interval_for_eval)
            if metrics_step_interval_for_eval is not None
            else Interval.create_interval(step=metrics_step_interval)
        )
        return [
            XdlEvalMetricsHook(
                ts_tensor=ts_tensor,
                other_tensors=additional_metrics,
                collect_interval=collect_interval,
                log_interval=log_interval,
                sinker=self._metrics_sinker,
            )
        ]

    def run(self, reader: xdl.DataReader, eval_slots=[]):
        batch = reader.read()
        app_id = get_app_id()
        if app_id is None:
            app_id = "xdl"
        app_id = app_id.replace('-', '_')
        set_task_name(app_id)
        logging.info("[EvalRunner] app_id is %s", app_id)
        worker_id = get_task_index()
        logging.info("[EvalRunner] worker_id is %s", worker_id)
        set_worker_id(worker_id)

        log_str = "gstep: [{0}], timestamp: [{1}]"
        global_step = get_global_step().value
        timestamp = xdl.max_value(batch["_timestamp"])
        log_tensors = [global_step, timestamp]

        train_ops = []
        hooks = []
        metric_tensors = []

        logging.info("xdl begin with phase %s" % self._parameters["phases"])

        # eval phase = 1
        if not eval_slots:  # 正常eval
            with xdl.model_scope("phase0"):
                ret = self._model.process(batch=batch, phase=0,)
        else:  # eval slots
            ret = ProcessResult()
            for slot in eval_slots:
                with xdl.model_scope("slot" + str(slot)):
                    partial_ret = self._model.process(
                        batch=batch, phase=0, eval_slot=slot
                    )
                    ret.append(partial_ret, f"slot_{slot}_")

        for name, tensor in ret.tensor_map.items():
            metric_tensors.append(("phase%s/%s" % (0, name), tensor))
            log_str += ", p%d_%s:{%d}" % (0, name, len(log_tensors))
            log_tensors.append(tensor)
            train_ops.append(tensor)

        if ret.additional_hooks:
            hooks.extend(ret.additional_hooks)

        # ts tensor
        ts_tensor = batch["_timestamp"]
        max_timestamp = xdl.max_value(ts_tensor)
        # add log hooks
        hooks.append(
            xdl.LoggerHook(
                log_tensors[:],
                log_str,
                interval=self._parameters["log_interval"].as_number(),
            )
        )
        # worker finish hook
        if not self._is_local:
            hooks.extend(self.gen_worker_finish_hook())

        hooks.extend(self.gen_save_metrics_hook(max_timestamp))

        # trace hook
        trace_hooks = self.gen_trace_hook()
        hooks.extend(trace_hooks)

        # metric hook
        hooks.extend(
            self.gen_metrics_hook(ts_tensor, additional_metrics=metric_tensors,)
        )

        # timeline hook
        timeline_hook = self.gen_timeline_hook()
        if timeline_hook:
            hooks.append(timeline_hook)

        sess = xdl.TrainSession(hooks=hooks)
        while not sess.should_stop():
            if timeline_hook:
                run_option = timeline_hook.run_option()
                run_option.timeout_second = self._parameters[
                    "timeout"
                ].as_number()
                sess.run(
                    train_ops,
                    run_option=run_option,
                    run_statistic=timeline_hook.run_statistic(),
                )
            else:
                run_option = xdl.RunOption()
                run_option.timeout_second = self._parameters[
                    "timeout"
                ].as_number()
                sess.run(train_ops, run_option=run_option)
