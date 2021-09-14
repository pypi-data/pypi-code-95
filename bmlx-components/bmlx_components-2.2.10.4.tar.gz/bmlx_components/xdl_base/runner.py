import xdl
import tensorflow as tf
import numpy as np
import random
import logging
import functools
import datetime

from typing import Dict, Text, List
from bmlx_components.proto import schema_pb2
from bmlx.flow import Artifact
from bmlx.utils import var_utils, import_utils, io_utils
from xdl.python.framework.session import Hook
from xdl.python.training.training_utils import get_global_step
from xdl.python.pybind import set_task_name, set_worker_id
from xdl.python.utils.config import get_app_id, get_task_index
from bmlx_components.xdl_base.hooks import (
    TimelineHook,
    XdlMetricsHook,
    KafkaTimestampHook,
    PulsarTimestampHook,
    SaveMetricsHook,
    TraceHook,
)
from bmlx_components.xdl_base.interval import Interval
from xdl.python.sparse_engine.embedding import (
    _EMBEDDING_SLOT_UPDATERS,
    _EMBEDDING_DECAY,
    _EMBEDDING_SCORE_FILTER,
    _EMBEDDING_STEP_FILTER,
    _EMBEDDING_TIMESTAMP_FILTER,
    EMBEDDING_INFOS,
)
from xdl.python.training.trace import trace_collection


class XdlRunner(object):
    def __init__(
        self,
        model_module,
        parameters,
        schema,
        stage,
        is_training,
        is_local=False,
        model_version="",
        metrics_sinker=None,
    ):
        self._parameters = parameters
        self._schema = schema
        self._stage = stage
        self._is_training = is_training
        self._is_local = is_local
        self._model_version = model_version
        self._metrics_sinker = metrics_sinker

        self._model = import_utils.import_class_by_path(model_module)(
            parameters, schema, stage, is_training
        )

        if not self._model:
            raise RuntimeError(
                "Failed to import model by module name %s" % model_module
            )

        if is_training and not model_version:
            raise RuntimeError("train mode must set model_version")

    def gen_hash_slots_update_hook(self):
        update_dict = _EMBEDDING_SLOT_UPDATERS
        hooks = []
        for k, v in update_dict.items():
            v.sort()
            slot_names = [elem.slot_name for elem in v]
            updaters = [elem.updater for elem in v]
            slot_values = [elem.slot_value for elem in v]
            hooks.append(
                xdl.HashSlotsUpdateHook(
                    var_name=k.emb_name,
                    slot_names=slot_names,
                    ids=k.unique_ids,
                    updaters=updaters,
                    slot_values=slot_values,
                )
            )
        return hooks

    def gen_global_step_filter_hook(self):
        filter_dict = _EMBEDDING_STEP_FILTER
        hooks = []
        if xdl.get_task_index() != 0:
            return hooks
        interval_dict = {}
        for name, info in filter_dict.items():
            interval = int(info["interval_steps"])
            threshold = int(info["threshold"])
            interval_dict.setdefault(interval, [[], []])
            interval_dict[interval][0].append(name)
            interval_dict[interval][1].append(threshold)
        for interval, lists in interval_dict.items():
            hooks.append(
                xdl.GlobalStepFilterHookV2(lists[0], lists[1], interval)
            )
        return hooks

    def gen_timestamp_filter_hook(self):
        filter_dict = _EMBEDDING_TIMESTAMP_FILTER
        hooks = []
        if xdl.get_task_index() != 0:
            return hooks
        interval_dict = {}
        for name, info in filter_dict.items():
            interval = info["interval_hours"]
            threshold = info["threshold"]
            interval_dict.setdefault(interval, [[], []])
            interval_dict[interval][0].append(name)
            interval_dict[interval][1].append(threshold)
        for interval, lists in interval_dict.items():
            hooks.append(
                xdl.TimestampFilterHook(lists[0], lists[1], interval)
            )
        return hooks

    def gen_hash_feature_decay_hook(self):
        decay_dict = _EMBEDDING_DECAY
        hooks = []
        interval_dict = {}
        if xdl.get_task_index() != 0:
            return hooks
        for key, info in decay_dict.items():
            if info["decay_interval_hours"] is not None:
                interval_key = "decay_interval_hours"
            else:
                interval_key = "decay_interval_steps"
            break
        for key, info in decay_dict.items():
            emb_name = key.emb_name
            slot_name = key.slot_name
            decay_rate = info["decay_rate"]
            interval = info[interval_key]
            interval_dict.setdefault(interval, {})
            interval_dict[interval].setdefault(
                emb_name, xdl.VarDecay(emb_name, [], [])
            )
            interval_dict[interval][emb_name].slot_list.append(slot_name)
            interval_dict[interval][emb_name].decay_rate_list.append(decay_rate)
        for interval, vars in interval_dict.items():
            var_decay_list = []
            for key, var_decay in vars.items():
                var_decay_list.append(var_decay)

            if interval_key == "decay_interval_hours":
                hooks.append(
                    xdl.HashFeatureDecayHook(
                        var_decay_list,
                        interval_hours=interval,
                    )
                )
            else:
                hooks.append(
                    xdl.HashFeatureDecayHook(
                        var_decay_list, interval_steps=interval
                    )
                )
        return hooks

    def gen_hash_feature_score_filter_hook(self):
        filter_dict = _EMBEDDING_SCORE_FILTER
        hooks = []
        if xdl.get_task_index() != 0:
            return hooks
        interval_dict = {}
        for name, info in filter_dict.items():
            if info["interval_hours"] is not None:
                interval_key = "interval_hours"
            else:
                interval_key = "interval_steps"
            break
        for name, info in filter_dict.items():
            interval = info[interval_key]
            nonclk_weight = float(info["nonclk_weight"])
            clk_weight = float(info["clk_weight"])
            threshold = float(info["threshold"])
            interval_dict.setdefault(interval, [[], [], [], []])
            interval_dict[interval][0].append(name)
            interval_dict[interval][1].append(nonclk_weight)
            interval_dict[interval][2].append(clk_weight)
            interval_dict[interval][3].append(threshold)
        for interval, lists in interval_dict.items():
            if interval_key == "interval_hours":
                hooks.append(
                    xdl.HashFeatureScoreFilterHook(
                        lists[0],
                        lists[1],
                        lists[2],
                        lists[3],
                        interval_hours=interval,
                    )
                )
            else:
                hooks.append(
                    xdl.HashFeatureScoreFilterHook(
                        lists[0],
                        lists[1],
                        lists[2],
                        lists[3],
                        interval_steps=interval,
                    )
                )
        return hooks

    def gen_worker_finish_hook(self):
        finish_rate = self._parameters["min_finish_worker_rate"].as_number()
        return [
            xdl.WorkerFinishHook(
                xdl.get_task_index()
            )
        ]

    def gen_checkpoint_hook(self):
        if xdl.get_task_index() != 0:
            return []

        if self._parameters["hooks"]["checkpoint"].exists():
            conf = self._parameters["hooks"]["checkpoint"]
            interval_steps = conf["interval_steps"].as_number()
            interval_hours = conf["interval_hours"].as_number()
            return [
                xdl.CheckpointHook(
                    interval_steps=interval_steps,
                    interval_hours=interval_hours,
                    end_version=self._model_version,
                )
            ]
        else:
            return []

    def gen_vars_sync_hook(self):
        if self._parameters["hooks"]["var_sync"].exists(use_default=False):
            conf = self._parameters["hooks"]["var_sync"]
            interval_steps = conf["interval_steps"].as_number()
            interval_hours = conf["interval_hours"].as_number()
            rules = conf["rules"].as_str()
            index = xdl.get_task_index()

            if index != 0:
                return []
            else:
                return [
                    xdl.VariableSyncChiefHook(
                        rules=rules,
                        interval_steps=interval_steps,
                        interval_hours=interval_hours,
                    )
                ]
        else:
            return []

    def gen_metrics_hook(self, ts_tensor, additional_metrics=[]):
        log_interval = Interval.create_interval(
            step=self._parameters["log_interval"].as_number()
        )
        metrics_step_interval = self._parameters["metrics_interval"].as_number()
        logging.info("[GenMetricsHook] metrics use step_interval, is %s", metrics_step_interval)
        collect_interval = (
            Interval.create_interval(step=metrics_step_interval)
        )
        return [
            XdlMetricsHook(
                ts_tensor=ts_tensor,
                other_tensors=additional_metrics,
                collect_interval=collect_interval,
                log_interval=log_interval,
                sinker=self._metrics_sinker,
            )
        ]

    def gen_save_metrics_hook(self, ts_tensor):
        metrics = xdl.get_all_metrics()
        if (
            xdl.get_task_index() != 0
            or not metrics
            or not self._parameters["hooks"]["save_metrics"].exists()
        ):
            return []
        interval_steps = self._parameters["hooks"]["save_metrics"][
            "interval_steps"
        ].as_number(1000)
        output_file_path = self._parameters["hooks"]["save_metrics"][
            "output_file_path"
        ].as_str()
        return [
            SaveMetricsHook(
                metrics=metrics,
                output_file_path=output_file_path,
                interval_steps=interval_steps,
                ts_tensor=ts_tensor,
            )
        ]

    def gen_timeline_hook(self):
        if self._parameters["hooks"]["timeline"].exists(use_default=False):
            hook_config = self._parameters["hooks"]["timeline"]
            interval = hook_config["interval"].as_number()
            worker_list = hook_config["worker_list"].as_str_seq()
            total_count = hook_config["total_count"].as_number()
            output_dir = hook_config["output_dir"].as_filename(
                relative_to="artifacts"
            )

            if str(xdl.get_task_index()) in worker_list:
                return TimelineHook(interval, total_count, output_dir)
        return None

    def gen_trace_hook(self):
        if self._parameters["hooks"]["trace"].exists(use_default=False):
            hc = self._parameters["hooks"]["trace"]
            if not hc:
                return []

            c = {
                "output_dir": hc["output_dir"].as_str(),
                "max_file_m_size": hc["max_file_m_size"].as_number(100),
                "output_file_name": hc["output_file_name"].as_str(),
                "log_type": hc["format"].as_str("pb"),
            }
            scope_list = []
            from xdl.python.backend.model_scope import get_model_scopes

            for scope in list(get_model_scopes()):
                if scope and not scope.startswith("tf_export_graph_scope"):
                    scope_list.append(scope)

            logging.info("trace generated to %s, scopes: %s", c, scope_list)
            return [
                TraceHook(c, is_training=self._is_training, scope=scope_list)
            ]
        return []

    def gen_kafka_timestamp_hook(self, data_io, ts_tensor):
        if data_io.is_kafka():
            return [KafkaTimestampHook(data_io, ts_tensor)]
        return []

    def gen_pulsar_timestamp_hook(self, data_io, ts_tensor, data_path):
        if data_io.is_pulsar():
            return [PulsarTimestampHook(data_io, ts_tensor, data_path)]
        return []

    def run(self, reader: xdl.DataReader):
        batch = reader.read()
        app_id = get_app_id()
        if app_id is None:
            app_id = "xdl"
        app_id = app_id.replace('-', '_')
        set_task_name(app_id)
        logging.info("[Runner] app_id is %s", app_id)
        worker_id = get_task_index()
        logging.info("[Runner] worker_id is %s", worker_id)
        set_worker_id(worker_id)

        log_str = "gstep: [{0}], timestamp: [{1}]"
        global_step = get_global_step().value
        timestamp = xdl.max_value(batch["_timestamp"])
        log_tensors = [global_step, timestamp]

        train_ops = []
        hooks = []
        metric_tensors = []

        first_global_optimizer = True
        logging.info("xdl begin with phase %s" % self._parameters["phases"])
        for phase in range(self._parameters["phases"].as_number(2)):
            with xdl.model_scope("phase%s" % phase):
                ret = self._model.process(
                    batch=batch,
                    phase=phase,
                )

                for name, tensor in ret.tensor_map.items():
                    metric_tensors.append(
                        ("phase%s/%s" % (phase, name), tensor)
                    )
                    log_str += ", p%d_%s:{%d}" % (phase, name, len(log_tensors))
                    log_tensors.append(tensor)
                    train_ops.append(tensor)

                if ret.additional_hooks:
                    hooks.extend(ret.additional_hooks)

                if self._is_training:
                    # append optimizers
                    optimizer = self._model.get_optimizer()
                    optvar = optimizer.optimize(
                        update_global_step=first_global_optimizer
                    )
                    first_global_optimizer = False
                    train_ops.append(optvar)

                    # update xdl ops
                    update_ops = xdl.get_collection(xdl.UPDATE_OPS)
                    if update_ops is not None:
                        train_ops.extend(update_ops)

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

        # only for training
        if self._is_training:
            hooks.extend(self.gen_kafka_timestamp_hook(reader, ts_tensor))
            hooks.extend(self.gen_hash_slots_update_hook())
            hooks.extend(self.gen_global_step_filter_hook())
            hooks.extend(self.gen_timestamp_filter_hook())
            hooks.extend(self.gen_hash_feature_decay_hook())
            hooks.extend(self.gen_hash_feature_score_filter_hook())
            hooks.extend(self.gen_checkpoint_hook())
            if not self._is_local:
                hooks.extend(self.gen_vars_sync_hook())

        hooks.extend(self.gen_save_metrics_hook(max_timestamp))

        # trace hook
        trace_hooks = self.gen_trace_hook()
        hooks.extend(trace_hooks)
        if trace_hooks and self._stage in ("predict"):
            # trace embedding 信息，embedding trace 帮助排查得分不一致原因
            xdl.trace_collection(EMBEDDING_INFOS, scope="")

        # metric hook
        hooks.extend(
            self.gen_metrics_hook(
                ts_tensor,
                additional_metrics=metric_tensors,
            )
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