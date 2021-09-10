"""
    This file contains example code that shows the basic usage of the SeggerBackend.py module. In this demo a
    segger backend is used to connect to a nRF5340 devkit, halt the processor, and interact with a CPU register.
    Note that this is a bare-bones example that doesn't cover all features. For example, the nvmc callback functions are
    not implemented.

    Sample program: segger_backend_demo.py
    Requires an nRF5340 Development Kit. This example has been tested with revision ENGA and ENGB.
    Use nrfjprog.exe --deviceversion to find your devkit version.

    Run from command line:
        python segger_backend_demo.py --snr=< snr >
    or if imported as "from pynrfjprog import examples"
        examples.segger_backend_demo.run(< snr >)

    Program flow:
        0. Create a segger backend instance.
        1. Read SEGGER JLink DLL version
        2. Connect to the emulator, then the device.
        3. Halt device CPU, and write 0 to the PC.
        4. Read the PC and confirm it has the same value.
        5. Disconnect from the device and emulator, and close the DLL by ending the 'with' block.

"""
from __future__ import print_function

try:
    from .. import SeggerBackend
except Exception:
    from pynrfjprog import SeggerBackend

import ctypes
import argparse

# Start logging
import logging

logger = logging.getLogger(__name__)

segger_backends = list()


def get_segger_instance_from_user_defined(void_ptr):
    if void_ptr == 0:
        logger.error("Cannot dereference nullpointer.")
        raise SeggerBackend.APIError(SeggerBackend.NrfjprogdllErr.INVALID_PARAMETER.value)
    return segger_backends[ctypes.cast(void_ptr, ctypes.POINTER(ctypes.c_uint)).contents.value]


def assert_secure_debug_available(segger_backend):
    ahb_ap_ctrl_status = segger_backend.read_access_port_register(ap_index=0, reg_addr=0)
    secure_debug = (ahb_ap_ctrl_status & (1 << 23))
    if not secure_debug:
        raise SeggerBackend.APIError(SeggerBackend.NrfjprogdllErr.NOT_AVAILABLE_BECAUSE_TRUST_ZONE.value)


def peripheral_is_secure(segger_backend, address):
    spu_addr = 0x50003000 | 0x800
    peri_id = (address & 0x000FF000) >> 12
    spu_periph_addr = spu_addr + (peri_id * 0x4)

    perm_value = segger_backend.ahb_read_u32(ap_index=0, addr=spu_periph_addr, secure_access=True)
    return (perm_value & 0x10) != 0  # Must cast to bool


def get_addr_with_secure_bit(addr, secure):
    if secure:
        return addr | 0x10000000
    else:
        return addr & 0xEFFFFFFF


def is_coprocessor_enabled_callback(user_defined, coprocessor, bool_ptr):
    global segger_backends
    logger.info("**** GOT IS_COPROCESSOR_ENABLED CALLBACK ****")
    logger.debug("User defined: 0x{:08X}".format(user_defined))
    logger.debug("coprocessor: {}".format(coprocessor))

    # Application core is always enabled
    if coprocessor == SeggerBackend.CoProcessor.CP_APPLICATION.value:
        bool_ptr[0] = True
        return SeggerBackend.NrfjprogdllErr.SUCCESS.value
    elif coprocessor != SeggerBackend.CoProcessor.CP_NETWORK:
        logger.error("Unrecognized coprocessor value for nRF53: {}."
                     "Expected {} or {}".format(coprocessor,
                                                SeggerBackend.CoProcessor.CP_APPLICATION,
                                                SeggerBackend.CoProcessor.CP_NETWORK))
        return SeggerBackend.NrfjprogdllErr.INVALID_PARAMETER.value

    try:
        # Get a handle to our segger backend
        segger_backend = get_segger_instance_from_user_defined(user_defined)

        # Assert secure debug is available. We can't check the SPU without.
        assert_secure_debug_available(segger_backend)

        # Read reset register security state
        app_reset_network = 0x50005000
        secure = peripheral_is_secure(segger_backend, app_reset_network)

        # Read forceoff and in_reset
        app_reset_network_reset_addr = get_addr_with_secure_bit(app_reset_network + 0x610, secure)
        app_reset_network_forceoff_addr = get_addr_with_secure_bit(app_reset_network + 0x614, secure)
        in_reset = segger_backend.ahb_read_u32(ap_index=0, addr=app_reset_network_reset_addr, secure_access=secure)
        in_forceoff = segger_backend.ahb_read_u32(ap_index=0, addr=app_reset_network_forceoff_addr,
                                                  secure_access=secure)

        # Store result
        bool_ptr[0] = (not in_reset and not in_forceoff)

    except SeggerBackend.APIError as ex:
        return ex.error_enum.value

    return SeggerBackend.NrfjprogdllErr.SUCCESS.value


def enable_coprocessor_callback(user_defined, coprocessor):
    global segger_backends
    logger.info("**** GOT ENABLE_COPROCESSOR CALLBACK! ****")
    logger.debug("User defined: 0x{:08X}".format(user_defined))
    logger.debug("coprocessor: {}".format(coprocessor))

    # Application core is always enabled
    if coprocessor == SeggerBackend.CoProcessor.CP_APPLICATION.value:
        return SeggerBackend.NrfjprogdllErr.SUCCESS.value
    elif coprocessor != SeggerBackend.CoProcessor.CP_NETWORK:
        logger.error("Unrecognized coprocessor value for nRF53: {}."
                     "Expected {} or {}".format(coprocessor,
                                                SeggerBackend.CoProcessor.CP_APPLICATION,
                                                SeggerBackend.CoProcessor.CP_NETWORK))
        return SeggerBackend.NrfjprogdllErr.INVALID_PARAMETER.value

    try:
        # Get a handle to our segger backend
        segger_backend = get_segger_instance_from_user_defined(user_defined)

        # Assert secure debug is available. We can't check the SPU without.
        assert_secure_debug_available(segger_backend)

        # Read reset register security state
        app_reset_network = 0x50005000
        secure = peripheral_is_secure(segger_backend, app_reset_network)

        # Release forceoff and reset
        app_reset_network_reset_addr = get_addr_with_secure_bit(app_reset_network + 0x610, secure)
        app_reset_network_forceoff_addr = get_addr_with_secure_bit(app_reset_network + 0x614, secure)
        segger_backend.ahb_write_u32(ap_index=0, addr=app_reset_network_reset_addr, data=0, secure_access=secure)
        segger_backend.ahb_write_u32(ap_index=0, addr=app_reset_network_forceoff_addr, data=0, secure_access=secure)

    except SeggerBackend.APIError as ex:
        return ex.error_enum.value

    return SeggerBackend.NrfjprogdllErr.SUCCESS.value


def nvmc_config_callback(user_defined, nvmc_mode):
    global segger_backends
    logger.debug("**** GOT NVMC_CONFIG_CALLBACK CALLBACK! ****")
    logger.debug("User defined: 0x{:08X}".format(user_defined))
    logger.debug("nvmc_mode: {}".format(nvmc_mode))

    # Not implemented

    return SeggerBackend.NrfjprogdllErr.SUCCESS.value


def nvmc_wait_for_ready_callback(user_defined):
    global segger_backends
    logger.debug("**** GOT NVMC_WAIT_FOR_READY CALLBACK! ****")
    logger.debug("User defined: 0x{:08X}".format(user_defined))

    # Not implemented

    return SeggerBackend.NrfjprogdllErr.SUCCESS.value


def get_init_params(selected_core, user_defined):
    result = dict()
    result["nvmc_config_cb"] = nvmc_config_callback
    result["nvmc_wait_for_ready_cb"] = nvmc_wait_for_ready_callback
    result["is_coprocessor_enabled_cb"] = is_coprocessor_enabled_callback
    result["enable_coprocessor_cb"] = enable_coprocessor_callback
    result["mem_access_fail_cb"] = None
    result["user_defined_cb_context"] = user_defined

    return result


def get_core_data_params(selected_core):
    result = dict()
    result["device_id"] = SeggerBackend.Parameters.JLinkCoreName.CORTEX_M33
    result["coprocessor"] = selected_core
    result["ahb_ap_index"] = 0 if selected_core == SeggerBackend.CoProcessor.CP_APPLICATION else 1
    result["expected_core"] = SeggerBackend.Parameters.JLinkCoreIndex.CORTEX_M33
    return result


def run(snr):
    global segger_backends

    logging.basicConfig(level=logging.DEBUG)

    # Add a placeholder to segger backends. Use the list index as user defined cb context
    segger_backends.append(None)
    segger_index = ctypes.c_int(len(segger_backends) - 1)
    user_defined_context = ctypes.byref(segger_index)

    selected_core = SeggerBackend.CoProcessor.CP_NETWORK
    init_params = get_init_params(selected_core, user_defined_context)

    # The segger backend will raise an APIError when a function has a non-zero return
    try:
        with SeggerBackend.SeggerBackend(close_all_segger_instances=False, **init_params) as segger_backend:
            # Set segger backend handle
            segger_backends[segger_index.value] = segger_backend

            # Read dll version and log
            major, minor, micro = segger_backend.dll_version()
            logger.info("JLink DLL version {}.{}.{}".format(major, minor, chr(micro)))

            # Connect to emu
            segger_backend.set_core_data(**get_core_data_params(selected_core))
            segger_backend.connect_to_emu_with_snr(snr)

            # Connect to core/device
            segger_backend.connect_to_device()

            # Halt cpu, then write and read back the program counter
            value = 0
            segger_backend.halt()
            segger_backend.write_cpu_register(SeggerBackend.Parameters.CpuRegister.PC, value)

            pc = segger_backend.read_cpu_register(SeggerBackend.CpuRegister.PC)
            logger.debug("Device has program counter: 0x{:08X}".format(pc))

            if value != pc:
                raise AssertionError("Device PC is different from written value!")

    # Ensure cleanup
    except Exception as ex:
        segger_backends[segger_index.value].close()
        raise ex


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--snr", required=True, type=int, help="Serial number of nrf5340 devkit")
    args = parser.parse_args()
    run(args.snr)
