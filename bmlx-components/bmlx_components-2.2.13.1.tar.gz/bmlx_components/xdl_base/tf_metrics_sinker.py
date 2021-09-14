import logging, tempfile, json, os
import numpy as np
import tensorflow as tf
from bmlx.utils import io_utils
import abc
class MetricsSinker:
    def __init__(self):
        self._dir = tempfile.mkdtemp()

    def close(self):
        # io_utils.rmtree(self._dir)
        pass

    @abc.abstractmethod
    def __call__(self, ts, metrics, sample_ts, step):
        raise NotImplementedError("not implelmented")


class TfMetricsSinker(MetricsSinker):
    def __init__(self, fp):
        super(TfMetricsSinker, self).__init__()
        self.fw = tf.compat.v1.summary.FileWriter(self._dir)
        self._final_metric_value = dict()
        self._fp = fp

    def __call__(self, ts, metrics, sample_ts, step):
        logging.debug("dump metrics step %s to %s" % (step, self._dir))
        for name, value in metrics:
            if isinstance(value, np.ndarray):
                self._final_metric_value[name] = []
                for i, subvalue in enumerate(
                        value.tolist()
                        if isinstance(value.tolist(), list)
                        else [value.tolist()]
                ):
                    summary = tf.Summary(
                        value=[
                            tf.Summary.Value(
                                tag="%s_%d" % (name, i),
                                simple_value=subvalue,
                            )
                        ]
                        if not isinstance(subvalue, list)
                        else [
                            tf.Summary.Value(
                                tag="%s_%d" % (name, i),
                                simple_value=sv,
                            )
                            for sv in subvalue
                        ]
                    )
                    self.fw.add_summary(
                        summary=summary, global_step=step
                    )
                    self._final_metric_value[name].append(subvalue)
            elif isinstance(value, (int, float)):
                summary = tf.Summary(
                    value=[
                        tf.Summary.value(tag=name, simple_value=value)
                    ]
                )
                self.fw.add_summary(summary=summary, global_step=step)
                self._final_metric_value[name] = value
            else:
                raise RuntimeError(
                    "unknown metrics type: %s" % (type(value))
                )
        self._final_metric_value["sample_ts"] = sample_ts
        self.fw.flush()

    def close(self):
        logging.info("upload metrics from %s => %s" % (self._dir, self._fp))
        io_utils.copytree(self._dir, self._fp)
        self.fw.close()
        if self._final_metric_value:
            io_utils.write_string_file(
                os.path.join(self._fp, "final_metrics"),
                json.dumps(self._final_metric_value).encode(),
            )
            logging.info("final metrics: %s", self._final_metric_value)
        super(TfMetricsSinker, self).close()

def _tf_metrics_sinker(fp):
    return TfMetricsSinker(fp)
