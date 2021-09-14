import xdl
import numpy as np
from xdl.python.framework.session import Hook
from xdl.python.lib.datatype import DataType
from xdl.python.framework.variable import Variable
from xdl.python.ops.init_ops import Zeros
from xdl.python.lib.graph import execute

class PulsarTimestampHook(Hook):
    def __init__(self, data_io, ts_tensor, pulsar_path):
        super(PulsarTimestampHook, self).__init__()
        self._save_mark = xdl.max_value(ts_tensor)
        self._data_io = data_io
        self._worker_num = xdl.get_task_num()
        self._worker_index = xdl.get_task_index()
        self.pulsar_path = str(pulsar_path)
        with xdl.python.framework.variable.variable_info(end_save='false'):
            self._state_var = Variable(
                name=self._data_io.ds_name + "/max_timestamp",
                shape=[self._worker_num, 1],
                dtype=DataType.int64,
                initializer=Zeros(),
                trainable=False)

    # seek operation should be executed at here no matter python api or c++ api
    def create_session(self):
        if self._worker_index == 0:
            state_op = self._state_var.gather(np.arange(0, self._worker_num, 1, np.int64))
            state = execute(state_op)
            off = min(state.tolist())[0]
            path = self.pulsar_path.split('/', 3)[-1]
            topic, begin_off = path.split("#")
            if begin_off == "":
                begin_stamp = off
            else:
                if "_" in begin_off:
                    begin_off, end_off = begin_off.split("_")
                begin_stamp = time2stamp(begin_off)
            if off != 0 and off > begin_stamp:
                begin_stamp = off
            offsets = np.array([begin_stamp] * int(self._data_io._reader_threads))
        else:
            offsets = np.array([0] * int(self._data_io._reader_threads))
        if offsets.any():
            pb = _load(offsets)
            if pb != None:
                print("restore_pulsar_state: ", pb)
                self._data_io.restore_pulsar_state(pb)
    def before_run(self, v):
        return [self._save_mark]

    def after_run(self, v):
        self.mark_value = v[0] if isinstance(v, list) else v
        update_op = xdl.ps_sparse_assign_op(
            var_name=self._state_var.name,
            var_type=self._state_var.vtype,
            ids=np.array([self._worker_index], dtype=np.int64),
            values=[self.mark_value])
        execute(update_op)