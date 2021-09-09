# Boltlight - a LN node wrapper
#
# Copyright (C) 2021 boltlight contributors
# Copyright (C) 2018 inbitcoin s.r.l.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# For a full list of contributors, please see the AUTHORS.md file.
"""
Implementation of a CLI to command boltlight.

- Exits with code 0 if everything is OK
- Exits with code 1 when a general client-side error occurs
- Exits with code 64 + <gRPC status code> when a gRPC error is raised by server
(https://github.com/grpc/grpc/blob/master/doc/statuscodes.md)

WARNING: new imports might require updating the package build system.
"""

from codecs import encode
from configparser import Error as ConfigError
from contextlib import contextmanager
from functools import wraps
from json import dumps
from os import getcwd, path

from click import (argument, echo, group, option, ParamType, pass_context,
                   version_option)
from google.protobuf.json_format import MessageToJson
from grpc import (channel_ready_future, composite_channel_credentials,
                  FutureTimeoutError, insecure_channel,
                  metadata_call_credentials, RpcError, secure_channel,
                  ssl_channel_credentials)

from . import (__version__, boltlight_pb2 as pb, boltlight_pb2_grpc as pb_grpc,
               settings as sett)

UNLOCKER_APIS = ('Unlock', )
BOLTLIGHT_APIS = (
    'GetInfo',
    'Lock',
)


class AddressType(ParamType):
    """Custom type of Address.Type proto enum."""
    name = 'Address.Type'

    def convert(self, value, param, ctx):
        """Convert input value to corresponding Address.Type enum."""
        if value in ['0', 'NP2WPKH', 'NESTED_SEGWIT']:
            return 0
        if value in ['1', 'P2WPKH', 'NATIVE_SEGWIT']:
            return 1
        return self.fail(f'{value} is not a valid {self.name}', param, ctx)


def _get_address_type(ctx, args, incomplete):
    """Autocompletion for AddressType."""
    assert ctx
    assert args
    address_types = [('NP2WPKH', 'Pay to nested witness key hash'),
                     ('P2WPKH', 'Pay to witness public key hash')]
    if incomplete == '':
        return address_types
    return [k for k in address_types if k[0].startswith(incomplete)]


class OrderDirection(ParamType):
    """Custom type of Order.Direction proto enum."""
    name = 'Order.Direction'

    def convert(self, value, param, ctx):
        """Convert input value to corresponding Order.Direction enum."""
        if value in ['0', 'ASCENDING']:
            return 0
        if value in ['1', 'DESCENDING']:
            return 1
        return self.fail(f'{value} is not a valid {self.name}', param, ctx)


def _get_order(ctx, args, incomplete):
    """Autocompletion for OrderDirection."""
    assert ctx
    assert args
    orders = [('ASCENDING', 'From oldest to newest'),
              ('DESCENDING', 'From newest to oldest')]
    if incomplete == '':
        return orders
    return [k for k in orders if k[0].startswith(incomplete)]


def _die(message=None, exit_code=1):
    """Print message to stderr and exit with the requested error code."""
    from .utils.misc import die  # pylint: disable=import-outside-toplevel
    die(message, exit_code)


def _check_rpcserver_addr():
    """Check the rpcserver address, adding port if missing."""
    if not sett.CLI_RPCSERVER:
        _die('Invalid rpcserver address')
    rpcserver = sett.CLI_RPCSERVER.split(':', 1)
    if len(rpcserver) > 1:
        port = rpcserver[1]
        if not port.isdigit():
            _die('Invalid port')
        if int(port) not in range(1, 65536):
            _die('Invalid port')
    else:
        sett.CLI_RPCSERVER = sett.CLI_RPCSERVER + ':' + sett.PORT


def _get_cli_options():
    """Set CLI options."""
    # pylint: disable=import-outside-toplevel
    from .utils.misc import get_config_parser, get_path, set_defaults, str2bool
    # pylint: enable=import-outside-toplevel
    config = get_config_parser(interactive=True)
    c_values = ['RPCSERVER', 'TLSCERT', 'MACAROON', 'INSECURE', 'NO_MACAROON']
    set_defaults(config, c_values)
    sec = 'blink'
    if not sett.CLI_INSECURE:
        sett.CLI_INSECURE = str2bool(config.get(sec, 'INSECURE'))
    if not sett.CLI_NO_MACAROON:
        sett.CLI_NO_MACAROON = str2bool(config.get(sec, 'NO_MACAROON'))
    if not sett.CLI_RPCSERVER:
        sett.CLI_RPCSERVER = config.get(sec, 'RPCSERVER')
        _check_rpcserver_addr()
    if not sett.CLI_INSECURE:
        if not sett.CLI_TLSCERT:
            sett.CLI_TLSCERT = get_path(config.get(sec, 'TLSCERT'))
    else:
        sett.CLI_NO_MACAROON = True
    if not sett.CLI_NO_MACAROON:
        if not sett.CLI_MACAROON:
            sett.CLI_MACAROON = get_path(config.get(sec, 'MACAROON'))


def handle_call(func):
    """Handle a call to boltlight."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        """Get start options and run wrapped function."""
        try:
            _get_cli_options()
            api, req = func(*args, **kwargs)
            stub_name = _get_stub_name(api)
            with _connect(stub_name) as stub:
                res = getattr(stub, api)(req, timeout=sett.CLI_TIMEOUT)
            _print_res(res)
        except RpcError as err:
            # pylint: disable=no-member
            err_code = err.code()
            json_err = {'code': err_code.name, 'details': err.details()}
            # pylint: enable=no-member
            error = dumps(json_err, indent=4, sort_keys=True)
            _die(error, sett.CLI_BASE_GRPC_CODE + err_code.value[0])
        except ConfigError as err:
            _die(f'Configuration error: {err}')

    return wrapper


def _print_res(response):
    """Print response using JSON format."""
    echo(
        MessageToJson(response,
                      including_default_value_fields=True,
                      preserving_proto_field_name=True))


def _get_stub_name(api):
    """Get name of proto service based on API name."""
    if api in UNLOCKER_APIS:
        return 'UnlockerStub'
    if api in BOLTLIGHT_APIS:
        return 'BoltlightStub'
    return 'LightningStub'


@contextmanager
def _connect(stub_class):
    """Connect to boltlight using gRPC (securely or insecurely)."""
    channel = None
    if sett.CLI_INSECURE:
        channel = insecure_channel(sett.CLI_RPCSERVER)
    else:
        if sett.CLI_NO_MACAROON:
            creds = _get_credentials(None)
        else:
            creds = _get_credentials(_metadata_callback)
        channel = secure_channel(sett.CLI_RPCSERVER, creds)
    future_channel = channel_ready_future(channel)
    try:
        future_channel.result(timeout=sett.CLI_TIMEOUT)
    except FutureTimeoutError:
        # Handle gRPC channel that did not connect
        _die('Failed to dial server')
    else:
        stub = getattr(pb_grpc, stub_class)(channel)
        yield stub
        channel.close()


def _get_credentials(callback):
    """Get credentials to open a secure gRPC channel.

    TLS certificate file must exist, macaroons are optional.
    """
    with open(sett.CLI_TLSCERT, 'rb') as file:
        cert = file.read()
    creds = cert_creds = ssl_channel_credentials(root_certificates=cert)
    if callback:  # macaroons are enabled
        if not path.exists(sett.CLI_MACAROON):
            _die('Macaroon file not found')
        auth_creds = metadata_call_credentials(callback)
        creds = composite_channel_credentials(cert_creds, auth_creds)
    return creds


def _metadata_callback(_context, callback):
    """Get boltlight's macaroon to be included in the gRPC request."""
    with open(sett.CLI_MACAROON, 'rb') as file:
        macaroon_bytes = file.read()
        macaroon = encode(macaroon_bytes, 'hex')
    callback([('macaroon', macaroon)], None)


@group()
@option('--config',
        nargs=1,
        help='Path to blink configuration file '
        '(default ~/.boltlight/config).')
@option('--rpcserver',
        nargs=1,
        help='Set host[:port] of boltlight gRPC server.')
@option('--tlscert', nargs=1, help='Path to boltlight\'s TLS certificate.')
@option('--macaroon', nargs=1, help='Path to boltlight\'s macaroon.')
@option('--insecure', is_flag=True, help='Do not use TLS and macaroon.')
@option('--no-macaroon', is_flag=True, help='Do not use macaroon.')
@version_option(version=__version__, message='%(version)s')
@pass_context  # pylint: disable=too-many-arguments
def entrypoint(ctx, config, rpcserver, tlscert, macaroon, insecure,
               no_macaroon):
    """Blink, a CLI for boltlight.

    Paths are relative to the working directory.
    """
    incompatible_opts = {
        'insecure': ['tlscert', 'macaroon'],
        'no_macaroon': ['macaroon'],
    }
    passed_params = [param for param in ctx.params if ctx.params[param]]
    for param in passed_params:
        if param in incompatible_opts:
            if any(opt in passed_params for opt in incompatible_opts[param]):
                _die('Incompatible options')

    if config is not None:
        if not config:
            _die('Invalid configuration file')
        # pylint: disable=import-outside-toplevel
        from .utils.misc import get_path
        # pylint: enable=import-outside-toplevel
        sett.CONFIG = get_path(config, base_path=getcwd())
    if rpcserver is not None:
        sett.CLI_RPCSERVER = rpcserver
        _check_rpcserver_addr()
    if tlscert is not None:
        if not tlscert or not path.exists(tlscert):
            _die(f"Missing TLS certificate '{tlscert}'")
        sett.CLI_TLSCERT = tlscert
    if macaroon is not None:
        if not macaroon or not path.exists(macaroon):
            _die(f"Missing macaroon '{macaroon}'")
        sett.CLI_MACAROON = macaroon
    if insecure:
        sett.CLI_INSECURE = True
    if no_macaroon:
        sett.CLI_NO_MACAROON = True


@entrypoint.command()
@option('--password',
        prompt='Insert boltlight\'s password',
        hide_input=True,
        help='Boltlight\'s password.')
@option('--unlock-node',
        is_flag=True,
        help='Whether to also unlock the LN '
        'node')
@handle_call
def unlock(password, unlock_node):
    """Unlock boltlight."""
    req = pb.UnlockRequest(password=password, unlock_node=unlock_node)
    return 'Unlock', req


@entrypoint.command()
@handle_call
def getinfo():
    """Show info about boltlight and the wrapped implementation."""
    req = pb.GetInfoRequest()
    return 'GetInfo', req


@entrypoint.command()
@handle_call
def lock():
    """Lock boltlight."""
    req = pb.LockRequest()
    return 'Lock', req


@entrypoint.command()
@handle_call
def balanceoffchain():
    """Show the available off-chain balance."""
    req = pb.BalanceOffChainRequest()
    return 'BalanceOffChain', req


@entrypoint.command()
@argument('payment_hash', nargs=1)
@handle_call
def checkinvoice(payment_hash):
    """Check if a LN invoice has been paid."""
    req = pb.CheckInvoiceRequest(payment_hash=payment_hash)
    return 'CheckInvoice', req


@entrypoint.command()
@argument('channel_id')
@option('--force', is_flag=True, help='Whether to force a unilateral close.')
@handle_call
def closechannel(channel_id, force):
    """Close a LN channel."""
    req = pb.CloseChannelRequest(channel_id=channel_id, force=force)
    return 'CloseChannel', req


@entrypoint.command()
@option('--amount-msat', nargs=1, type=int, help='Invoice amount.')
@option('--description', nargs=1, help='Invoice description.')
@option('--expiry',
        nargs=1,
        type=int,
        help='Invoice expiration time, in '
        'seconds (default: 420).')
@option('--min-final-cltv-expiry',
        nargs=1,
        type=int,
        help='CTLV delay '
        '(absolute) to use for the final hop in the route.')
@option('--fallback-addr',
        nargs=1,
        help='Fallback address to use if the LN '
        'payment fails.')
@handle_call
def createinvoice(amount_msat, description, expiry, min_final_cltv_expiry,
                  fallback_addr):
    """Create a LN invoice (BOLT 11)."""
    req = pb.CreateInvoiceRequest(amount_msat=amount_msat,
                                  description=description,
                                  expiry=expiry,
                                  min_final_cltv_expiry=min_final_cltv_expiry,
                                  fallback_addr=fallback_addr)
    return 'CreateInvoice', req


@entrypoint.command()
@argument('payment_request', nargs=1)
@option('--description',
        nargs=1,
        help='Invoice description, whose hash should'
        ' match the description hash in the payment request (if present).')
@handle_call
def decodeinvoice(payment_request, description):
    """Decode a LN invoice (BOLT 11)."""
    req = pb.DecodeInvoiceRequest(payment_request=payment_request,
                                  description=description)
    return 'DecodeInvoice', req


@entrypoint.command()
@handle_call
def getnodeinfo():
    """Show info about the wrapped LN node."""
    req = pb.GetNodeInfoRequest()
    return 'GetNodeInfo', req


@entrypoint.command()
@option('--active-only',
        is_flag=True,
        help='Whether to return active '
        'channels only (channel is open and peer is online).')
@handle_call
def listchannels(active_only):
    """List the node's LN channels."""
    req = pb.ListChannelsRequest(active_only=active_only)
    return 'ListChannels', req


# pylint: disable=too-many-arguments
@entrypoint.command()
@option('--max-items',
        nargs=1,
        type=int,
        help='Maximum number of invoices '
        'to be returned (default: 200).')
@option('--search-timestamp',
        nargs=1,
        type=int,
        help='Timestamp to be used '
        'as starting point for the search.')
@option('--search-order',
        nargs=1,
        type=OrderDirection(),
        autocompletion=_get_order,
        help='Search direction - requires search_timestamp (default: '
        'ascending).')
@option('--list-order',
        nargs=1,
        type=OrderDirection(),
        autocompletion=_get_order,
        help='Order of the returned invoices (default: ascending)')
@option('--paid', is_flag=True, help='Whether to include paid invoices.')
@option('--pending', is_flag=True, help='Whether to include pending invoices.')
@option('--expired', is_flag=True, help='Whether to include expired invoices.')
@option('--unknown',
        is_flag=True,
        help='Whether to include invoices with an '
        'unknown state.')
@handle_call  # pylint: enable=too-many-arguments
def listinvoices(max_items, search_timestamp, search_order, list_order, paid,
                 pending, expired, unknown):
    """List the node's LN invoices."""
    req = pb.ListInvoicesRequest(max_items=max_items,
                                 search_timestamp=search_timestamp,
                                 search_order=search_order,
                                 list_order=list_order,
                                 paid=paid,
                                 pending=pending,
                                 expired=expired,
                                 unknown=unknown)
    return 'ListInvoices', req


@entrypoint.command()
@handle_call
def listpayments():
    """List the node's LN payments."""
    req = pb.ListPaymentsRequest()
    return 'ListPayments', req


@entrypoint.command()
@handle_call
def listpeers():
    """List the node's connected peers."""
    req = pb.ListPeersRequest()
    return 'ListPeers', req


@entrypoint.command()
@handle_call
def listtransactions():
    """List the node's on-chain transactions."""
    req = pb.ListTransactionsRequest()
    return 'ListTransactions', req


@entrypoint.command()
@option('--addr-type',
        nargs=1,
        type=AddressType(),
        autocompletion=_get_address_type,
        help='Bitcoin address type (P2WPKH '
        'or NP2WPKH).')
@handle_call
def newaddress(addr_type):
    """Create a new bitcoin address."""
    req = pb.NewAddressRequest(addr_type=addr_type)
    return 'NewAddress', req


@entrypoint.command()
@argument('node_uri', nargs=1)
@argument('funding_sat', nargs=1, type=int)
@option('--push-msat',
        nargs=1,
        type=int,
        help='Amount (taken from funding_sat'
        ') to be pushed to peer, in millisatoshi.')
@option('--private',
        is_flag=True,
        help='Whether the channel will be private '
        '(not anonunced).')
@handle_call
def openchannel(node_uri, funding_sat, push_msat, private):
    """Connect and open a channel with a peer."""
    req = pb.OpenChannelRequest(node_uri=node_uri,
                                funding_sat=funding_sat,
                                push_msat=push_msat,
                                private=private)
    return 'OpenChannel', req


@entrypoint.command()
@argument('payment_request', nargs=1)
@option('--amount-msat', nargs=1, type=int, help='Value to be paid.')
@option('--description',
        nargs=1,
        help='Invoice description, whose hash should'
        ' match the description hash in the payment request (if present).')
@option('--cltv-expiry-delta',
        nargs=1,
        type=int,
        help='Delta to use for the '
        'time-lock of the CLTV (absolute) extended to the final hop.')
@handle_call
def payinvoice(payment_request, amount_msat, description, cltv_expiry_delta):
    """Pay a LN invoice from its payment request (BOLT 11)."""
    req = pb.PayInvoiceRequest(payment_request=payment_request,
                               amount_msat=amount_msat,
                               description=description,
                               cltv_expiry_delta=cltv_expiry_delta)
    return 'PayInvoice', req


@entrypoint.command()
@argument('address', nargs=1)
@argument('amount_sat', nargs=1, type=int)
@option('--fee-sat-byte',
        nargs=1,
        type=int,
        help='Fee rate in satoshi per '
        'byte.')
@handle_call
def payonchain(address, amount_sat, fee_sat_byte):
    """Pay to a bitcoin address."""
    req = pb.PayOnChainRequest(address=address,
                               amount_sat=amount_sat,
                               fee_sat_byte=fee_sat_byte)
    return 'PayOnChain', req


@entrypoint.command()
@option('--password',
        prompt='Insert boltlight\'s password',
        hide_input=True,
        help='Boltlight\'s password.')
@handle_call
def unlocknode(password):
    """Unlock the wrapped node."""
    req = pb.UnlockNodeRequest(password=password)
    return 'UnlockNode', req


@entrypoint.command()
@handle_call
def balanceonchain():
    """Show the available on-chain balance."""
    req = pb.BalanceOnChainRequest()
    return 'BalanceOnChain', req
