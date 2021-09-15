# pylint: disable=I0011,W0312,C0301,C0103,W0123,W1202,C0326,C0111,R0911,R0913,R0914
import logging
import threading
from exoedge import logger
from pymodbus.client.sync import ModbusTcpClient, ModbusSerialClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian
from pymodbus.exceptions import ModbusException

LOG = logger.getLogger(__name__, level=logging.getLogger('exoedge').getEffectiveLevel())

# RANGES = {
#     'RANGE_FLOAT_32'  : { 'low': -2.0**31, 'high': 2.0**31-1, 'fits_into': 2},
#     'RANGE_FLOAT_64'  : { 'low': -2.0**63, 'high':2.0**63-1,  'fits_into': 4},
#     'RANGE_INT_8'     : { 'low': -2**7,    'high':2**7-1,     'fits_into': 0.5},
#     'RANGE_INT_16'    : { 'low': -2**15,   'high':2**15-1,    'fits_into': 1},
#     'RANGE_INT_32'    : { 'low': -2**31,   'high':2**31-1,    'fits_into': 2},
#     'RANGE_INT_64'    : { 'low': -2**63,   'high':2**63-1,    'fits_into': 4},
#     'RANGE_UINT_8'    : { 'low': 0,        'high': 2**8-1,    'fits_into': 0.5},
#     'RANGE_UINT_16'   : { 'low': 0,        'high': 2**16-1,   'fits_into': 1},
#     'RANGE_UINT_32'   : { 'low': 0,        'high': 2**32-1,   'fits_into': 2},
#     'RANGE_UINT_64'   : { 'low': 0,        'high': 2**64-1,   'fits_into': 4},
# }

RANGES = {
    "RANGE_UINT_8": {
        "high": 255,
        "fits_into": 0.5,
        "low": 0
    },
    "RANGE_INT_8": {
        "high": 127,
        "fits_into": 0.5,
        "low": -128
    },
    "RANGE_UINT_64": {
        "high": 18446744073709551615,
        "fits_into": 4,
        "low": 0
    },
    "RANGE_INT_32": {
        "high": 2147483647,
        "fits_into": 2,
        "low": -2147483648
    },
    "RANGE_UINT_32": {
        "high": 4294967295,
        "fits_into": 2,
        "low": 0
    },
    "RANGE_INT_16": {
        "high": 32767,
        "fits_into": 1,
        "low": -32768
    },
    "RANGE_FLOAT_32": {
        "high": 2147483647.0,
        "fits_into": 2,
        "low": -2147483648.0
    },
    "RANGE_UINT_16": {
        "high": 65535,
        "fits_into": 1,
        "low": 0
    },
    "RANGE_INT_64": {
        "high": 9223372036854775807,
        "fits_into": 4,
        "low": -9223372036854775808
    },
    "RANGE_FLOAT_64": {
        "high": 9.223372036854776e+18,
        "fits_into": 4,
        "low": -9.223372036854776e+18
    }
}

REGISTER_NUMBER_MAP = {
    "INPUT_COIL": {
        "range": range(0, 10000),
        "method": "read_coils",
    },
    "HOLDING_COIL": {
        "range": range(0, 10000),
        "method": "read_discrete_inputs",
    },
    "INPUT_REGISTER": {
        "range": range(0, 10000),
        "method": "read_input_registers",
    },
    "HOLDING_REGISTER": {
        "range": range(0, 10000),
        "method": "read_holding_registers",
    },
}

ENDIAN_MAP = {
    None: Endian.Big, # default
    'big': Endian.Big,
    'little': Endian.Little
}


class ExositeModbus(object):
    """
        Do not use this class to create objects.

        Instead, use the mixin classes inheriting this class, below.

        This class provides the basic ExoSense schema support for
        Modbus devices.
    """
    __device_lock = threading.Lock()

    @classmethod
    def get_builder_method(cls, mode, count):
        """
            Class method for mapping the ExoSense "evaluation_mode"
            to the correct, support pymodbus function when doing writes.
        """
        LOG.debug("mode: {} count: {}".format(mode, count))
        if mode == 'floating point: ieee754':
            # registers are 16-bit
            return 'add_{}bit_float'.format(32 if count <= 2 else 64)
        elif mode == 'whole-remainder':
            return None
        elif mode == 'signed integer':
            if count <= 1:
                return 'add_16bit_int'
            elif count <= 2:
                return 'add_32bit_int'
            elif count <= 4:
                return 'add_64bit_int'
            else:
                return 'add_16bit_int'
        elif mode == 'unsigned':
            if count <= 1:
                return 'add_16bit_uint'
            elif count <= 2:
                return 'add_32bit_uint'
            elif count <= 4:
                return 'add_64bit_uint'
            else:
                return 'add_16bit_uint'
        elif mode == 'bitmask_int':
            return None
        elif mode == 'bitmask_bool':
            return None
        elif mode == 'string-ascii-byte':
            return 'add_string'
        elif mode == 'string-ascii-register':
            return 'add_string'

    @classmethod
    def get_decoder_method(cls, mode, count):
        """
            Class method for mapping the ExoSense "evaluation_mode"
            to the correct, support pymodbus function when doing reads.
        """
        LOG.debug("mode: {} count: {}".format(mode, count))
        if mode == 'floating point: ieee754':
            # registers are 16-bit
            return 'decode_32bit_float' # .format(32 if count <= 2 else 64)
        elif mode == 'whole-remainder':
            return None
        elif mode == 'signed integer':
            # TODO: not sure if this is correct.
            # if count <= 8:
            #     return 'decode_8bit_int'
            # elif count <= 16:
            #     return 'decode_16bit_int'
            # elif count <= 32:
            #     return 'decode_32bit_int'
            # elif count <= 64:
            #     return 'decode_64bit_int'
            return 'decode_16bit_int'
        elif mode == 'unsigned':
            # TODO: not sure if this is correct.
            if count <= 8:
                return 'decode_8bit_uint'
            elif count <= 16:
                return 'decode_16bit_uint'
            elif count <= 32:
                return 'decode_32bit_uint'
            elif count <= 64:
                return 'decode_64bit_uint'
        elif mode == 'bitmask_int':
            return 'decode_bits'
        elif mode == 'bitmask_bool':
            return 'decode_bits'
        elif mode == 'string-ascii-byte':
            return 'decode_string'
        elif mode == 'string-ascii-register':
            return 'decode_string'

    @classmethod
    def evaluate_coils(cls, **kwargs):
        """
            supported methods:
             - read_coils
             - read_discrete_inputs

            supported evaluation_modes:
             - string-ascii-register
             - string-ascii-byte
             - bitmask_int
             - bitmask_bool

            unsupported/unimplimented evaluation_modes:
             - floating point: ieee754
             - whole-remainder
             - signed integer
             - unsigned
        """
        LOG.debug('evaluate_coils: {}'.format(kwargs))
        decoder = BinaryPayloadDecoder.fromCoils(
            kwargs.get('coils'),
            byteorder=kwargs.get('byte_endianness'),
        )
        eval_mode = kwargs.get('evaluation_mode')
        bitmask = kwargs.get('bitmask')
        coil_count = kwargs.get('register_count')
        assert eval_mode in [
            'string-ascii-register',
            'string-ascii-byte',
            'bitmask_int',
            'bitmask_bool'
        ], "unsupported evaluation mode: {}".format(eval_mode)

        decoder_method = cls.get_decoder_method(eval_mode, coil_count)
        LOG.debug('using method: {}'.format(decoder_method))
        if eval_mode == 'string-ascii-register':
            return getattr(decoder, decoder_method)(coil_count)
        elif eval_mode == 'string-ascii-byte':
            return getattr(decoder, decoder_method)(1)
        else:
            LOG.debug("trying to decode with: {}".format(decoder_method))
            decoded = getattr(decoder, decoder_method)()
        LOG.debug("decoded: {}".format(decoded))
        bools_to_ints = [1 if c else 0 for c in decoded]
        LOG.debug('bools_to_ints: {}'.format(bools_to_ints))
        payload = bools_to_ints
        val = 0
        for bit in bools_to_ints:
            val = (val << 1) | bit
        LOG.debug("bitmask: {}".format(bitmask))
        LOG.debug("val: {}".format(val))

        if eval_mode == 'bitmask_int':
            payload = int(bitmask, 0) & val
            LOG.debug("bitmask_int: {}".format(payload))
        elif eval_mode == 'bitmask_bool':
            payload = bool(int(bitmask, 0) & val)
            LOG.debug("bitmask_bool: {}".format(payload))

        return payload

    @classmethod
    def evaluate_registers(cls, **kwargs):
        LOG.debug("kwargs: {!r}".format(kwargs))
        LOG.debug("byteorder: {}".format(kwargs.get('byte_endianness')))
        LOG.debug("wordorder: {}".format(kwargs.get('register_endianness')))

        eval_mode = kwargs.get('evaluation_mode')
        registers = kwargs.get('registers')
        count = kwargs.get('register_count')
        byteorder = ENDIAN_MAP[kwargs.get('byte_endianness')]
        wordorder = ENDIAN_MAP[kwargs.get('register_endianness')]
        bitmask = kwargs.get('bitmask')
        decoder = BinaryPayloadDecoder.fromRegisters(
            registers,
            byteorder=byteorder,
            wordorder=wordorder
        )

        def eval_signed(decoder, count):
            LOG.debug("evaluating signed integer: {}".format(registers))
            if count == 1:
                LOG.debug("using: decode_16bit_int")
                payload = decoder.decode_16bit_int()
            elif count <= 2:
                LOG.debug("using: decode_32bit_int")
                payload = decoder.decode_32bit_int()
            elif count <= 4:
                LOG.debug("using: decode_64bit_int")
                payload = decoder.decode_64bit_int()
            return payload

        def eval_unsigned(decoder, count):
            LOG.debug("evaluating unsigned integer: {!r}".format(decoder))
            if count == 1:
                LOG.debug("using: decode_16bit_uint")
                payload = decoder.decode_16bit_uint()
            elif count <= 2:
                LOG.debug("using: decode_32bit_uint")
                payload = decoder.decode_32bit_uint()
            elif count <= 4:
                LOG.debug("using: decode_64bit_uint")
                payload = decoder.decode_64bit_uint()
            return payload

        if eval_mode == 'floating point: ieee754':
            LOG.debug("before decode: {} : {}".format(decoder, count))
            if count <= 2:
                LOG.debug("using: decode_32bit_float")
                payload = decoder.decode_32bit_float()
            elif count <= 4:
                LOG.debug("using: decode_64bit_float")
                payload = decoder.decode_64bit_float()
        elif eval_mode == 'whole-remainder':
            LOG.critical("not implimented: {}".format(eval_mode))
            payload = None
        elif eval_mode == 'signed integer':
            payload = eval_signed(decoder, count)
        elif eval_mode == 'unsigned':
            payload = eval_unsigned(decoder, count)
        elif eval_mode == 'bitmask_int':
            the_int = eval_signed(decoder, count)
            payload = int(bitmask, 0) & the_int
        elif eval_mode == 'bitmask_bool':
            the_int = eval_signed(decoder, count)
            payload = bool(int(bitmask, 0) & the_int)
        elif eval_mode == 'string-ascii-byte':
            LOG.debug("before decode: {} : {}".format(decoder, count))
            payload = decoder.decode_string(count)
        elif eval_mode == 'string-ascii-register':
            LOG.debug("before decode: {} : {}".format(decoder, count))
            payload = decoder.decode_string(count)
        return payload

    def read_coils(self, eval_kwargs, no_decode=False):
        address = eval_kwargs.get('data_address')
        count = eval_kwargs.get('register_count')
        LOG.info("read_coils kwargs: {}".format(eval_kwargs))
        with self.__device_lock:
            coils = self.client.read_coils(address, count, unit=self.slave_id)
            LOG.debug("coils({}, {}): {}".format(coils, address, count))
            if not hasattr(coils, 'bits'):
                raise ExoEdgeModbusException("could not read holding coil(s): {}".format(coils))
        LOG.info("coils[address{}:count{}]: {}".format(address, count, coils.bits[address:count]))

        if no_decode:
            return coils.bits
        eval_kwargs['coils'] = coils.bits
        payload = self.evaluate_coils(**eval_kwargs)
        return payload

    def read_discrete_inputs(self, eval_kwargs, no_decode=False):
        address = eval_kwargs.get('data_address')
        count = eval_kwargs.get('register_count')
        LOG.info("read_discrete_inputs kwargs: {}".format(eval_kwargs))
        with self.__device_lock:
            coils = self.client.read_discrete_inputs(address, count, unit=self.slave_id)
            LOG.debug("coils({}, {}): {}".format(coils, address, count))
            if not hasattr(coils, 'bits'):
                raise ExoEdgeModbusException("could not read input coil(s): {}".format(coils))
        LOG.info("coils[address{}:count{}]: {}".format(address, count, coils.bits[address:count]))

        if no_decode:
            return coils.bits
        eval_kwargs['coils'] = coils.bits
        payload = self.evaluate_coils(**eval_kwargs)
        return payload

    def read_input_registers(self, eval_kwargs, no_decode=False):
        address = eval_kwargs.get('data_address')
        count = eval_kwargs.get('register_count')
        LOG.info("read_input_registers kwargs: {}".format(eval_kwargs))
        with self.__device_lock:
            response = self.client.read_input_registers(address, count, unit=self.slave_id)
            if not hasattr(response, 'registers'):
                raise ExoEdgeModbusException("could not read input register(s): {}".format(response))
        LOG.info("registers[address:count]: {}".format(address, count, response.registers))
        if no_decode:
            return response.registers
        eval_kwargs['registers'] = response.registers
        payload = self.evaluate_registers(**eval_kwargs)
        return payload

    def read_holding_registers(self, eval_kwargs, no_decode=False):
        address = eval_kwargs.get('data_address')
        count = eval_kwargs.get('register_count')
        LOG.info("read_holding_registers kwargs: {}".format(eval_kwargs))
        with self.__device_lock:
            response = self.client.read_holding_registers(address, count, unit=self.slave_id)
            if not hasattr(response, 'registers'):
                raise ExoEdgeModbusException("could not read holding register(s): {}".format(response))
        LOG.info("registers[address:count]: {}".format(address, count, response.registers))
        if no_decode:
            return response.registers
        eval_kwargs['registers'] = response.registers
        payload = self.evaluate_registers(**eval_kwargs)
        return payload

    def write_coil(self, address, value):
        with self.__device_lock:
            response = self.client.write_coil(address, int(value), unit=self.slave_id)
            return response

    def write_coils(self, address, values):
        raw_str_list = values.split(',')
        bool_list = [bool(int(v)) for v in raw_str_list]
        LOG.debug("coils values: {}".format(bool_list))
        with self.__device_lock:
            response = self.client.write_coils(address, bool_list, unit=self.slave_id)
            return response

    def write_register(self, address, value, eval_mode, byteorder, wordorder):
        builder = BinaryPayloadBuilder(
            byteorder=byteorder,
            wordorder=wordorder
        )
        if not eval_mode.startswith('string'):
            if eval_mode == 'floating point: ieee754':
                cast_method = float
            else:
                cast_method = int
            value = cast_method(value)
        getattr(builder, self.get_builder_method(eval_mode, 1))(value)
        payload = builder.build()
        LOG.debug(payload)
        with self.__device_lock:
            response = self.client.write_register(address, payload[0], skip_encode=True, unit=self.slave_id)
            return response

    def write_registers(self, address, count, value, eval_mode, byteorder, wordorder):
        byteorder=ENDIAN_MAP[byteorder]
        wordorder=ENDIAN_MAP[wordorder]
        builder = BinaryPayloadBuilder(
            byteorder=byteorder,
            wordorder=wordorder
        )
        if not eval_mode.startswith('string'):
            if eval_mode == 'floating point: ieee754':
                cast_method = float
            else:
                cast_method = int
            value = [cast_method(v) for v in value.split(',')]
            LOG.debug('packing value: {}'.format(value))
            for val in value:
                method = self.get_builder_method(eval_mode, count)
                LOG.debug('using method: {}'.format(method))
                getattr(builder, method)(val)
            payload = builder.to_registers()
        else:
            method = self.get_builder_method(eval_mode, count)
            LOG.debug('value: {} method: {} count: {}'.format(value, method, count))
            getattr(builder, method)(value)
            payload = builder.to_registers()
        LOG.debug("payload: {}".format(payload))
        # decode just to verify...
        decoder = BinaryPayloadDecoder.fromRegisters(
            payload,
            byteorder=byteorder,
            wordorder=wordorder
        )
        dmethod = self.get_decoder_method(eval_mode, count)
        decoded = getattr(decoder, dmethod)()
        with self.__device_lock:
            response = self.client.write_registers(address, payload, unit=self.slave_id)
            return response

class ExositeModbusTCP(ExositeModbus):
    def __init__(self, **kwargs):
        self.ip = kwargs.get('ip_address')
        self.port = kwargs.get('port')
        self.slave_id = 1
        self.client = ModbusTcpClient(
            self.ip,
            self.port)

class ExositeModbusRTU(ExositeModbus):
    """
        Mixin class for Modbus RTU.

        Defaults for client kwargs are located:
            https://github.com/riptideio/pymodbus/blob/master/pymodbus/constants.py#L92

    """
    def __init__(self, **kwargs):
        self.slave_id = 1

        self.ip = '127.0.0.1'
        self.port = kwargs.get('interface')

        stopbits = int(kwargs.get('stop_bits', 1))

        if kwargs.get('parity') == 'even':
            parity = 'E'
        elif kwargs.get('parity') == 'odd':
            parity = 'O'
        elif kwargs.get('parity') == 'none':
            parity = 'N'
        else:
            parity = 'N'

        self.client = ModbusSerialClient(
            method='rtu',
            port=kwargs.get('interface'),
            baudrate=kwargs.get('baud_rate'),
            stopbits=stopbits,
            parity=parity,
            timeout=int(kwargs.get('timeout', 1))
        )
        LOG.critical("ExositeModbusRTU: initialized: {}".format(kwargs))
        LOG.critical("ExositeModbusRTU: initialized: {}".format(self))


class ExoEdgeModbusException(Exception):
    pass
