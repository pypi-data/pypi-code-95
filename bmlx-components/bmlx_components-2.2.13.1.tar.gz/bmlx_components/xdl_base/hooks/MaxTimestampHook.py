import xdl
from xdl.python.lib.graph import execute
from xdl.python.framework.session import Hook
class MaxTimestampHook(Hook):
    def __init__(self, ts_tensor):
        super(MaxTimestampHook, self).__init__()
        from xdl.python.training.training_utils import get_global_timestamp
        self._global_timestamp = get_global_timestamp()
        self._save_mark = ts_tensor

    def before_run(self, v):
        return [self._global_timestamp.value, self._save_mark]

    def after_run(self, v):
        self.global_timestamp = v[0]
        self.mark_value = v[1]
        if self.mark_value > self.global_timestamp:
            update_op = xdl.ps_assign_op(delta=self.mark_value,
                                         var_name=self._global_timestamp.name,
                                         var_type=self._global_timestamp.vtype)
            execute(update_op)

