from argparse import Namespace
import imp
import multicommand
import logging
from zabbix_api import ZabbixAPI
from . import commands


def main():
    parser = multicommand.create_parser(commands)
    parser.add_argument('-s', '--zbx-server', required=True, help='URL of zabbix server')
    parser.add_argument('-u', '--zbx-user', required=True, help='Zabbix server login username')
    parser.add_argument('-p', '--zbx-passwd', required=True, help='Zabbix server login password')
    parser.add_argument('-t', '--timeout', default=60, type=int, help='Zabbix API timeout')
    parser.add_argument('-v', '--verbose', action='store_true', help='Print debug information')
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    zapi = ZabbixAPI(args.zbx_server, timeout=args.timeout)
    zapi.validate_certs = False
    zapi.login(user=args.zbx_user, password=args.zbx_passwd)

    setattr(args, 'zapi', zapi)

    if hasattr(args, "handler"):
        args.handler(args)

    zapi.logout()

if __name__ == "__main__":
    exit(main())
