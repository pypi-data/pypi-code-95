"""
This module serves as a Python wrapper around the jlinkarm_backend DLL.

Note: Please look at the jlinkarm_backenddll.h file provided with in the folder "documentation" for a more elaborate description of the API functions and their side effects.
"""

from __future__ import print_function
import ctypes
import os
import sys
import logging

from .APIError import *
from .Parameters import *

py2 = sys.version_info[0] == 2
py3 = sys.version_info[0] == 3
"""
Logging:
    The HighLevel module uses the python logging module for logging. The following log levels are used:
        DEBUG: Detailed messages about the executed instructions from all layers of nRFJProg and J-Link.
        INFO:  General progress messages from the HighLevel commands.
        ERROR: Error codes and exceptions.

    pynrfjprog performs no configuration of logger channels, but not all logging channels receive output by default.    
    ERROR logging is always performed, while DEBUG and INFO log messages can be suppressed to increase performance. 
    By setting log=False, the required callbacks are not passed to the library, disabling INFO and DEBUG level messages.    
"""

# Disable logging to API logger if no other handlers are present
logging.getLogger(__name__).addHandler(logging.NullHandler())


class SeggerBackend(object):
    _DEFAULT_JLINK_SPEED_KHZ = 2000

    def __init__(self, log=True, log_suffix="", jlink_arm_dll_path=None, nvmc_config_cb=None,
                 nvmc_wait_for_ready_cb=None, mem_access_fail_cb=None, is_coprocessor_enabled_cb=None,
                 enable_coprocessor_cb=None, user_defined_cb_context=None, close_all_segger_instances=False):
        """
        Constructor. If no jlink_arm_dll_path is provided the segger backend will try to auto-locate the jlink dll by
        looking in default locations.

        :param log: Enable logging to the python logging module
        :type log: bool, optional

        :param log_suffix: Suffix to append to logger module name
        :type log_suffix: str, optional

        :param jlink_arm_dll_path: File path to the jlink dll to use
        :type jlink_arm_dll_path: str, optional

        :param nvmc_config_cb: Callback function for configuring the NVMC. See c-type 'nvmc_config_ptr'
        :type nvmc_config_cb: Python function, optional

        :param nvmc_wait_for_ready_cb: Callback function that waits for NVMC to become ready. See c-type 'nvmc_wait_for_ready_ptr'
        :type nvmc_wait_for_ready_cb: Python function, optional

        :param mem_access_fail_cb: Callback function that handles memory access errors. See c-type mem_access_fail_ptr
        :type mem_access_fail_cb: Python function, optional

        :param is_coprocessor_enabled_cb: Callback function that checks if a coprocessor is enabled. See c-type is_coprocessor_enabled_ptr
        :type is_coprocessor_enabled_cb: Python function, optional

        :param enable_coprocessor_cb: Callback function that enables a given coprocessor. See c-type 'enable_coprocessor_ptr'
        :type enable_coprocessor_cb: Python function, optional

        :param user_defined_cb_context: Context passed to the callback functions as a void pointer.
        :type user_defined_cb_context: ctype.c_void_p, optional

        :param close_all_segger_instances: Close all segger backend instances after loading dll. Useful for terminating zombie segger backend sessions.
        :type close_all_segger_instances: bool, optional
        """
        # Init logger functionality. Set logging callback functions to None if log is not True
        _logger = logging.getLogger(__name__)
        self._logger = Parameters.LoggerAdapter(_logger, log_suffix, log=log)

        # Create callbacks. Save a copy of the function pointer to ensure it does not go out of scope and is
        # garbage collected
        self.nvmc_config_cb = nvmc_config_cb
        self.nvmc_config_cb_ctype = SeggerBackend._create_nvmc_config_callback(self.nvmc_config_cb)

        self.nvmc_wait_for_ready_cb = nvmc_wait_for_ready_cb
        self.nvmc_wait_for_ready_cb_ctype = SeggerBackend._create_nvmc_wait_for_ready_callback(
            self.nvmc_wait_for_ready_cb)

        self.mem_access_fail_cb = mem_access_fail_cb
        self.mem_access_fail_cb_ctype = SeggerBackend._create_mem_access_fail_callback(self.mem_access_fail_cb)

        self.is_coprocessor_enabled_cb = is_coprocessor_enabled_cb
        self.is_coprocessor_enabled_cb_ctype = SeggerBackend._create_is_coprocessor_enabled_callback(
            self.is_coprocessor_enabled_cb)

        self.enable_coprocessor_cb = enable_coprocessor_cb
        self.enable_coprocessor_cb_ctype = SeggerBackend._create_enable_coprocessor_callback(self.enable_coprocessor_cb)

        # Save user defined callback context
        self.user_defined_cb_context = user_defined_cb_context

        # Save jlink path
        self.jlink_arm_dll_path = str(jlink_arm_dll_path).encode('utf-8') if jlink_arm_dll_path is not None else None

        # Load the dll file
        self._load_dll()
        self._segger_backend_handle = ctypes.c_void_p(0)

        if close_all_segger_instances:
            num_closed_instances = self.close_all()
            self._logger.debug("Closed {} existing segger backend instances".format(num_closed_instances))

    def _load_dll(self):
        """
        Load the segger backend dll.
        """
        os_name = sys.platform.lower()

        if os_name.startswith('win'):
            jlinkarm_backend_dll_name = 'jlinkarm_backend.dll'
        elif os_name.startswith('lin'):
            jlinkarm_backend_dll_name = 'libjlinkarm_backend.so'
        elif os_name.startswith('dar'):
            jlinkarm_backend_dll_name = 'libjlinkarm_backend.dylib'
        else:
            raise Exception('Unsupported operating system!')

        jlinkarm_backend_dll_path = os.path.join(find_lib_dir(), jlinkarm_backend_dll_name)

        if not os.path.exists(jlinkarm_backend_dll_path):
            raise APIError(NrfjprogdllErr.NRFJPROG_SUB_DLL_NOT_FOUND, jlinkarm_backend_dll_path,
                           log=self._logger.error)

        try:
            self._lib = ctypes.cdll.LoadLibrary(jlinkarm_backend_dll_path)
        except Exception as ex:
            raise APIError(NrfjprogdllErr.NRFJPROG_SUB_DLL_COULD_NOT_BE_OPENED,
                           'Got error {} for library at {}'.format(repr(ex), jlinkarm_backend_dll_path),
                           log=self._logger.error)

    @staticmethod
    def _create_nvmc_config_callback(nvmc_config_cb):
        """
        Create a C-type function callback for nvmc_config_callback from a python function pointer
        nvmc_config_callback:
            typedef nrfjprogdll_err_t (*nvmc_config_callback)(void * const user_def, nvmc_ctrl_t nvmc_mode);

        :param nvmc_config_cb: Function handle to the python implementation of nvmc_config_callback
        :type nvmc_config_cb: Python function handle

        :return: C-compatible nvmc_config_callback function pointer
        :rtype: ctype callback pointer
        """
        if nvmc_config_cb is None:
            return ctypes.c_void_p(0)
        else:
            return ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_int)(nvmc_config_cb)

    @staticmethod
    def _create_nvmc_wait_for_ready_callback(nvmc_wait_for_ready_cb):
        """
        Create a C-type function callback for nvmc_wait_for_ready_callback from a python function pointer
        nvmc_wait_for_ready_callback:
            typedef nrfjprogdll_err_t (*nvmc_wait_for_ready_callback)(void * const user_def);

        :param nvmc_wait_for_ready_cb: Function handle to the python implementation of nvmc_wait_for_ready_callback
        :type nvmc_wait_for_ready_cb: Python function handle

        :return: C-compatible nvmc_wait_for_ready_callback function pointer
        :rtype: ctype callback pointer
        """
        if nvmc_wait_for_ready_cb is None:
            return ctypes.c_void_p(0)
        else:
            return ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p)(nvmc_wait_for_ready_cb)

    @staticmethod
    def _create_mem_access_fail_callback(mem_access_fail_cb):
        """
        Deprecated, always returns a null-pointer.

        :param mem_access_fail_cb: Function handle to the python implementation of mem_access_fail_callback
        :type mem_access_fail_cb: Python function handle

        :return: C-compatible mem_access_fail_callback function pointer
        :rtype: ctype callback pointer
        """
        return ctypes.c_void_p(0)

    @staticmethod
    def _create_is_coprocessor_enabled_callback(is_coprocessor_enabled_cb):
        """
        Create a C-type function callback for is_coprocessor_enabled_callback from a python function pointer
        is_coprocessor_enabled_callback:
            typedef nrfjprogdll_err_t (*is_coprocessor_enabled_callback)(void * const user_def,
                                                                        coprocessor_t coprocessor,
                                                                        bool * is_enabled);

        :param is_coprocessor_enabled_cb: Function handle to the python implementation of is_coprocessor_enabled_callback
        :type is_coprocessor_enabled_cb: Python function handle

        :return: C-compatible is_coprocessor_enabled_callback function pointer
        :rtype: ctype callback pointer
        """
        if is_coprocessor_enabled_cb is None:
            return ctypes.c_void_p(0)
        else:
            return ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_bool))(
                is_coprocessor_enabled_cb)

    @staticmethod
    def _create_enable_coprocessor_callback(enable_coprocessor_cb):
        """
        Create a C-type function callback for enable_coprocessor_callback from a python function pointer
        enable_coprocessor_callback:
            typedef nrfjprogdll_err_t (*enable_coprocessor_callback)(void * const user_def, coprocessor_t coprocessor);

        :param enable_coprocessor_cb: Function handle to the python implementation of enable_coprocessor_callback
        :type enable_coprocessor_cb: Python function handle

        :return: C-compatible enable_coprocessor_callback function pointer
        :rtype: ctype callback pointer
        """
        if enable_coprocessor_cb is None:
            return ctypes.c_void_p(0)
        else:
            return ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_int)(enable_coprocessor_cb)

    def __enter__(self):
        """
        Called automatically when the 'with' construct is used.
        """
        self.open()
        return self

    def __exit__(self, ex_type, ex_value, traceback):
        """
        Called automatically when the 'with' construct is used.
        """
        self.close()

    def open(self):
        """
        Open the segger backend and create a handle to a valid SEGGER backend instance.
        """
        result = self._lib.NRFJPROG_segger_open(ctypes.byref(self._segger_backend_handle),  # Instance pointer
                                                self.jlink_arm_dll_path,
                                                None,  # log to file (path)
                                                self._logger.log_cb,
                                                self.user_defined_cb_context,
                                                self.nvmc_config_cb_ctype,
                                                self.nvmc_wait_for_ready_cb_ctype,
                                                self.mem_access_fail_cb_ctype,
                                                self.is_coprocessor_enabled_cb_ctype,
                                                self.enable_coprocessor_cb_ctype
                                                )
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result, log=self._logger.error)

    def close(self):
        """
        Close and delete the segger backend instance
        """
        if self._segger_backend_handle is not None:
            result = self._lib.NRFJPROG_segger_close(ctypes.byref(self._segger_backend_handle))
            if result != NrfjprogdllErr.SUCCESS:
                raise APIError(result, log=self._logger.error)
            self._segger_backend_handle = None

    def close_all(self):
        """
        Close and delete all segger backend instances that are using the same DLL (instances in the same process)
        :return: Number of instances closed
        :rtype: int
        """
        num_instances_closed = ctypes.c_uint32(0)
        self._lib.NRFJPROG_segger_close_all(ctypes.byref(num_instances_closed))

        return num_instances_closed.value

    def dll_version(self):
        """
        Get the version number for the loaded JLink Dll (not jlinkarm_backend dll).

        :return: The major, minor and micro version of the JLinkARM DLL in use by the SeggerBackend
        :rtype: int, int, int
        """
        major = ctypes.c_uint32(0)
        minor = ctypes.c_uint32(0)
        micro = ctypes.c_uint32(0)
        result = self._lib.NRFJPROG_segger_dll_version(self._segger_backend_handle, ctypes.byref(major),
                                                       ctypes.byref(minor), ctypes.byref(micro))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result, log=self._logger.error)

        return major.value, minor.value, micro.value

    def lock(self):
        """
        Attempts to acquire the JLink DLL lock. Will always return false when not connected to an emulator.

        :return: Lock success
        :rtype: bool
        """
        result = self._lib.NRFJPROG_segger_lock(self._segger_backend_handle)
        if result == NrfjprogdllErr.SUCCESS:
            return True
        elif result == NrfjprogdllErr.JLINKARM_DLL_ERROR:
            return False
        else:
            raise APIError(result, log=self._logger.error)

    def unlock(self):
        """
        Attempt to release the segger backend lock. Will always return false when not connected to an emulator.

        :return: Unlock success
        :rtype: bool
        """
        result = self._lib.NRFJPROG_segger_unlock(self._segger_backend_handle)
        if result == NrfjprogdllErr.SUCCESS:
            return True
        elif result == NrfjprogdllErr.JLINKARM_DLL_ERROR:
            return False
        else:
            raise APIError(result, log=self._logger.error)

    def get_num_emus(self):
        """
        Get the number of emulators connected to the host PC.

        :return: The number of connected emulators
        :rtype: int
        """
        num_emulators = ctypes.c_uint32(0)

        result = self._lib.NRFJPROG_segger_get_num_emus(self._segger_backend_handle, ctypes.byref(num_emulators))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result, log=self._logger.error)

        return num_emulators.value

    def enum_emu_snr(self, max_num_serial_numbers=None):
        """
        Get a list of connected emulator serial numbers. If max_num_serial_numbers is not set the max_num_serial_numbers
        will be decided using get_num_emus().

        :param max_num_serial_numbers: The maximum number of emulator serial numbers to enumerate.
        :type max_num_serial_numbers: int, optional

        :return: A list of serial numbers
        :rtype: list of int
        """
        # If max_num_serial_numbers was provided, check that it is a valid uint32 value. If the variable is unset,
        # use the value from get_num_emus
        if max_num_serial_numbers is None:
            max_num_serial_numbers = self.get_num_emus()
        elif not is_u32(max_num_serial_numbers):
            raise ValueError('The max_num_serial_numbers parameter must be an unsigned 32-bit value.')

        num_snr_found = ctypes.c_uint32(0)
        max_num_snr = ctypes.c_uint32(max_num_serial_numbers)
        serial_number_array = (ctypes.c_uint32 * max_num_snr.value)()

        result = self._lib.NRFJPROG_segger_enum_emu_snr(self._segger_backend_handle, ctypes.byref(serial_number_array),
                                                        max_num_snr, ctypes.byref(num_snr_found))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result, log=self._logger.error)

        return serial_number_array[0:num_snr_found.value]

    def enum_emu_com(self, serial_number):
        """
        Finds all COM ports currently associated with the emulator serial number.

        :param serial_number: Serial number of the debug probe to find the com port of.
        :type serial_number: int

        :return: A list of the enumerated com ports
        :rtype: list of ComPortInfo
        """
        if not is_u32(serial_number):
            raise ValueError('The serial_number parameter must be an unsigned 32-bit value.')

        serial_number = ctypes.c_uint32(serial_number)
        num_com_ports = ctypes.c_uint32()
        com_ports_len = ctypes.c_uint32(NRFJPROG_COM_PER_JLINK)
        com_ports = (ComPortInfoStruct * NRFJPROG_COM_PER_JLINK)()

        result = self._lib.NRFJPROG_segger_enum_emu_com(self._segger_backend_handle,
                                                        serial_number, ctypes.byref(com_ports), com_ports_len,
                                                        ctypes.byref(num_com_ports))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return [ComPortInfo(comport) for comport in com_ports[0:num_com_ports.value]]

    def is_connected_to_emu(self):
        """
        Check if connected to an emulator.

        :return: True if connected to an emulator
        :rtype: bool
        """
        is_connected_to_emu = ctypes.c_bool(False)

        result = self._lib.NRFJPROG_segger_is_open(self._segger_backend_handle,
                                                   ctypes.byref(is_connected_to_emu))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result, log=self._logger.error)

        return is_connected_to_emu.value

    def connect_to_emu_with_snr(self, serial_number, jlink_speed_khz=_DEFAULT_JLINK_SPEED_KHZ):
        """
        Connect to the emulator with the given 'serial_number'.
        Before connecting remember to set core data, see :func:`~SeggerBackend.SeggerBackend.set_core_data`.

        :param serial_number: Serial number of the emulator to connect to.
        :type serial_number: int
        :param jlink_speed_khz: SWDCLK speed [kHz].
        :type jlink_speed_khz: int
        """
        if not is_u32(serial_number):
            raise ValueError('The serial_number parameter must be an unsigned 32-bit value.')

        if not is_u32(jlink_speed_khz):
            raise ValueError('The jlink_speed_khz parameter must be an unsigned 32-bit value.')

        serial_number = ctypes.c_uint32(serial_number)
        jlink_speed_khz = ctypes.c_uint32(jlink_speed_khz)

        result = self._lib.NRFJPROG_segger_connect_to_emu_with_snr(self._segger_backend_handle, serial_number,
                                                                   jlink_speed_khz)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def connect_to_emu_without_snr(self, jlink_speed_khz=_DEFAULT_JLINK_SPEED_KHZ):
        """
        Connect to an emulator without specifying a serial number. If there is more than 1 emulator to choose from, an
        interactive selection window is launched.
        Before connecting remember to set core data, see :func:`~SeggerBackend.SeggerBackend.set_core_data`.

        :param jlink_speed_khz: SWDCLK speed [kHz].
        :type jlink_speed_khz: int
        """
        if not is_u32(jlink_speed_khz):
            raise ValueError('The jlink_speed_khz parameter must be an unsigned 32-bit value.')

        jlink_speed_khz = ctypes.c_uint32(jlink_speed_khz)

        result = self._lib.NRFJPROG_segger_connect_to_emu_without_snr(self._segger_backend_handle, jlink_speed_khz)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def disconnect_from_emu(self):
        """
        Disconnect from the connected emulator. Calling this function when no emulator is connected has no effect.
        """
        result = self._lib.NRFJPROG_segger_disconnect_from_emu(self._segger_backend_handle)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def reset_connected_emu(self):
        """
        Reset the connected emulator. This command is specific for the "J-Link OB-SAM3U128-V2-NordicSemi" emulator,
        i.e. nRF53, nRF91, and nRF52820 DKs does NOT support this.
        """
        result = self._lib.NRFJPROG_segger_reset_connected_emu(self._segger_backend_handle)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def replace_connected_emu_fw(self):
        """
        Replace the firmware of the connected emulator. The version supplied by the loaded JLink DLL is programmed to
        the emulator regardless of it's current firmware version.
        """
        result = self._lib.NRFJPROG_segger_replace_connected_emu_fw(self._segger_backend_handle)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def read_connected_emu_snr(self):
        """
        Read the serial number of the connected emulator.

        :return: Emulator serial number.
        :rtype: int
        """
        snr = ctypes.c_uint32()

        result = self._lib.NRFJPROG_segger_read_connected_emu_snr(self._segger_backend_handle, ctypes.byref(snr))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return snr.value

    def read_connected_emu_fwstr(self):
        """
        Read the firmware identification string of the connected emulator.

        :return: firmware identification string.
        :rtype: str
        """
        buffer_size = ctypes.c_uint32(255)
        firmware_string = ctypes.create_string_buffer(buffer_size.value)

        result = self._lib.NRFJPROG_segger_read_connected_emu_fwstr(self._segger_backend_handle, firmware_string,
                                                                    buffer_size)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        if py2:
            return firmware_string.value
        else:
            return firmware_string.value.decode('utf-8')

    def is_connected_to_device(self):
        """
        Checks if the connected emulator has an established connection with an nRF device.

        :return: True if connected.
        :rtype: bool
        """
        is_connected_to_device = ctypes.c_bool()

        result = self._lib.NRFJPROG_segger_is_connected_to_device(self._segger_backend_handle,
                                                                  ctypes.byref(is_connected_to_device))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return is_connected_to_device.value

    def disconnect_from_device(self):
        """
        Disconnect from the connected device.
        """
        result = self._lib.NRFJPROG_segger_disconnect_from_device(self._segger_backend_handle)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def set_core_data(self, device_id, coprocessor, ahb_ap_index, expected_core=Parameters.JLinkCoreIndex.NONE):
        """
        Sets the connection information used when connecting to an emulator, and later when connecting to an nRF device.

        :param device_id: The SEGGER id name for the device or core to connect to. See enum :class:`~Parameters.JLinkCoreName`.
        :type device_id: str or JLinkCoreName
        :param coprocessor: Index of the coprocessor to connect to. This will be passed to the enable coprocessor callback. See enum :class:`~Parameters.CoProcessor`
        :type coprocessor: CoProcessor
        :param ahb_ap_index:  AHB index of the core.
        :type ahb_ap_index: int
        :param expected_core: What core to expect when connecting to the device. See enum :class:`~Parameters.JLinkCoreIndex`
        :type expected_core: int or JLinkCoreIndex
        """
        if is_enum(device_id, JLinkCoreName):
            device_id = decode_enum(device_id, JLinkCoreName).value
        elif not isinstance(device_id, str):
            raise ValueError('Parameter expected_core must of type str or JLinkCoreName enumeration.')

        if is_enum(expected_core, JLinkCoreIndex):
            expected_core = decode_enum(expected_core, JLinkCoreIndex).value
        elif not is_u32(expected_core):
            raise ValueError(
                'Parameter expected_core must of an unsigned 32-bit integer or a JLinkCoreIndex enumeration.')

        if not is_enum(coprocessor, CoProcessor):
            raise TypeError('Parameter direction must be of type int, str or CoProcessor enumeration.')

        if not is_u8(ahb_ap_index):
            raise TypeError('The ahb_ap_index parameter must be an unsigned 8-bit value.')

        device_id = device_id.encode('utf-8')
        expected_core = ctypes.c_uint32(expected_core)
        coprocessor = ctypes.c_int(decode_enum(coprocessor, CoProcessor))
        ahb_ap_index = ctypes.c_uint8(ahb_ap_index)

        result = self._lib.NRFJPROG_segger_set_core_data(self._segger_backend_handle, device_id, expected_core,
                                                         coprocessor, ahb_ap_index)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def connect_to_device(self):
        """
        Connects to the nRF device.
        Requires that you have connected to an emulator and have set the appropriate core data. See function
        :func:`~SeggerBackend.SeggerBackend.connect_to_emu_with_snr` and
        :func:`~SeggerBackend.SeggerBackend.connect_to_emu_without_snr`

        """
        result = self._lib.NRFJPROG_segger_connect_to_device(self._segger_backend_handle)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def sys_reset(self):
        """
        Executes a system reset request on the connected device.

        """
        result = self._lib.NRFJPROG_segger_sys_reset(self._segger_backend_handle)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def pin_reset(self):
        """
        Executes a pin reset on the connected device. If your device has a configurable pin reset the it must be
        enabled in the UICR.PSELRESET[] device registers. Note that nRF51 has a separate pin_reset function, see
        :func:`~SeggerBackend.SeggerBackend.nrf51_pin_reset`.

        """
        result = self._lib.NRFJPROG_segger_pin_reset(self._segger_backend_handle)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def is_halted(self):
        """
        Checks if the device CPU is halted.

        :return: True if halted.
        :rtype: bool
        """
        is_halted = ctypes.c_bool()

        result = self._lib.NRFJPROG_segger_is_halted(self._segger_backend_handle, ctypes.byref(is_halted))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return is_halted.value

    def halt(self):
        """
        Halts the device CPU.

        """
        result = self._lib.NRFJPROG_segger_halt(self._segger_backend_handle)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def run(self, pc, sp):
        """
        Starts the device CPU with the given program counter and stack pointer.

        :param pc: Program counter value
        :type pc: int
        :param sp: Stackpointer value
        :type sp: int
        :return:
        """
        if not is_u32(pc):
            raise ValueError('The pc parameter must be an unsigned 32-bit value.')

        if not is_u32(sp):
            raise ValueError('The sp parameter must be an unsigned 32-bit value.')

        pc = ctypes.c_uint32(pc)
        sp = ctypes.c_uint32(sp)

        result = self._lib.NRFJPROG_segger_run(self._segger_backend_handle, pc, sp)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def go(self):
        """
        Starts the device CPU.

        """
        result = self._lib.NRFJPROG_segger_go(self._segger_backend_handle)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def step(self):
        """
        Runs the device CPU for one instruction.

        """
        result = self._lib.NRFJPROG_segger_step(self._segger_backend_handle)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def nrf51_disable_system_off(self):
        """
        Bring an nRF51 device out of system off mode.

        """
        result = self._lib.NRFJPROG_segger_nRF51_disable_system_off(self._segger_backend_handle)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def nrf51_pin_reset(self):
        """
        Perform an nRF51 pin reset.
        """
        result = self._lib.NRFJPROG_segger_nRF51_pin_reset(self._segger_backend_handle)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def write_u32(self, addr, data, nvmc_control, halting=False):
        """
        Writes one uint32_t data into the given addr.

        :param addr: addr to write
        :type addr: int
        :param data: Value to write
        :type data: int
        :param nvmc_control: Do a nvmc_control callback before the write operation
        :type nvmc_control: bool
        :param halting: Halt the core before the write operation
        :type halting: bool
        """
        if not is_u32(addr):
            raise ValueError('The addr parameter must be an unsigned 32-bit value.')

        if not is_u32(data):
            raise ValueError('The data parameter must be an unsigned 32-bit value.')

        if not is_bool(nvmc_control):
            raise ValueError('The nvmc_control parameter must be a boolean value.')

        if not is_bool(halting):
            raise ValueError('The halting parameter must be a boolean value.')

        addr = ctypes.c_uint32(addr)
        data = ctypes.c_uint32(data)
        nvmc_control = ctypes.c_bool(nvmc_control)
        halting = ctypes.c_bool(halting)

        result = self._lib.NRFJPROG_segger_write_u32(self._segger_backend_handle, addr, data, nvmc_control, halting)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def read_u32(self, addr, halting=False):
        """
        Reads one uint32_t from the given addr.

        :param addr: addr to read.
        :type addr: int
        :param halting: Halt the core before the read operation
        :type halting: bool

        :return: Value read.
        :rtype: int
        """
        if not is_u32(addr):
            raise ValueError('The addr parameter must be an unsigned 32-bit value.')

        if not is_bool(halting):
            raise ValueError("The halting parameter must be a boolean value")

        addr = ctypes.c_uint32(addr)
        data = ctypes.c_uint32()
        halting = ctypes.c_bool(halting)

        result = self._lib.NRFJPROG_segger_read_u32(self._segger_backend_handle, addr, ctypes.byref(data), halting)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return data.value

    def write(self, addr, data, nvmc_control, halting=False):
        """
        Writes data from the array into the device starting at the given addr.

        :param addr: addr to write
        :type addr: int
        :param data: Data to write
        :type data: Iterable (string, list, bytearray ...)
        :param nvmc_control: Do an nvmc_control callback before the write operation
        :type nvmc_control: bool
        :param halting: Halt the core before the write operation
        :type halting: bool
        """

        if not is_u32(addr):
            raise ValueError('The addr parameter must be an unsigned 32-bit value.')

        if not is_valid_buf(data):
            raise ValueError('The data parameter must be a sequence type with at least one item.')

        if not is_bool(nvmc_control):
            raise ValueError('The nvmc_control parameter must be a boolean value.')

        if not is_bool(halting):
            raise ValueError('The halting parameter must be a boolean value.')

        addr = ctypes.c_uint32(addr)
        data_len = ctypes.c_uint32(len(data))
        data = (ctypes.c_uint8 * data_len.value)(*data)
        nvmc_control = ctypes.c_bool(nvmc_control)
        halting = ctypes.c_bool(halting)

        result = self._lib.NRFJPROG_segger_write(self._segger_backend_handle, addr, ctypes.byref(data), data_len,
                                                 nvmc_control, halting)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def read(self, addr, data_len, halting=False):
        """
        Read 'num_words' starting at 'addr'. If 'halting' is True, the core will be halted before reading.

        :param addr: Start addr of the memory block to read.
        :type addr: int
        :param data_len: Number of bytes to read.
        :type data_len: int
        :param halting: Halt the core before the read operation
        :type halting: bool

        :return: List of the read values.
        :rtype: list of int
        """
        if not is_u32(addr):
            raise ValueError('The addr parameter must be an unsigned 32-bit value.')

        if not is_u32(data_len):
            raise ValueError('The data_len parameter must be an unsigned 32-bit value.')

        if not is_bool(halting):
            raise ValueError("The halting parameter must be a boolean value")

        addr = ctypes.c_uint32(addr)
        data_len = ctypes.c_uint32(data_len)
        data = (ctypes.c_uint8 * data_len.value)()
        halting = ctypes.c_bool(halting)

        result = self._lib.NRFJPROG_segger_read(self._segger_backend_handle, addr, ctypes.byref(data), data_len,
                                                halting)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return list(data)

    def ahb_read_u32(self, ap_index, addr, secure_access):
        """
        Read one uint32_t from the given addr, using the AHB access port denoted by index 'ap_index'. Unlike
        :func:`~SeggerBackend.SeggerBackend.read_u32`, this function will not connect to the device CPU.

        :param ap_index: Access Port index
        :type ap_index: int
        :param addr: addr to read
        :type addr: int
        :param secure_access: Make a secure access
        :type secure_access: bool

        :return: Value read
        :rtype: int
        """
        if not is_u8(ap_index):
            raise ValueError('The ap_index parameter must be an unsigned 8-bit value.')

        if not is_u32(addr):
            raise ValueError('The addr parameter must be an unsigned 32-bit value.')

        if not is_bool(secure_access):
            raise ValueError("The secure_access parameter must be a boolean value")

        addr = ctypes.c_uint32(addr)
        data = ctypes.c_uint32()
        secure_access = ctypes.c_bool(secure_access)

        result = self._lib.NRFJPROG_segger_ahb_read_u32(self._segger_backend_handle, ap_index, addr,
                                                        ctypes.byref(data),
                                                        secure_access)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return data.value

    def ahb_write_u32(self, ap_index, addr, data, secure_access):
        """
        Write one uint32_t to an access port register, using the AHB access port denoted by index 'ap_index'. Unlike
        :func:`~SeggerBackend.SeggerBackend.write_u32`, this function will not connect to the device CPU.

        :param ap_index: Access Port index
        :type ap_index: int
        :param addr: Address to write
        :type addr: int
        :param data: Value to write
        :type data: int
        :param secure_access: Make a secure access
        :type secure_access: bool
        """
        if not is_u8(ap_index):
            raise TypeError('The ap_index parameter must be an unsigned 8-bit value.')

        if not is_u32(addr):
            raise ValueError('The addr parameter must be an unsigned 32-bit value.')

        if not is_u32(data):
            raise ValueError('The data parameter must be an unsigned 32-bit value.')

        if not is_bool(secure_access):
            raise ValueError('The halting parameter must be a boolean value.')

        ap_index = ctypes.c_uint8(ap_index)
        addr = ctypes.c_uint32(addr)
        data = ctypes.c_uint32(data)

        result = self._lib.NRFJPROG_segger_ahb_write_u32(self._segger_backend_handle, ap_index, addr,
                                                         data, secure_access)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def ahb_write(self, ap_index, addr, data, secure_access):
        """
        Write one uint32_t to an access port register, using the AHB access port denoted by index 'ap_index'. Unlike
        :func:`~SeggerBackend.SeggerBackend.write`, this function will not connect to the device CPU.

        :param ap_index: Access Port index
        :type ap_index: int
        :param addr: Address to write
        :type addr: int
        :param data: Data to write
        :type data: Iterable (string, list, bytearray ...)
        :param secure_access: Make a secure access
        :type secure_access: bool
        """
        if not is_u8(ap_index):
            raise TypeError('The ap_index parameter must be an unsigned 8-bit value.')

        if not is_u32(addr):
            raise ValueError('The addr parameter must be an unsigned 32-bit value.')

        if not is_valid_buf(data):
            raise ValueError('The data parameter must be a sequence type with at least one item.')

        if not is_bool(secure_access):
            raise ValueError('The halting parameter must be a boolean value.')

        ap_index = ctypes.c_uint8(ap_index)
        addr = ctypes.c_uint32(addr)
        data_len = ctypes.c_uint32(len(data))
        data = (ctypes.c_uint8 * data_len.value)(*data)

        result = self._lib.NRFJPROG_segger_ahb_write(self._segger_backend_handle, ap_index, addr,
                                                     ctypes.byref(data), data_len, secure_access)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def read_debug_port_register(self, addr):
        """
        Reads a debug port register.

        :param addr: Address to read
        :type addr: int

        :return: Value read
        :rtype: int
        """
        if not is_u8(addr):
            raise ValueError('The addr parameter must be an unsigned 8-bit value.')

        addr = ctypes.c_uint8(addr)
        data = ctypes.c_uint32()

        result = self._lib.NRFJPROG_segger_read_debug_port_register(self._segger_backend_handle, addr,
                                                                    ctypes.byref(data))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return data.value

    def write_debug_port_register(self, addr, data):
        """
        Writes a debug port register.

        :param addr: Address to write
        :type addr: int
        :param data: Value to write.
        :type data:: int
        """
        if not is_u8(addr):
            raise ValueError('The addr parameter must be an unsigned 8-bit value.')

        if not is_u32(data):
            raise ValueError('The data parameter must be an unsigned 32-bit value.')

        addr = ctypes.c_uint8(addr)
        data = ctypes.c_uint32(data)

        result = self._lib.NRFJPROG_segger_write_debug_port_register(self._segger_backend_handle, addr, data)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def read_debug_port_register_idr(self):
        """
        Reads the debug port IDR (Identification Register)

        :return: IDR value, revision, part number, JEDEC manufacturer
        :rtype: int, int, int, str
        """
        idr = ctypes.c_uint32(0)
        revision = ctypes.c_uint8(0)
        partno = ctypes.c_uint8(0)
        jdec_manufacturer = ctypes.c_int()

        result = self._lib.NRFJPROG_segger_read_debug_port_idr(self._segger_backend_handle, ctypes.byref(idr),
                                                               ctypes.byref(revision), ctypes.byref(partno),
                                                               ctypes.pointer(jdec_manufacturer))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return idr.value, revision.value, partno.value, JEDECManufacturer(jdec_manufacturer.value).name

    def read_access_port_register(self, ap_index, reg_addr):
        """
        Reads a debugger access port register.

        :param ap_index: Index of the access port to read
        :type ap_index: int
        :param reg_addr: Address of register to read
        :type reg_addr: int

        :return: Value read
        :rtype: int
        """
        if not is_u8(ap_index):
            raise ValueError('The ap_index parameter must be an unsigned 8-bit value.')

        if not is_u8(reg_addr):
            raise ValueError('The reg_addr parameter must be an unsigned 8-bit value.')

        ap_index = ctypes.c_uint8(ap_index)
        reg_addr = ctypes.c_uint8(reg_addr)
        data = ctypes.c_uint32()

        result = self._lib.NRFJPROG_segger_read_access_port_register(self._segger_backend_handle, ap_index, reg_addr,
                                                                     ctypes.byref(data))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return data.value

    def write_access_port_register(self, ap_index, reg_addr, data):
        """
        Writes a debugger access port register.

        :param ap_index: Index of the access port to write
        :type ap_index: int
        :param reg_addr: Address of register to write
        :type reg_addr: int
        :param data: Value to write
        :type data: int
        """
        if not is_u8(ap_index):
            raise ValueError('The ap_index parameter must be an unsigned 8-bit value.')

        if not is_u8(reg_addr):
            raise ValueError('The reg_addr parameter must be an unsigned 8-bit value.')

        if not is_u32(data):
            raise ValueError('The data parameter must be an unsigned 32-bit value.')

        ap_index = ctypes.c_uint8(ap_index)
        reg_addr = ctypes.c_uint8(reg_addr)
        data = ctypes.c_uint32(data)

        result = self._lib.NRFJPROG_segger_write_access_port_register(self._segger_backend_handle, ap_index, reg_addr,
                                                                      data)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def read_access_port_idr(self, ap_index):
        """
        Reads the access port IDR (Identification Register)

        :param ap_index: Index of the access port to write
        :type ap_index: int

        :return: idr, revision, manufacturer, is_memory_AP, identity
        :rtype: int, int, str, bool, int
        """
        if not is_u8(ap_index):
            raise ValueError('The ap_index parameter must be an unsigned 8-bit value.')

        ap_index = ctypes.c_uint8(ap_index)
        idr = ctypes.c_uint32(0)
        revision = ctypes.c_uint8(0)
        jedec_manufacturer = ctypes.c_int(0)
        memory_ap = ctypes.c_bool(0)
        identity = ctypes.c_uint8(0)

        result = self._lib.NRFJPROG_segger_read_access_port_idr(self._segger_backend_handle, ap_index, ctypes.byref(idr)
                                                                , ctypes.byref(revision),
                                                                ctypes.byref(jedec_manufacturer),
                                                                ctypes.byref(memory_ap), ctypes.byref(identity))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return idr.value, revision.value, JEDECManufacturer(
            jedec_manufacturer.value).name, memory_ap.value, identity.value

    def read_cpu_register(self, register_name):
        """
        Reads a CPU register.

        :param register_name: CPU register to read.
        :type register_name: int, str, or CPURegister(IntEnum)
        :return: Value read
        :rtype: int
        """
        if not is_enum(register_name, CpuRegister):
            raise ValueError('Parameter register_name must be of type int, str or CpuRegister enumeration.')

        register_name = decode_enum(register_name, CpuRegister)
        if register_name is None:
            raise ValueError('Parameter register_name must be of type int, str or CpuRegister enumeration.')

        register_name = ctypes.c_int(register_name.value)
        value = ctypes.c_uint32()

        result = self._lib.NRFJPROG_segger_read_cpu_register(self._segger_backend_handle, register_name,
                                                             ctypes.byref(value))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return value.value

    def write_cpu_register(self, register_name, value):
        """
        Writes a CPU register.

        :param register_name: CPU register to read.
        :type register_name: int, str, or CPURegister(IntEnum)
        :param value: Value to write
        :type value: int
        """
        if not is_u32(value):
            raise ValueError('The value parameter must be an unsigned 32-bit value.')

        if not is_enum(register_name, CpuRegister):
            raise ValueError('Parameter register_name must be of type int, str or CpuRegister enumeration.')

        register_name = decode_enum(register_name, CpuRegister)
        if register_name is None:
            raise ValueError('Parameter register_name must be of type int, str or CpuRegister enumeration.')

        register_name = ctypes.c_int(register_name.value)
        value = ctypes.c_uint32(value)

        result = self._lib.NRFJPROG_segger_write_cpu_register(self._segger_backend_handle, register_name, value)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def is_rtt_started(self):
        """
        Checks if the RTT is started.

        :return: True if started.
        :rtype: bool
        """
        started = ctypes.c_bool()

        result = self._lib.NRFJPROG_segger_is_rtt_started(self._segger_backend_handle, ctypes.byref(started))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return started.value

    def rtt_start(self):
        """
        Starts RTT.
        Remember to set the RTT range before attempting rtt_start. See function :func:`~SeggerBackend.SeggerBackend.set_rtt_range`
        """
        result = self._lib.NRFJPROG_segger_rtt_start(self._segger_backend_handle)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def rtt_set_control_block_address(self, addr):
        """
        Indicates to the dll the location of the RTT control block in the device memory.

        :param addr: Address of the RTT Control Block in memory
        :type addr: int
        """
        if not is_u32(addr):
            raise ValueError('The address parameter must be an unsigned 32-bit value.')

        addr = ctypes.c_uint32(addr)

        result = self._lib.NRFJPROG_segger_rtt_set_control_block_address(self._segger_backend_handle, addr)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def rtt_is_control_block_found(self):
        """
        Checks if RTT control block has been found.

        :return: True if RTT control block found
        :rtype: bool
        """
        is_control_block_found = ctypes.c_bool()

        result = self._lib.NRFJPROG_segger_rtt_is_control_block_found(self._segger_backend_handle,
                                                                      ctypes.byref(is_control_block_found))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return is_control_block_found.value

    def rtt_stop(self):
        """
        Stops RTT.

        """
        result = self._lib.NRFJPROG_segger_rtt_stop(self._segger_backend_handle)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def rtt_read(self, channel_index, length, encoding='utf-8'):
        """
        Reads from an RTT channel.

        :param channel_index: RTT channel to read.
        :type channel_index: int
        :param length: Number of bytes to read. Note that depending on the encoding parameter, the number of bytes read and the numbers of characters read might differ.
        :type length: int
        :param encoding: Encoding for the data read in order to build a readable string. Default value 'utf-8'. Note that since Python2 native string is coded in ASCII, only ASCII characters will be properly represented.
        :type encoding: str or None, optional
        :return: Data read
        :rtype: str or bytearray. Return type depends on encoding optional parameter. If an encoding is given, the return type will be Python version's native string type. If None is given, a bytearray will be returned.
        """
        if not is_u32(channel_index):
            raise ValueError('The channel_index parameter must be an unsigned 32-bit value.')

        if not is_u32(length):
            raise ValueError('The length parameter must be an unsigned 32-bit value.')

        if encoding is not None and not is_valid_encoding(encoding):
            raise ValueError('The encoding parameter must be either None or a standard encoding in python.')

        channel_index = ctypes.c_uint32(channel_index)
        length = ctypes.c_uint32(length)
        data = (ctypes.c_uint8 * length.value)()
        data_read = ctypes.c_uint32()

        result = self._lib.NRFJPROG_segger_rtt_read(self._segger_backend_handle, channel_index, ctypes.byref(data),
                                                    length, ctypes.byref(data_read))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        if py2:
            return bytearray(data[0:data_read.value]) if encoding is None else bytearray(
                data[0:data_read.value]).decode(encoding).encode('utf-8')
        else:
            return bytearray(data[0:data_read.value]).decode(encoding)

    def rtt_write(self, channel_index, msg, encoding='utf-8'):
        """
        Writes to an RTT channel.

        :param channel_index: RTT channel to write
        :rtype channel_index: int
        :param msg: Data to write.
        :type msg: iterable (i.e. string, list, bytearray...)
        :param encoding: Encoding of the msg to write. Default value 'utf-8'
        :type encoding: str og None, optional
        :return: Number of bytes written. Note that if non-'latin-1' characters are used, the number of bytes written depends on the encoding parameter given.
        :rtype: int
        """
        if not is_u32(channel_index):
            raise ValueError('The channel_index parameter must be an unsigned 32-bit value.')

        if encoding is not None and not is_valid_encoding(encoding):
            raise ValueError('The encoding parameter must be either None or a standard encoding in python.')

        msg = bytearray(msg.encode(encoding)) if encoding else bytearray(msg)
        if not is_valid_buf(msg):
            raise ValueError('The msg parameter must be a sequence type with at least one item.')

        channel_index = ctypes.c_uint32(channel_index)
        length = ctypes.c_uint32(len(msg))
        data = (ctypes.c_uint8 * length.value)(*msg)
        data_written = ctypes.c_uint32()

        result = self._lib.NRFJPROG_segger_rtt_write(self._segger_backend_handle, channel_index, ctypes.byref(data),
                                                     length, ctypes.byref(data_written))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return data_written.value

    def rtt_read_channel_count(self):
        """
        Gets the number of RTT channels.

        :return: Tuple containing the number of down RTT channels and the number of up RTT channels.
        :rtype: int, int
        """
        down_channel_number = ctypes.c_uint32()
        up_channel_number = ctypes.c_uint32()

        result = self._lib.NRFJPROG_segger_rtt_read_channel_count(self._segger_backend_handle,
                                                                  ctypes.byref(down_channel_number),
                                                                  ctypes.byref(up_channel_number))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return down_channel_number.value, up_channel_number.value

    def rtt_read_channel_info(self, channel_index, direction):
        """
        Reads the info of one RTT channel.

        :param channel_index: RTT channel to request info
        :type channel_index: int
        :param direction: Direction of the channel to request info.
        :type direction: int, str, or RTTChannelDirection(IntEnum)
        :return: Tuple containing the channel name and the size of channel buffer.
        :rtype: str, int
        """
        if not is_u32(channel_index):
            raise ValueError('The channel_index parameter must be an unsigned 32-bit value.')

        if not is_enum(direction, RTTChannelDirection):
            raise ValueError('Parameter direction must be of type int, str or RTTChannelDirection enumeration.')

        direction = decode_enum(direction, RTTChannelDirection)
        if direction is None:
            raise ValueError('Parameter direction must be of type int, str or RTTChannelDirection enumeration.')

        channel_index = ctypes.c_uint32(channel_index)
        direction = ctypes.c_int(direction.value)
        name_len = ctypes.c_uint32(32)
        name = (ctypes.c_uint8 * 32)()
        size = ctypes.c_uint32()

        result = self._lib.NRFJPROG_segger_rtt_read_channel_info(self._segger_backend_handle, channel_index, direction,
                                                                 ctypes.byref(name), name_len, ctypes.byref(size))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return ''.join(chr(i) for i in name if i != 0), size.value

    def set_rtt_range(self, addr, mem_size):
        """
        Sets the address search range used when searching for the RTT start block.

        :param addr: Address to the start of the RTT block
        :type addr: int
        :param mem_size: Size of the RTT memory block
        """
        if not is_u32(addr):
            raise ValueError('The addr parameter must be an unsigned 32-bit value.')

        if not is_u32(mem_size):
            raise ValueError('The mem_size parameter must be an unsigned 32-bit value.')

        addr = ctypes.c_uint32(addr)
        mem_size = ctypes.c_uint32(mem_size)

        result = self._lib.NRFJPROG_segger_set_rtt_range(self._segger_backend_handle, addr, mem_size)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)
