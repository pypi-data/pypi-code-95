import xdl
import numpy as np
import struct
import os
import logging
import tempfile
import time
import datetime
import collections
from xdl.python.framework.session import Hook
from xdl.python.training.training_utils import get_global_step
from xdl.python.utils import collections as xdl_collections
from xdl.python.proto import trace_pb2
from xdl.python.pybind import get_file_system
from xdl.python.training import trace
from xdl.python.lib.graph import execute
from bmlx.utils import io_utils


def nptype2trace(np_type):
    if np_type == np.int8:
        return trace_pb2.Int8
    elif np_type == np.int16:
        return trace_pb2.Int16
    elif np_type == np.int32:
        return trace_pb2.Int32
    elif np_type == np.int64:
        return trace_pb2.Int64
    elif np_type == np.float32:
        return trace_pb2.Float
    elif np_type == np.float64:
        return trace_pb2.Double
    elif np_type == np.bool:
        return trace_pb2.Bool
    elif np_type == np.byte:
        return trace_pb2.Byte
    else:
        raise RuntimeError("unknown numpy dtype: {}".format(np_type))


class TraceWriter(object):
    def __init__(self, config, is_training=True):
        if "output_dir" not in config:
            raise RuntimeError("trace output_dir not specified")
        self._output_dir = config["output_dir"]

        self._max_file_size = 300
        if "max_file_m_size" in config:
            self._max_file_size = config["max_file_m_size"]
        self._output_file_name = "trace"
        if "output_file_name" in config:
            self._output_file_name = config["output_file_name"]
        self._log_type = "pb"
        if "log_type" in config:
            self._log_type = config["log_type"]
            if self._log_type != "pb" and self._log_type != "txt":
                logging.error(
                    (
                        "{} is not supported, will trace as pb".format(
                            self._log_type
                        )
                    )
                )
                self._log_type = "pb"

        self._rank = xdl.get_task_index()
        prefix = "train" if is_training else "test"

        self._writer = None
        self._meta_writer = None

        self._local_output_dir = tempfile.mkdtemp()

        self._out_prefix = os.path.join(
            self._local_output_dir,
            "{}.{}.{}".format(prefix, self._output_file_name, self._rank),
        )
        self._cur_file_index = 0
        self._new_file()
        self._headers = []

        self._lstep_begin = -1
        self._lstep_end = -1
        self._gstep_begin = -1
        self._gstep_end = -1
        self._timestamp_begin = -1
        self._timestamp_end = -1

        self._last_lstep = -1
        self._last_gstep = -1
        self._last_timestamp = -1

    def _close_writers(self):
        if self._writer and not self._writer.closed:
            self._writer.close()
        if self._meta_writer and not self._meta_writer.closed:
            self._meta_writer.close()

    def finish(self):
        self._close_writers()
        logging.info(
            "TraceHook finished, upload data from local dir %s to remote dir %s",
            self._local_output_dir,
            self._output_dir,
        )
        io_utils.upload_dir(self._local_output_dir, self._output_dir)

    def _new_file(self):
        self._close_writers()

        self._cur_size = 0
        self._cur_file_index += 1
        self._cur_path = "{}.{}".format(self._out_prefix, self._cur_file_index)
        self._cur_meta_path = "{}.meta".format(self._cur_path)
        self._writer = open(self._cur_path, "wb")
        self._meta_writer = open(self._cur_meta_path, "wb")

    def _write_buf(self, buf):
        self._cur_size += len(buf)
        self._writer.write(buf)

    def _write_size(self, size):
        buf = struct.pack("<I", size)
        self._write_buf(buf)

    def _write_protobuf(self, msg):
        buf = msg.SerializeToString()
        self._write_size(len(buf))
        self._write_buf(buf)

    def _write_jsonbuf(self, msg):
        buf = "|".join(msg)
        buf += "\n"
        self._write_buf(buf)

    def write_headers(self, headers):
        self._headers = headers
        if self._log_type == "pb":
            header = trace_pb2.Header()
            header.key.extend(headers)
            self._write_protobuf(header)
        elif self._log_type == "txt":
            self._write_jsonbuf(headers)
        else:
            pass

    def write_meta(self):
        meta = trace_pb2.Meta()
        meta.lstep_begin = self._lstep_begin
        meta.lstep_end = self._lstep_end
        meta.gstep_begin = self._gstep_begin
        meta.gstep_end = self._gstep_end
        meta.timestamp_begin = self._timestamp_begin
        meta.timestamp_end = self._timestamp_end
        buf = meta.SerializeToString()
        self._meta_writer.write(buf)

    def write_records(self, columns, gstep, lstep, timestamp):
        if self._last_lstep == -1:
            self._last_lstep = lstep
        if self._last_gstep == -1:
            self._last_gstep = gstep
        if self._last_timestamp == -1:
            self._last_timestamp = timestamp
        if self._lstep_begin == -1:
            self._lstep_begin = self._last_lstep
        if self._gstep_begin == -1:
            self._gstep_begin = self._last_gstep
        if self._timestamp_begin == -1:
            self._timestamp_begin = self._last_timestamp
        if self._cur_size >= self._max_file_size * 1e6:
            self._lstep_end = self._last_lstep
            self._gstep_end = self._last_gstep
            self._timestamp_end = self._last_timestamp
            self.write_meta()
            self._new_file()
            self.write_headers(self._headers)
            self._lstep_begin = -1
            self._gstep_begin = -1
            self._timestamp_begin = -1
        assert len(self._headers) == len(columns)
        if self._log_type == "pb":
            record = trace_pb2.Record()
            record.gstep = gstep
            record.lstep = lstep
            record.timestamp = timestamp
            for arr in columns:
                col = record.column.add()
                col.dtype = nptype2trace(arr.dtype)
                col.shape.extend(list(arr.shape))
                col.data = arr.tobytes()
            self._write_protobuf(record)

        self._last_lstep = lstep
        self._last_gstep = gstep
        self._last_timestamp = timestamp


class TraceFilter(object):
    def filtered(self, **kwargs):
        return False


class StepFilter(TraceFilter):
    def __init__(self, step_size=100):
        self._step_size = step_size

    def filtered(self, **kwargs):
        lstep = kwargs["lstep"]
        return lstep % self._step_size != 0


class RangeFilter(TraceFilter):
    def __init__(self, start, end):
        self._start = start
        self._end = end

    def filtered(self, **kwargs):
        lstep = kwargs("lstep")
        return lstep < self._start or lstep > self._end


class TimeFilter(TraceFilter):
    def __init__(self, window):
        self._window = window
        self._start = datetime.datetime.now()

    def filtered(self, **kwargs):
        cur = datetime.datetime.now()
        diff = cur - self._start
        if diff.total_seconds() >= self._window:
            self._start = datetime.datetime.now()
            return True
        return False


_default_filter = TraceFilter()


class TraceHook(Hook):
    def __init__(
        self,
        config=None,
        is_training=True,
        gstep=None,
        trace_filter=_default_filter,
        scope=None,
    ):
        super(TraceHook, self).__init__()
        self._keys = []
        self._values = []
        self._summaries = []
        # callbacks
        self._cb_keys = []
        self._cbs = []

        # once
        self._once_keys = []
        self._once_values = []

        # sparse assign
        self._sparse_assign_vars = []
        self._sparse_assign_ids = []
        self._sparse_assign_values = []

        if is_training or gstep is None:
            self._gstep = get_global_step()
            self._use_gstep = True
        else:
            self._gstep = gstep
            self._use_gstep = False
        self._lstep = 0
        if config is None or "output_dir" not in config:
            logging.warning(
                "WARNING: no output_dir found, trace will not work!!!"
            )
            self._writer = None
        else:
            self._writer = TraceWriter(config, is_training)

        self._filter = trace_filter

        scope = list(scope) if isinstance(scope, (list, tuple)) else [scope]
        for s in scope:
            info = trace.get_values("tf_sparse_assign", s)
            vars = trace.get_variables("tf_sparse_assign", s)
            self._sparse_assign_ids.extend(
                [info[i] for i in range(len(info)) if i % 2 == 0]
            )
            self._sparse_assign_values.extend(
                [info[i] for i in range(len(info)) if i % 2 == 1]
            )
            self._sparse_assign_vars.extend(
                [vars[i] for i in range(len(vars)) if i % 2 == 0]
            )

            for vtype in ["xdl", "tf", "mxnet"]:
                self._keys.extend(trace.get_names(vtype, s))
                self._values.extend(trace.get_values(vtype, s))
                self._summaries.extend(trace.get_functions(vtype, s))
            self._cb_keys.extend(trace.get_names("function", s))
            self._cbs.extend(trace.get_functions("function", s))

            self._once_keys.extend(trace.get_names("once", s))
            self._once_values.extend(trace.get_values("once", s))

            assert len(self._sparse_assign_ids) == len(
                self._sparse_assign_values
            )
            assert len(self._sparse_assign_ids) == len(self._sparse_assign_vars)

            assert len(self._keys) == len(self._values)
            assert len(self._keys) == len(self._summaries)
            assert len(self._cb_keys) == len(self._cbs)
            assert len(self._once_keys) == len(self._once_values)

        logging.info(("before_run_key: %s", self._keys))
        logging.info(("before_run_tensors: %s", self._values))

    def _execute_sparse_assign(self, sparse_ids, sparse_vals):
        assert len(sparse_ids) == len(self._sparse_assign_ids)
        assert len(sparse_vals) == len(self._sparse_assign_values)
        for i in range(len(self._sparse_assign_ids)):
            ids = sparse_ids[i]
            values = sparse_vals[i]
            var = self._sparse_assign_vars[i]
            op = xdl.ps_sparse_assign_op(
                var_name=var.name, var_type=var.vtype, ids=ids, values=values
            )
            execute(op)

    def before_run(self, v):
        res = []
        if self._use_gstep:
            res = [self._gstep.value, self._values]
        else:
            res = [self._values]
        if self._lstep == 0 and len(self._once_keys) > 0:
            res.append(self._once_values)
        if len(self._sparse_assign_ids) > 0:
            res.append(self._sparse_assign_ids)
            res.append(self._sparse_assign_values)
        return res

    def after_run(self, v):
        self._lstep += 1
        if self._filter.filtered(lstep=self._lstep):
            return
        if self._use_gstep:
            gstep, values = v[0], v[1]
            if len(self._sparse_assign_ids) > 0:
                sparse_ids, sparse_vals = v[2], v[3]
        else:
            gstep, values = self._gstep, v[0]
            if len(self._sparse_assign_ids) > 0:
                sparse_ids, sparse_vals = v[1], v[2]
        if len(self._sparse_assign_ids) > 0:
            self._execute_sparse_assign(sparse_ids, sparse_vals)
        once_values = []
        if len(self._once_keys) > 0:
            if self._lstep == 1:
                once_values = v[2]
            else:
                once_values = len(self._once_keys) * [
                    np.array([], dtype=np.float32)
                ]

        assert len(self._keys) == len(values)
        cb_values = []
        for cb in self._cbs:
            cb_values.append(cb())
        assert len(self._cb_keys) == len(cb_values)
        if self._writer is None:
            return
        if self._lstep == 1:
            self._writer.write_headers(
                self._keys + self._cb_keys + self._once_keys
            )
        # execute user summary function
        temp_values = []
        for v, func in zip(values, self._summaries):
            if isinstance(func, collections.Callable):
                temp_values.append(func(v))
            else:
                temp_values.append(v)

        self._writer.write_records(
            temp_values + cb_values + once_values,
            gstep,
            self._lstep,
            int(time.time() * 1000),
        )

    def end(self):
        self._writer.finish()

    def add_variable(self, var_name, key=None, scope=None):
        if key is None:
            if scope is not None and scope != "":
                key = scope + "/" + var_name
            else:
                key = var_name
        global_vars = xdl_collections.get_collection(
            xdl_collections.GLOBAL_VARIABLES, scope
        )
        not_found = True
        for var in global_vars:
            if var.name == var_name:
                not_found = False
                # add to keys and values
                self._keys.append(key)
                self._values.append(var.value)
                break
        if not_found:
            logging.warning(
                ("WARNING: variable %s not found to trace" % var_name)
            )

    def add_tensor(self, value, key):
        self._keys.append(key)
        self._values.append(value)

    def add_gradient(self, var_name, key=None, scope=None):
        if key is None:
            if scope is not None and scope != "":
                key = scope + "/gradient/" + var_name
            else:
                key = "gradient/" + var_name
        gradient = xdl.get_gradient(var_name, scope)
        self._keys.append(key)
        self._values.append(gradient)

    def add_collection(self, coll_name, scope=None):
        coll = xdl_collections.get_collection(coll_name, scope)
        for var in coll:
            key = var.name
            if scope is not None and scope != "":
                key = scope + "/" + key
            self._keys.append(key)
            self._values.append(var.value)

    def add_callback(self, callback, key):
        self._cb_keys.append(key)
        self._cbs.append(callback)
