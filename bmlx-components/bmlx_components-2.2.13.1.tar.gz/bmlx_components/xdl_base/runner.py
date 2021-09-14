import xdl, sys
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
from xdl.python.sparse_engine.embedding import (
    _EMBEDDING_SLOT_UPDATERS,
    _EMBEDDING_DECAY,
    _EMBEDDING_SCORE_FILTER,
    _EMBEDDING_STEP_FILTER,
    _EMBEDDING_TIMESTAMP_FILTER,
    _EMBEDDING_INFO,
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
        is_save_ckpt,
        is_local=False,
        model_version="",
        metrics_sinker=None,
    ):
        # set for prometheus metric 
        appId = xdl.get_app_id()
        if appId is None:
            appId = "xdl"
        appId = appId.replace("-", '_')
        set_task_name(appId)
        set_worker_id(get_task_index())

        self._parameters = parameters
        self._schema = schema
        self._stage = stage
        self._is_training = is_training
        self._is_save_ckpt = is_save_ckpt
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

        if is_save_ckpt and not model_version:
            raise RuntimeError("saving ckpt must set model_version")
 
    def gen_kafka_timestamp_hook(self, data_io, ts_tensor):
        if data_io.is_kafka():
            from xdl.python.training.hook_utils import KafkaTimestampHook
            return [KafkaTimestampHook(data_io, ts_tensor)]
        return []

    def gen_pulsar_timestamp_hook(self, data_io, ts_tensor):
        if data_io.is_pulsar():
            from xdl.python.training.hook_utils import PulsarTimestampHook
            return [PulsarTimestampHook(data_io, ts_tensor)]
        return []

    def gen_max_timestamp_hook(self, ts_tensor):
        from xdl.python.training.hook_utils import MaxTimestampHook
        return MaxTimestampHook(ts_tensor)

    def gen_save_metrics(self, ts_tensor):
        metrics = xdl.get_all_metrics()
        if not self._parameters["hooks"]["save_metrics"].exists() or len(metrics) == 0:
            return []
        conf = self._parameters["hooks"]["save_metrics"].flatten()
        print("conf: ", conf, flush=True)
        from xdl.python.training.train_session import SaveMetricsHook
        return [SaveMetricsHook(metrics, conf, xdl.get_task_index(), ts_tensor)]

    def gen_record_metrics_to_prometheus(self, ts_tensor):
        from xdl.python.training.train_session import SavePromethusHook
        metrics = xdl.get_user_metrics_to_prometheus()
        return SavePromethusHook(metrics, ts_tensor)

    def gen_timeline_hook(self):
        if self._parameters["hooks"]["timeline"].exists(use_default=False):
            hook_config = self._parameters["hooks"]["timeline"]
            interval = hook_config["interval_steps"].as_number()
            worker_list = hook_config["worker_list"].as_str_seq()
            total_count = hook_config["total_count"].as_number()
            output_dir = hook_config["output_dir"].as_filename(
                relative_to="artifacts"
            )
            if str(xdl.get_task_index()) in worker_list:
                from xdl.python.training.hook_utils import TimelineHook
                return TimelineHook(interval, total_count, output_dir)
        return None

    def gen_trace_hook(self):
        if self._parameters["hooks"]["trace"].exists(use_default=False):
            hc = self._parameters["hooks"]["trace"]
            if not hc:
                return []

            c = {
                "output_dir": hc["output_dir"].as_str(),
                "max_file_m_size": hc["max_file_m_size"].as_number(300),
                "output_file_name": hc["output_file_name"].as_str("trace"),
                "log_type": hc["log_type"].as_str("pb"),
            }
            scope_list = []
            from xdl.python.backend.model_scope import get_model_scopes

            for scope in list(get_model_scopes()):
                if scope and not scope.startswith("tf_export_graph_scope"):
                    scope_list.append(scope)

            logging.info("trace generated to %s, scopes: %s", c, scope_list)
            return [xdl.TraceHook(c, is_training=self._is_training, scope=scope_list)]
        return []

    def extend_one_bracket(self, col):
        left = col.find("[")
        if left == -1:
            return [col]
        right = col.find("]")
        prefix = col[:left]
        surfix = col[right+1:]
        dash = col.find("-")
        start = col[left+1:dash]
        end = col[dash+1:right]
        if len(start) != len(end):
            raise Exception("start,end length must equal for " + col)
        result = []
        for i in range(int(end)-int(start)+1):
            result.append((prefix + "%0" + str(len(start)) + "d" + surfix) % (int(start) + i))
        return result

    def extend_brackets(self, cols):
        result = []
        for col in cols:
            result.extend(self.extend_one_bracket(col))
        if len(result) == len(cols):
            return result
        else:
            return self.extend_brackets(result)

    def extend_cols(self, cols):
        result = []
        for col in cols:
            result.extend(self.extend_brackets([col]))
        return result

    def gen_var_list(self, include_vars, exclude_vars=[]):
        assert len(include_vars) != 0, "var list is empty."
        exclude_vars = self.extend_cols(exclude_vars)
        vars_list = [var.name for var in list(_EMBEDDING_INFO.keys())]
        result = []

        include_vars = self.extend_cols(include_vars)
        for var in include_vars:
            idx = var.find('*')
            if idx != -1:
                pattern = var[0 : idx]
                result.extend([var for var in vars_list if var.startswith(pattern)])

        result += [var for var in vars_list if var in include_vars]
        if len(exclude_vars):
            result = [var for var in result if var not in exclude_vars]

        return list(set(result))



    def gen_hash_slots_update_hook(self):
        update_dict = _EMBEDDING_SLOT_UPDATERS
        hooks = []
        def _get_key(ele):
            return ele._updater
        for k, v in list(update_dict.items()):
            v.sort(key=_get_key)
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
        for name, info in list(filter_dict.items()):
            interval = int(info["interval_steps"])
            threshold = int(info["threshold"])
            interval_dict.setdefault(interval, [[], []])
            interval_dict[interval][0].append(name)
            interval_dict[interval][1].append(threshold)
        for interval, lists in list(interval_dict.items()):
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
        for name, info in list(filter_dict.items()):
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
        for key, info in list(decay_dict.items()):
            if info["decay_interval_hours"] is not None:
                interval_key = "decay_interval_hours"
            else:
                interval_key = "decay_interval_steps"
            break
        for key, info in list(decay_dict.items()):
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
        for interval, vars in list(interval_dict.items()):
            var_decay_list = []
            for key, var_decay in list(vars.items()):
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
        for name, info in list(filter_dict.items()):
            if info["interval_hours"] is not None:
                interval_key = "interval_hours"
            else:
                interval_key = "interval_steps"
            break
        for name, info in list(filter_dict.items()):
            interval = info[interval_key]
            nonclk_weight = float(info["nonclk_weight"])
            clk_weight = float(info["clk_weight"])
            threshold = float(info["threshold"])
            interval_dict.setdefault(interval, [[], [], [], []])
            interval_dict[interval][0].append(name)
            interval_dict[interval][1].append(nonclk_weight)
            interval_dict[interval][2].append(clk_weight)
            interval_dict[interval][3].append(threshold)
        for interval, lists in list(interval_dict.items()):
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

    def gen_hash_feature_import_filter(self, config):
        hooks = []
        include_vars = config["var_list"]
        exclude_vars = []
        if "exclude_vars" in config:
            exclude_vars = config["exclude_vars"]
        import_threshold = float(config["import_threshold"])
        vars_list = self.gen_var_list(include_vars, exclude_vars)
        if len(vars_list):
            hooks.append(xdl.HashFeatureImportFilterHook(vars_list, import_threshold, xdl.get_task_index()))
        else:
            print("WARNING: HashFeatureImportFilterHook does not match any variable")
        return hooks

    def gen_worker_finish_hook(self):
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
            finish_rate=self._parameters["min_finish_worker_rate"].as_number(95)
            return [
                xdl.CheckpointHook(
                    interval_steps=interval_steps,
                    interval_hours=interval_hours,
                    end_version=self._model_version,
                    finish_rate=finish_rate
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

    def gen_notify_barrier_slave_hook(self, slave_join_check_interval_s):
        return xdl.NotifyBarrierSlaveHook(xdl.get_task_index(), xdl.get_task_num(),
                                      join_barrier_interval_seconds=slave_join_check_interval_s)

    def gen_metrics_hook(self, ts_tensor, additional_metrics=[]):
        from xdl.python.utils.interval import Interval
        collect_interval = Interval.create_interval(
            step=self._parameters["metrics_interval"].as_number()
        )
        from xdl.python.training.hook_utils import XdlMetricsHook
        return [
            XdlMetricsHook(
                ts_tensor=ts_tensor,
                other_tensors=additional_metrics,
                collect_interval=collect_interval,
                sinker=self._metrics_sinker,
            )
        ]
    def gen_all_hook(self, reader, ts_tensor):
        hooks = []
        this_module = sys.modules[__name__]
        max_timestamp = xdl.max_value(ts_tensor)
        if self._parameters["hooks"]["hash_feature_import"].exists(use_default=False):
            hooks.extend(self.gen_hash_feature_import_filter(self._parameters["hooks"]["hash_feature_import"].flatten()))
        trace_hook = self.gen_trace_hook()
        hooks.extend(trace_hook)
        if trace_hook and self._stage is "predict":
            xdl.trace_collection(EMBEDDING_INFOS, scope="")
        save_metrics_hook = self.gen_save_metrics(max_timestamp)
        hooks.extend(save_metrics_hook)
        record_metrics_hook = self.gen_record_metrics_to_prometheus(max_timestamp)
        hooks.append(record_metrics_hook)
        if self._is_training:
            max_ts = self.gen_max_timestamp_hook(max_timestamp)
            hooks.extend(self.gen_hash_slots_update_hook())
            hooks.extend(self.gen_global_step_filter_hook())
            hooks.extend(self.gen_timestamp_filter_hook())
            hooks.extend(self.gen_hash_feature_decay_hook())
            hooks.extend(self.gen_hash_feature_score_filter_hook())
            hooks.extend(self.gen_kafka_timestamp_hook(reader, ts_tensor))
            hooks.extend(self.gen_pulsar_timestamp_hook(reader, ts_tensor))
            if xdl.get_run_mode() != "local":
                variable_sync_hook = self.gen_vars_sync_hook()
                hooks.extend(variable_sync_hook)
        if self._is_save_ckpt:
            hooks.extend(self.gen_checkpoint_hook())
        if not self._is_local:
            hooks.extend(self.gen_worker_finish_hook())
        return hooks

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

        hooks.append(
            xdl.LoggerHook(
                log_tensors[:],
                log_str,
                interval=self._parameters["log_interval"].as_number(),
            )
        )
        hooks.extend(self.gen_all_hook(reader, batch["_timestamp"]))
        # metric hook
        if xdl.get_task_index() == 0:
            hooks.extend(self.gen_metrics_hook(batch["_timestamp"],
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
