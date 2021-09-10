'''Module to detect the machine architecture.'''


import subprocess as _sp
import os.path as _op


def detect_machine():
    '''Detects the machine architecture.

    Returns
    -------
    ['arm64-rpi', 'arm64-tx1', 'arm64-tx2', 'arm64-j43', 'amd64-cpu', 'amd64-nvidia', 'amd64-amd']
        a unique name identifying the machine architecture

    Notes
    -----
    The names correspond to the following architectures:

    - "arm64-rp4" : a Raspberry Pi Model 4
    - "arm64-rp3" : a Raspberry Pi Model 3
    - "arm64-tk1" : an Nvidia Tegra K1
    - "arm64-tx1" : an Nvidia Tegra X1
    - "arm64-tx2" : an Nvidia Tegra X2
    - "arn64-xnx" : an Nvidia Jetson Xavier-NX
    - "amd64-cpu" : an amd64 PC without any graphic card
    - "amd64-nvidia" : an amd64 PC with Nvidia graphic card(s)
    - "amd64-amd" : and amd64 PC with AMDGPU card(s)
    '''
    machine_type = _sp.check_output(['uname', '-m']).decode().strip()

    if machine_type == 'aarch64': # arm64
        tegra_chip_id_filepath = '/sys/module/tegra_fuse/parameters/tegra_chip_id'

        if not _op.exists(tegra_chip_id_filepath): # not a Tegra? maybe an RPi

            rpi_model_filepath = '/sys/firmware/devicetree/base/model'

            if not _op.exists(rpi_model_filepath):
                return "unknown" # unknown aarch64

            rpi_model = _sp.check_output(['cat', rpi_model_filepath]).decode().strip()

            if rpi_model.startswith('Raspberry Pi 4'):
                return "arm64-rp4"

            if rpi_model.startswith('Raspberry Pi 3'):
                return "arm64-rp3"

            return "unknown" # unknown Raspberry Pi model

        # Tegra
        chip_id = _sp.check_output(['cat', tegra_chip_id_filepath]).decode().strip()
        # We expect TK1 to respond '64', TX1 to respond '32', TX2 to respond '24'.
        if chip_id == '64':
            return "arm64-tk1" # obsolete
        if chip_id in ['32', '33']:
            return "arm64-tx1"
        if chip_id == '25':
            return "arm64-xnx"
        if chip_id != '24': # need to expand later
            return "unknown"

        # TX2
        return "arm64-tx2" # need to expand later

    if machine_type != 'x86_64':
        return "unknown" # need to expand later

    try:
        nvidia_smi = _sp.check_output(['which', 'nvidia-smi']).decode().strip()
        if nvidia_smi:
            return 'amd64-nvidia'
    except:
        pass

    try:
        rocm_smi = _sp.check_output(['which', 'rocm-smi']).decode().strip()
        if rocm_smi:
            return 'amd64-amd'
    except:
        pass

    return 'amd64-cpu'
