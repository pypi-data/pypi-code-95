# pylint: disable=I0011,W0312,C0301,C0103,W0123,W1202,C0326,C0111,R0911
r"""Tool for interacting with modbus devices.

Usage:
  exomod [-hv]
  exomod [options] read_coils             <address> <count>              [options]
  exomod [options] read_discrete_inputs   <address> <count>              [options]
  exomod [options] read_input_registers   <address> <count>              [options]
  exomod [options] read_holding_registers <address> <count>              [options]
  exomod [options] write_coil             <address>              <value> [options]
  exomod [options] write_coils            <address> <count>      <value> [options]
  exomod [options] write_register         <address>         [--] <value> [options]
  exomod [options] write_registers        <address> <count> [--] <value> [options]

Options:
    -h --help                               Show this screen.
    -v --version                            Show the version.
    -D --debug <lvl>                        Either DEBUG | INFO | WARNING | ERROR | CRITICAL.
    -I --ip-address <ip>                    The ip address of the modbus device.
    -P --port <port>                        The port of the modbus device.
    -S --slave-id <slave_id>                RTU only. The slave id or unit of the modbus device.
    <address>                               The address of coil/register to begin the read/write operation.
    <count>                                 The number of coils/registers to read/write.
    <value>                                 The value to read/write.
    -n --no-decode                          Just print the contents of the registers/coils. Do not attempt
                                            to decode/translate them into a single evaluated value.
    -e --endianness <endianness>            Either big or little.
    -b --bitmask <bitmask>                  When evaluating registers as bitmask_int and bitmask_bool,
                                            AND the result with <bitmask>.
    -B --byte-endianness <byteendianness>   Either big or little.
    -r --reg-endianness <regendianness>     Either big or little. A word is 2 bytes, or 1 register.
    -m --evaluation-mode <mode>             When reading/writing, evaluate the <value>/result in one
                                            of the following modes:

          |--------------------------|------------|----------------------|---------------------|------------------------|
          |          mode            | read_coils | read_discrete_inputs | read_input_regisers | read_holding_registers |
          |--------------------------|------------|----------------------|---------------------|------------------------|
          | floating point: ieee754  |     n      |          n           |          y          |             y          |
          | whole-remainder          |    n/a     |         n/a          |         n/a         |            n/a         |
          | signed integer           |     n      |          n           |          y          |             y          |
          | unsigned                 |     n      |          n           |          y          |             y          |
          | bitmask_int              |     y      |          y           |          y          |             y          |
          | bitmask_bool             |     y      |          y           |          y          |             y          |
          | string-ascii-byte        |     y      |          y           |          y          |             y          |
          | string-ascii-register    |     y      |          y           |          y          |             y          |
          |--------------------------|------------|----------------------|---------------------|------------------------|
"""

from __future__ import print_function
import logging
from docopt import docopt, DocoptExit
from exoedge_modbus.lib import ExositeModbusTCP, ExositeModbusRTU
from exoedge_modbus.__version__ import __version__
from pymodbus.constants import Endian

logging.basicConfig()
LOG = logging.getLogger('exoedge.exomod')


def main():
    # ##################################### #
    # parse cli opts
    # ##################################### #

    docopt_args = docopt(__doc__, version=__version__)
    if docopt_args.get('--version'):
        print(__version__)
        return
    debug = docopt_args.get('--debug')
    if debug:
        LOG.setLevel(getattr(logging, debug[0].upper()))
    LOG.debug("\n{}".format(docopt_args))

    method = "tcp"

    ip = docopt_args.get('--ip-address')
    if not ip:
        ip = '127.0.0.1'
    else:
        ip = ip[0]
    port = docopt_args.get('--port')
    if not port:
        port = 5020
    else:
        port = port[0]

    slave_id = docopt_args.get('--slave-id')
    if not slave_id:
        slave_id = 1
    else:
        print("using rtu")
        method = 'rtu'
        slave_id = int(slave_id[0])
        if not docopt_args.get('--port'):
            raise DocoptExit('serial port must be specified via --port when using rtu.')

    eval_mode = docopt_args.get('--evaluation-mode')
    if eval_mode:
        eval_mode = eval_mode[0]
    else:
        eval_mode = 'signed integer'

    LOG.debug("eval_mode: {}".format(eval_mode))

    address = int(docopt_args.get('<address>'))
    count = docopt_args.get('<count>')
    if count:
        count = int(count)
    value = docopt_args.get('<value>')

    byteorder = docopt_args.get('--byte-endianness')
    if not byteorder:
        byteorder = 'big'
    elif byteorder[0].lower() in ['little', 'big']:
        byteorder = byteorder.lower()
    LOG.debug("byteorder: {}".format(byteorder))

    wordorder = docopt_args.get('--reg-endianness')
    if not wordorder:
        wordorder = 'big'
    elif wordorder[0].lower() in ['little', 'big']:
        wordorder = wordorder.lower()
    LOG.debug("wordorder: {}".format(wordorder))

    bitmask = docopt_args.get('--bitmask')
    if bitmask:
        bitmask = bitmask[0]
    else:
        bitmask = '0b11111111'
    LOG.debug("bitmask before casting to int: {}".format(bitmask))

    no_decode = True if docopt_args.get('--no-decode') else False

    eval_kwargs = {
        'ip_address': ip,
        'port': port,
        'slave_id': slave_id,
        'data_address': address,
        'register_count': count,
        'value': value,
        'byte_endianness': byteorder,
        'register_endianness': wordorder,
        'evaluation_mode': eval_mode,
        'bitmask': bitmask,
    }

    if method == 'rtu':
        eval_kwargs.update({
                'interface':port,
                'slave_id':slave_id,
                'baud_rate':19200,
                'stop_bits':1,
                'parity':'N',
                'timeout':1})
        print("rtu kwargs: {}".format(eval_kwargs))
        c = ExositeModbusRTU(**eval_kwargs)
    else:
        c = ExositeModbusTCP(**eval_kwargs)

    # ####################################### #
    # READ
    # ####################################### #
    if docopt_args.get('read_coils'):
        res = c.read_coils(eval_kwargs, no_decode=no_decode)
    elif docopt_args.get('read_discrete_inputs'):
        res = c.read_discrete_inputs(eval_kwargs, no_decode=no_decode)
    elif docopt_args.get('read_input_registers'):
        res = c.read_input_registers(eval_kwargs, no_decode=no_decode)
    elif docopt_args.get('read_holding_registers'):
        res = c.read_holding_registers(eval_kwargs, no_decode=no_decode)

    # ####################################### #
    # WRITE
    # ####################################### #
    elif docopt_args.get('write_coil'):
        res = c.write_coil(address, value)
    elif docopt_args.get('write_coils'):
        res = c.write_coils(address, value)
    elif docopt_args.get('write_register'):
        res = c.write_register(address, value, eval_mode, byteorder, wordorder)
    elif docopt_args.get('write_registers'):
        res = c.write_registers(address, count, value, eval_mode, byteorder, wordorder)

    print(res)

if __name__ == '__main__':
    main()

