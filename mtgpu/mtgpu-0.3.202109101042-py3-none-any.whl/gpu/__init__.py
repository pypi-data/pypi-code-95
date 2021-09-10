from __future__ import absolute_import, division, print_function

from .version import version as __version__
from .arch import detect_machine


__all__ = ['detect_machine', 'get_mem_info']


def get_mem_info(print_bars=False):
    '''Returns a dictionary containing information about detected CPU/GPU devices and their memory usage, or None if the architecture is unknown.

    Parameters
    ----------
    print_bars : bool
        whether or not to print some bars
    '''
    arch = detect_machine()

    if arch == 'amd64-cpu':
        from .arch_amd64_cpu import get_mem_info_impl
        res = get_mem_info_impl()
    elif arch == 'amd64-nvidia':
        from .arch_amd64_nvidia import get_mem_info_impl
        res =  get_mem_info_impl()
    elif arch == 'amd64-amd':
        from .arch_amd64_amd import get_mem_info_impl
        res = get_mem_info_impl()
    elif arch in ['arm64-rp3', 'arm64-rp4']:
        from .arch_rpi import get_mem_info_impl
        res = get_mem_info_impl(arch)
    elif arch in ['arm64-tx1', 'arm64-tx2', 'arm64-xnx']:
        from .arch_tegra import get_mem_info_impl
        res = get_mem_info_impl(arch)
    elif arch == 'unknown':
        res = None

    if print_bars and res:
        from tqdm import tqdm
        MB = 1024*1024

        is_cgpu = res.get('cpu_mem_shared_with_gpu', False)

        cpu_desc = 'cpu_gpu' if is_cgpu else 'cpu'
        cpu_bar = tqdm(desc=cpu_desc, total=res['cpu_mem_total']//MB, initial=res['cpu_mem_used']//MB, unit='MB', bar_format='{l_bar}{bar}|{n_fmt}/{total_fmt} {unit}')
        cpu_bar.display()
        cpu_bar.close()

        if not is_cgpu:
            for i, gpu in enumerate(res['gpus']):
                gpu_desc = 'gpu {} ({})'.format(i, gpu['name'])
                gpu_bar = tqdm(desc=gpu_desc, total=gpu['mem_total']//MB, initial=gpu['mem_used']//MB, unit='MB', bar_format='{l_bar}{bar}|{n_fmt}/{total_fmt} {unit}')
                gpu_bar.display()
                gpu_bar.close()

    return res
