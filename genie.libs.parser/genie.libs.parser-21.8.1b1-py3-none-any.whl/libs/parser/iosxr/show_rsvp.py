"""show_rsvp.py

IOSXR parsers for the following commands:
    * show rsvp session
    * show rsvp session destination {ipaddress}
    * show rsvp neighbors
    * show rsvp graceful-restart neighbors
"""
import re

# Metaparser
from genie.metaparser import MetaParser
from pyats.utils.exceptions import SchemaError
from genie.metaparser.util.schemaengine import Any, Optional, Use, Schema, ListOf
from genie.libs.parser.utils.common import Common


class ShowRSVPSessionSchema(MetaParser):
    """ Schema for:
        * show rsvp session
        * show rsvp session destination {ipaddress}
    """

    schema = {
        "rsvp-session-information": {
            Optional("rsvp-session-data"): ListOf({
                "type": str,
                "destination-address": str,
                "destination-port": int,
                "proto-exttun-id": str,
                "psb": int,
                "rsb": int,
                "req": int
            }),
        }
    }


class ShowRSVPSession(ShowRSVPSessionSchema):
    """ Parser for:
        * show rsvp session
        * show rsvp session destination {ipaddress}
    """

    cli_command = ['show rsvp session', 'show rsvp session destination {ipaddress}']

    def cli(self, output=None, ip_address=None):
        if not output and ip_address:
            out = self.device.execute(self.cli_command[1].format(ipaddress=ip_address))
        elif not output:
            out = self.device.execute(self.cli_command[0])
        else:
            out = output

        ret_dict = {}

        # LSP4     17.17.17.17 15060 141.141.141.141     1     1     1
        p1 = re.compile(r'^(?P<type>\S+)\s+(?P<destination_address>\d{1,3}\.\d{1,3}'
                        r'\.\d{1,3}\.\d{1,3})\s+(?P<destination_port>\d+)\s+'
                        r'(?P<proto_exttun_id>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+'
                        r'(?P<psb>\d+)\s+(?P<rsb>\d+)\s+(?P<req>\d+)$')

        for line in out.splitlines():
            line = line.strip()

            # LSP4     17.17.17.17 15060 141.141.141.141     1     1     1
            m = p1.match(line)
            if m:
                group = m.groupdict()
                session_data_list = ret_dict.setdefault('rsvp-session-information', {}) \
                    .setdefault('rsvp-session-data', [])
                session_data_dict = {}
                session_data_dict.update({
                    'type': group['type'],
                    'destination-address': group['destination_address'],
                    'destination-port': int(group['destination_port']),
                    'proto-exttun-id': group['proto_exttun_id'],
                    'psb': int(group['psb']),
                    'rsb': int(group['rsb']),
                    'req': int(group['req'])
                })
                session_data_list.append(session_data_dict)
                continue

        return ret_dict


class ShowRSVPNeighborSchema(MetaParser):
    """ Schema for:
        * show rsvp neighbors
    """

    schema = {
        "rsvp-neighbor-information": {
            "global-neighbor": {
                Any():{
                    "interface-neighbor": str,
                    "interface": str
                }
            }
        }
    }

class ShowRSVPNeighbor(ShowRSVPNeighborSchema):
    """ Parser for:
        * show rsvp neighbor
    """

    cli_command = 'show rsvp neighbor'

    def cli(self, output=None):
        if not output:
            out = self.device.execute(self.cli_command)
        else:
            out = output

        ret_dict = {}

        # Global Neighbor: 106.106.106.106
        p1 = re.compile(r'^Global +Neighbor:\s+(?P<global_neighbor>.+)$')

        # 99.33.0.2            TenGigE0/2/0/0
        p2 = re.compile(r'^(?P<intf_neighbor>\d{1,3}\.\d{1,3}\.'
                        r'\d{1,3}\.\d{1,3})\s+(?P<interface>.+)$')


        for line in out.splitlines():
            line = line.strip()

            # Global Neighbor: 106.106.106.106
            m = p1.match(line)
            if m:
                group = m.groupdict()
                neighbor_information = ret_dict.setdefault('rsvp-neighbor-information', {}).\
                    setdefault('global-neighbor', {}).setdefault(group['global_neighbor'], {})
                continue

            # 99.33.0.2            TenGigE0/2/0/0
            m = p2.match(line)
            if m:
                group = m.groupdict()
                # convert interface to full name
                interface = Common.convert_intf_name(group['interface'])
                neighbor_information.update({
                    'interface-neighbor': group['intf_neighbor'],
                    'interface': interface
                })
                continue

        return ret_dict


class ShowRSVPGracefulRestartNeighborsSchema(MetaParser):
    """ Schema for:
        * show rsvp graceful-restart neighbors
    """

    schema = {
        "rsvp-neighbor-information": {
            "neighbor": {
                Any():{
                    "app": str,
                    "state": str,
                    "recovery": str,
                    "reason": str,
                    "since": str,
                    "lost-connection": int
                }
            }
        }
    }

class ShowRSVPGracefulRestartNeighbors(ShowRSVPGracefulRestartNeighborsSchema):
    """ Parser for:
       * show rsvp graceful-restart neighbors
    """

    cli_command = 'show rsvp graceful-restart neighbors'

    def cli(self, output=None):
        if not output:
            out = self.device.execute(self.cli_command)
        else:
            out = output

        ret_dict = {}

        # 106.106.106.106  MPLS    N/A     DONE          N/A                  N/A        0
        p1 = re.compile(r'^(?P<neighbor>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+'
                        r'(?P<app>\w+)\s+(?P<state>\S+)\s+(?P<recovery>\w+)\s+'
                        r'(?P<reason>\S+)\s+(?P<since>\S+)\s+(?P<lost_cnt>\d+)$')


        for line in out.splitlines():
            line = line.strip()

            # 106.106.106.106  MPLS    N/A     DONE          N/A                  N/A        0
            m = p1.match(line)
            if m:
                group = m.groupdict()
                neighbor_information = ret_dict.setdefault('rsvp-neighbor-information', {}).\
                    setdefault('neighbor', {}).setdefault(group['neighbor'], {})
                neighbor_information.update({
                    'app': group['app'],
                    'state': group['state'],
                    'recovery': group['recovery'],
                    'reason': group['reason'],
                    'since': group['since'],
                    'lost-connection': int(group['lost_cnt'])
                })
                continue

        return ret_dict
