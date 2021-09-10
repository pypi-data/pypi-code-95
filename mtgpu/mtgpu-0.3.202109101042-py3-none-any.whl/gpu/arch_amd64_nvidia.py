'''Module specific to amd64-nvidia arch.'''


import psutil as _pu

try:
    from pynvml import *
except ImportError:
    raise RuntimeError("Package 'pynvml' is required on a machine with an Nvidia GPU card. Please install pynvml using pip.")


def get_mem_info_impl():
    res = {}

    mem_info = _pu.virtual_memory()
    res['cpu_mem_free'] = mem_info.free
    res['cpu_mem_used'] = mem_info.used
    res['cpu_mem_total'] = mem_info.total
    res['cpu_mem_shared_with_gpu'] = False

    nvmlInit()
    driver_version = nvmlSystemGetDriverVersion().decode()
    deviceCount = nvmlDeviceGetCount()
    if deviceCount:
        gpus = []
        for i in range(deviceCount):
            gpu = {}
            handle = nvmlDeviceGetHandleByIndex(i)
            
            gpu['name'] = nvmlDeviceGetName(handle).decode()
            gpu['driver_version'] = driver_version

            gpu['bus'] = nvmlDeviceGetPciInfo(handle).busId.decode()
            try:
                gpu['fan_speed'] = nvmlDeviceGetFanSpeed(handle)
            except:
                pass

            mem_info = nvmlDeviceGetMemoryInfo(handle)
            gpu['mem_free'] = mem_info.free
            gpu['mem_used'] = mem_info.used
            gpu['mem_total'] = mem_info.total

            gpus.append(gpu)

        res['gpus'] = gpus
    else:
        res['gpus'] = []

    nvmlShutdown()

    return res
