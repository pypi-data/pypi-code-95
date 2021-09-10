'''Module specific to amd64-cpu arch.'''

import psutil as _pu
import subprocess as _sp


def get_mem_info_impl(arch):
    mem_info = _pu.virtual_memory()

    res = {'gpus': [], 'cpu_mem_free': mem_info.free, 'cpu_mem_used': mem_info.used, 'cpu_mem_total': mem_info.total}

    rpi_model_filepath = '/sys/firmware/devicetree/base/model'
    rpi_model = _sp.check_output(['cat', rpi_model_filepath]).decode().strip()
    res['model'] = rpi_model

    return res
