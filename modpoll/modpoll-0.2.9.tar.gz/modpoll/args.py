import argparse

from modpoll import __version__

def parse_args():
    parser = argparse.ArgumentParser(description=f'modpoll {__version__} - A command line tool to communicate with modbus devices')
    parser.add_argument('--version', action='version', version=f'modpoll {__version__}')
    parser.add_argument('--config', required=True, help='Configuration file. Required!')
    parser.add_argument('--rate', default=5.0, type=float, help='The sampling rate (s) to poll modbus device')
    parser.add_argument('--interval', default=1.0, type=float, help='The time interval (s) between two polling')
    parser.add_argument('--tcp', help='Act as a Modbus TCP master, connecting to host TCP')
    parser.add_argument('--tcp-port', default=502, type=int, help='Port for MODBUS TCP. Defaults to 502')
    parser.add_argument('--rtu', help='pyserial URL (or port name) for RTU serial port')
    parser.add_argument('--rtu-baud', default=9600, type=int, help='Baud rate for serial port. Defaults to 9600')
    parser.add_argument('--rtu-parity', default='none', choices=['even', 'odd', 'none'], help='Parity for serial port. Defaults to none')
    parser.add_argument('--timeout', default=0.5, type=float, help='Response time-out for MODBUS devices')
    parser.add_argument('--export', default=None, help='Export references/registers to local csv file')
    parser.add_argument('--mqtt-host', default=None, help='MQTT server address. Skip MQTT setup if not specified')
    parser.add_argument('--mqtt-port', default=1883, type=int, help='Defaults to 1883 for non-TLS or 8883 for TLS')
    parser.add_argument('--mqtt-topic', default='modbus/', help='Topic prefix to be used for subscribing/publishing. Defaults to "modbus/"')
    parser.add_argument('--mqtt-user', default=None, help='Username for authentication (optional)')
    parser.add_argument('--mqtt-pass', default=None, help='Password for authentication (optional)')
    parser.add_argument('--mqtt-use-tls', action='store_true', help='Use TLS')
    parser.add_argument('--mqtt-insecure', action='store_true', help='Use TLS without providing certificates')
    parser.add_argument('--mqtt-cacerts', default=None, help="Path to keychain including ")
    parser.add_argument('--mqtt-tls-version', default=None, help='TLS protocol version, can be one of tlsv1.2 tlsv1.1 or tlsv1')
    parser.add_argument('--diagnostics-rate', default=0, type=float, help='Time in seconds after which for each device diagnostics are published via mqtt.')
    parser.add_argument('--verbosity', default='3', type=int, help='Verbose level, 0=silent, 1=errors only, 2=connections, 3=mb writes, 4=all')
    parser.add_argument('--autoremove', action='store_true', help='Automatically remove poller if modbus communication has failed three times.')
    return parser.parse_args()


args = parse_args()
