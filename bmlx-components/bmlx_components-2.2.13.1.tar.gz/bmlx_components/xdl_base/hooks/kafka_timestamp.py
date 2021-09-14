import xdl
from xdl.python.framework.session import Hook
from xdl.python.lib.datatype import DataType
from xdl.python.framework.variable import get_variable_scope, Variable
from xdl.python.ops.init_ops import Zeros
from xdl.python.lib.graph import execute


class KafkaTimestampHook(Hook):
    def __init__(self, data_io, ts_tensor):
        super(KafkaTimestampHook, self).__init__()
        self._worker_num = xdl.get_task_num()
        self._worker_index = xdl.get_task_index()
        self._last_state = []
        self._data_io = data_io
        self._save_mark = xdl.max_value(ts_tensor)
        with xdl.python.framework.variable.variable_info(end_save="false"):
            self._state_var = Variable(
                name=self._data_io.ds_name + "/max_timestamp",
                shape=[self._worker_num, 1],
                dtype=DataType.int64,
                initializer=Zeros(),
                trainable=False,
            )

    def before_run(self, v):
        return [self._save_mark]

    def after_run(self, v):
        import numpy as np

        self.mark_value = v[0] if isinstance(v, list) else v
        update_op = xdl.ps_sparse_assign_op(
            var_name=self._state_var.name,
            var_type=self._state_var.vtype,
            ids=np.array([self._worker_index], dtype=np.int64),
            values=[self.mark_value],
        )
        execute(update_op)
