'''Module specific to amd64-cpu arch.'''

import psutil as _pu


def get_mem_info_impl():
    mem_info = _pu.virtual_memory()
    return {'gpus': [], 'cpu_mem_free': mem_info.free, 'cpu_mem_used': mem_info.used, 'cpu_mem_total': mem_info.total}
