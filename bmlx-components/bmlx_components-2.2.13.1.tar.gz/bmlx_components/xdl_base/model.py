import xdl
import abc
import logging
import functools

import tensorflow as tf
from typing import Dict, Text, List
from xdl.python.framework.session import Hook

def get_conf(dict, key, default=None):
    if key in dict:
        return dict[key].as_number()
    else:
        return default


class ProcessResult:
    def __init__(self, tensor_map={}, additional_hooks=[]):
        self.tensor_map = tensor_map
        self.additional_hooks = additional_hooks

    tensor_map: Dict[Text, tf.Tensor] = {}
    additional_hooks: List[Hook] = []

    def append(self, result, prefix=""):
        result.tensor_map = result.tensor_map or {}
        self.tensor_map.update(
            {f"{prefix}{k}": v for k, v in result.tensor_map.items()}
        )
        self.additional_hooks.extend(result.additional_hooks or [])


def tf_wrapper_with_self(f):
    def wrapped(self, *f_args, **f_kwargs):
        tf_wrapper = xdl.tf_wrapper(export_graph=self._is_training)
        wrap_self = functools.partial(f, self)
        assert "is_training" in f_kwargs or "is_training" in f_args, "is_training must be set in model_func's kwargs"
        return tf_wrapper(wrap_self)(*f_args, **f_kwargs)

    return wrapped


class XdlModel(object):
    def __init__(self, parameters, schema, stage, is_training):
        self._parameters = parameters
        self._schema = schema
        self._stage = stage
        self._is_training = is_training

    """
    这个类值得注意的一个trick是，用户如果指定了hooks，那就会激发默认值，否则默认不打开
    """

    def get_slot_filters(self, slot, click=None, timestamp_feat_slot=None):
        def descade_get(conf, dft, key):
            if conf and key in conf:
                return conf[key]
            elif dft and key in dft:
                return dft[key]
            else:
                raise RuntimeError("config '%s' non exists" % key)

        ret = []
        if self._parameters["hooks"]["global_step"].exists():
            gs_config = self._parameters["hooks"]["global_step"]
            slot_config = gs_config[slot] if slot in gs_config else None
            dft_config = gs_config["default"]

            interval_steps = descade_get(
                slot_config, dft_config, "interval_steps"
            ).as_number()
            filter_threshold = descade_get(
                slot_config, dft_config, "filter_threshold"
            ).as_number()
            ret.append(
                xdl.GlobalStepFilter(
                    interval_steps=interval_steps,
                    filter_threshold=filter_threshold,
                )
            )
            logging.info(
                "Added global step filter for %s, [threshold:%s, interval_step:%s]"
                % (slot, filter_threshold, interval_steps)
            )

        if self._parameters["hooks"]["feature_score"].exists():
            assert click is not None
            fsf_config = self._parameters["hooks"]["feature_score"]
            slot_config = fsf_config[slot] if slot in fsf_config else None
            dft_config = fsf_config["default"]

            filter_threshold = descade_get(
                slot_config, dft_config, "filter_threshold"
            ).as_number()
            decay_interval_hours = descade_get(
                slot_config, dft_config, "decay_interval_hours"
            ).as_number()
            interval_hours = descade_get(
                slot_config, dft_config, "interval_hours"
            ).as_number()
            decay_rate = descade_get(
                slot_config, dft_config, "decay_rate"
            ).as_number()
            click_weight = descade_get(
                slot_config, dft_config, "click_weight"
            ).as_number()
            show_weight = descade_get(
                slot_config, dft_config, "show_weight"
            ).as_number()
            ret.append(
                xdl.FeatureScoreFilter(
                    filter_threshold=filter_threshold,
                    click=click,
                    decay_interval_hours=decay_interval_hours,
                    interval_hours=interval_hours,
                    decay_rate=decay_rate,
                    click_weight=click_weight,
                    show_weight=show_weight,
                )
            )
            logging.info(
                "Added feature score filter for %s, [threshold:%s][decay_interval_hour:%s][interval_hour:%s][decay_rate:%s][click_weight:%s][show_weight:%s]"
                % (
                    slot,
                    filter_threshold,
                    decay_interval_hours,
                    interval_hours,
                    decay_rate,
                    click_weight,
                    show_weight,
                )
            )

        if self._parameters["hooks"]["timestamp"].exists():
            ts_config = self._parameters["hooks"]["timestamp"]
            slot_config = ts_config[slot] if slot in ts_config else None
            dft_config = ts_config["default"]
            interval_hours = descade_get(
                slot_config, dft_config, "interval_hours"
            ).as_number()
            filter_threshold = descade_get(
                slot_config, dft_config, "filter_threshold"
            ).as_number()
            ret.append(
                xdl.TimestampFilter(
                    interval_hours=interval_hours,
                    filter_threshold=filter_threshold,
                    ts_tensor=timestamp_feat_slot,
                )
            )
            logging.info(
                "added timestamp filter for %s, [interval_hours:%s][filter_threshold:%s]"
                % (slot, interval_hours, filter_threshold)
            )

        return ret

    @abc.abstractmethod
    def process(self, batch: xdl.Batch, phase: int, **kwargs) -> ProcessResult:
        pass

    def generate_one_optimizer(self, conf):
        name = conf["name"].as_str()
        print("name: ", type(name))
        name = name.lower()
        if name == "adam":
            learning_rate = get_conf(conf, "learning_rate", 0.001)
            beta1 = get_conf(conf, "beta1", 0.9)
            beta2 = get_conf(conf, "beta2", 0.999)
            epsilon = get_conf(conf, "epsilon", 1e-08)
            lr_decay = get_conf(conf, "lr_decay", True)
            return xdl.Adam(learning_rate, beta1, beta2, epsilon, lr_decay)
        elif name == "adagrad":
            learning_rate = get_conf(conf, "learning_rate")
            initial_accumulator_value = get_conf(conf, "initial_accumulator_value", 0.1)
            return xdl.Adagrad(learning_rate, initial_accumulator_value)
        elif name == "momentum":
            learning_rate = get_conf(conf, "learning_rate")
            momentum = get_conf(conf, "momentum")
            use_nesterov = get_conf(conf, "use_nesterov", False)
            return xdl.Momentum(learning_rate, momentum, use_nesterov)
        elif name == "sgd":
            learning_rate = get_conf(conf, "learning_rate")
            return xdl.SGD(learning_rate)
        elif name == "rmsprop":
            learning_rate = get_conf(conf, "learning_rate")
            decay =  get_conf(conf, "decay", 0.9)
            momentum = get_conf(conf, "momentum", 0.0)
            epsilon = get_conf(conf, "epsilon", 1e-10)
            return xdl.RMSProp(learning_rate, decay, momentum, epsilon)
        elif name == "ftrl":
            learning_rate = get_conf(conf, "learning_rate")
            learning_rate_power = get_conf(conf, "learning_rate_power", -0.5)
            initial_accumulator_value = get_conf(conf, "initial_accumulator_value", 0.1)
            l1_regularization_strength = get_conf(conf, "l1_regularization_strength", 0.0)
            l2_regularization_strength = get_conf(conf, "l2_regularization_strength", 0.0)                
            return xdl.Ftrl(learning_rate, learning_rate_power, initial_accumulator_value, l1_regularization_strength, l2_regularization_strength)
        elif name == "none":
            return None
        else:
            raise Exception("optimizer " + name + " not support.")
        
    def get_optimizer(self):
        return self.generate_one_optimizer(self._parameters['optimizer'])

