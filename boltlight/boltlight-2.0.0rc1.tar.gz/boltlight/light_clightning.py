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
"""Implementation of boltlight.proto defined methods for c-lightning."""

from ast import literal_eval
from concurrent.futures import TimeoutError as TimeoutFutError, \
    ThreadPoolExecutor
from contextlib import suppress
from datetime import datetime
from logging import CRITICAL, getLogger
from os import path

from pyln.client import LightningRpc, RpcError as ClightningRpcError

from . import boltlight_pb2 as pb, settings as sett
from .errors import Err
from .utils.bitcoin import Enforcer as Enf, get_channel_balances, \
    has_amount_encoded, split_node_uri
from .utils.misc import get_path, handle_thread, set_defaults
from .utils.network import check_req_params, FakeContext, get_thread_timeout

LOGGER = getLogger(__name__)

ERRORS = {
    "'fundchannel_start' failed": {
        'fun': 'openchannel_failed'
    },
    'Bad bech32 string': {
        'fun': 'invalid',
        'params': 'payment_request'
    },
    'Cannot afford transaction': {
        'fun': 'insufficient_funds'
    },
    'Channel ID not found': {
        'fun': 'invalid',
        'params': 'channel_id'
    },
    'Connection refused': {
        'fun': 'node_error'
    },
    'Could not find a route': {
        'fun': 'route_not_found'
    },
    'does not match description': {
        'fun': 'incorrect_description'
    },
    'Error broadcasting transaction': {
        'fun': 'payonchain_failed'
    },
    'Exchanging init messages: Operation now in progress': {
        'fun': 'connect_failed'
    },
    'Fallback address does not match our network': {
        'fun': 'invalid',
        'params': 'fallback_addr'
    },
    'Fallback address not valid': {
        'fun': 'invalid',
        'params': 'fallback_addr'
    },
    'Given id is not a channel ID or short channel ID': {
        'fun': 'invalid',
        'params': 'channel_id'
    },
    # this error happens when giving a short fallback address (e.g. "sd")
    'Incorrect \'id\' in response': {
        'fun': 'invalid',
        'params': 'fallback_addr'
    },
    'Invoice expired': {
        'fun': 'invoice_expired',
    },
    'msatoshi parameter required': {
        'fun': 'amount_required'
    },
    'no description to check': {
        'fun': 'missing_parameter',
        'params': 'description'
    },
    'Parsing accept_channel': {
        'fun': 'openchannel_failed'
    },
    'payment_hash: should be a 32 byte hex value': {
        'fun': 'invalid',
        'params': 'payment_hash'
    },
    'Peer already': {
        'fun': 'openchannel_failed'
    },
    'Still syncing with bitcoin network': {
        'fun': 'openchannel_failed'
    },
    'They sent error': {
        'fun': 'openchannel_failed'
    },
    'Unknown peer': {
        'fun': 'connect_failed'
    },
}


def get_node_version():
    """Get node's version."""
    rpc_cl = ClightningRPC()
    with suppress(RuntimeError):
        cl_res, is_err = rpc_cl.getinfo(FakeContext())
        if not is_err:
            return cl_res.get('version', '')
    return ''


def get_settings(config, sec):
    """Get c-lightning settings."""
    cl_values = ['CL_RPC']
    set_defaults(config, cl_values)
    cl_rpc_dir = get_path(config.get(sec, 'CL_RPC_DIR'))
    cl_rpc = config.get(sec, 'CL_RPC')
    cl_rpc_path = path.join(cl_rpc_dir, cl_rpc)
    if not path.exists(cl_rpc_path):
        raise RuntimeError(f'Missing {cl_rpc} file')
    sett.RPC_URL = cl_rpc_path


def unlock_node(_ctx, _password, _session=None):
    """Return a successful response (no locking system for c-lightning)."""
    return pb.UnlockNodeResponse()


def update_settings(_dummy):
    """Update c-lightning specific settings."""


def BalanceOffChain(_req, ctx):
    """Return the off-chain balance available across all channels."""
    channels = ListChannels(pb.ListChannelsRequest(), ctx).channels
    return get_channel_balances(channels)


def BalanceOnChain(_req, ctx):
    """Return the on-chain balance in satoshi of the running LN node."""
    rpc_cl = ClightningRPC()
    cl_res, is_err = rpc_cl.listfunds(ctx)
    if is_err:
        _handle_error(ctx, cl_res)
    tot_funds = conf_funds = 0.0
    for output in cl_res.get('outputs', []):
        output_value = output.get('value', 0)
        tot_funds += output_value
        if output.get('status') == 'confirmed':
            conf_funds += output_value
    return pb.BalanceOnChainResponse(total_sat=int(tot_funds),
                                     confirmed_sat=int(conf_funds))


def CheckInvoice(req, ctx):
    """Check if a LN invoice has been paid."""
    rpc_cl = ClightningRPC()
    check_req_params(ctx, req, 'payment_hash')
    invoice = None
    cl_req = {'payment_hash': req.payment_hash}
    cl_res, is_err = rpc_cl.listinvoices(ctx, cl_req)
    if is_err:
        _handle_error(ctx, cl_res)
    for inv in cl_res.get('invoices', []):
        if inv.get('payment_hash') == req.payment_hash:
            invoice = inv
            break
    if not invoice:
        Err().invoice_not_found(ctx)
    return pb.CheckInvoiceResponse(state=_get_invoice_state(invoice))


def CloseChannel(req, ctx):
    """Try to close a LN channel."""
    check_req_params(ctx, req, 'channel_id')
    cl_req = {'peer_id': req.channel_id}
    if req.force:
        # setting a 1 second timeout to force an immediate unilateral close
        cl_req['unilateraltimeout'] = 1
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_close_channel, cl_req)
        try:
            cl_res = future.result(timeout=get_thread_timeout(ctx))
            if cl_res:
                return pb.CloseChannelResponse(closing_txid=cl_res.get('txid'))
        except RuntimeError as cl_err:
            try:
                error = literal_eval(str(cl_err))
                _handle_error(ctx, error)
            except (SyntaxError, ValueError):
                Err().report_error(ctx, str(cl_err))
        except TimeoutFutError:
            executor.shutdown(wait=False)
    return pb.CloseChannelResponse()


def CreateInvoice(req, ctx):
    """Create a LN invoice (bolt 11)."""
    rpc_cl = ClightningRPC()
    cl_req = {}
    if req.min_final_cltv_expiry:
        cl_req['cltv'] = req.min_final_cltv_expiry
    if req.amount_msat and Enf.check_value(
            ctx, req.amount_msat, enforce=Enf.LN_PAYREQ):
        cl_req['msatoshi'] = req.amount_msat
    else:
        cl_req['msatoshi'] = 'any'
    description = ''
    if req.description:
        description = req.description
    cl_req['description'] = description
    label = _create_label()
    cl_req['label'] = label
    if req.expiry:
        cl_req['expiry'] = req.expiry
    else:
        cl_req['expiry'] = sett.EXPIRY_TIME
    if req.fallback_addr:
        cl_req['fallbacks'] = [req.fallback_addr]
    cl_res, is_err = rpc_cl.invoice(ctx, cl_req)
    if is_err:
        _handle_error(ctx, cl_res)
    return pb.CreateInvoiceResponse(payment_hash=cl_res.get('payment_hash'),
                                    payment_request=cl_res.get('bolt11'),
                                    expires_at=cl_res.get('expires_at'))


def DecodeInvoice(req, ctx):
    """Return information of an invoice from its payment request (bolt 11)."""
    rpc_cl = ClightningRPC()
    check_req_params(ctx, req, 'payment_request')
    cl_req = {'bolt11': req.payment_request}
    if req.description:
        cl_req['description'] = req.description
    cl_res, is_err = rpc_cl.decodepay(ctx, cl_req)
    if is_err:
        _handle_error(ctx, cl_res)
    res = pb.DecodeInvoiceResponse(
        amount_msat=int(cl_res.get('msatoshi', 0)),
        timestamp=cl_res.get('created_at'),
        payment_hash=cl_res.get('payment_hash'),
        description=cl_res.get('description'),
        destination_pubkey=cl_res.get('payee'),
        description_hash=cl_res.get('description_hash'),
        expiry=cl_res.get('expiry'),
        min_final_cltv_expiry=cl_res.get('min_final_cltv_expiry'))
    fallbacks = cl_res.get('fallbacks', [])
    if len(fallbacks):
        res.fallback_addr = fallbacks[0].get('addr', '')
    for cl_route in cl_res.get('routes', []):
        _add_route_hint(res, cl_route)
    return res


def GetNodeInfo(_req, ctx):
    """Return info about the running LN node."""
    rpc_cl = ClightningRPC()
    cl_res, is_err = rpc_cl.getinfo(ctx)
    if is_err:
        _handle_error(ctx, cl_res)
    color = cl_res.get('color')
    res = pb.GetNodeInfoResponse(identity_pubkey=cl_res.get('id'),
                                 alias=cl_res.get('alias'),
                                 block_height=int(cl_res.get('blockheight',
                                                             0)),
                                 color=f'#{color}' if color else '')
    if res.identity_pubkey:
        addresses = cl_res.get('address', [])
        if len(addresses):
            address = addresses[0]
            addr = address.get('address')
            port = address.get('port')
            if addr and port:
                res.node_uri = f'{res.identity_pubkey}@{addr}:{port}'
    network = cl_res.get('network')
    if network == 'bitcoin':
        res.network = pb.Network.MAINNET
    elif network == 'testnet':
        res.network = pb.Network.TESTNET
    elif network == 'regtest':
        res.network = pb.Network.REGTEST
    return res


def ListChannels(req, ctx):
    """Return a list of channels of the running LN node."""
    rpc_cl = ClightningRPC()
    cl_res, is_err = rpc_cl.listpeers(ctx)
    if is_err:
        _handle_error(ctx, cl_res)
    res = pb.ListChannelsResponse()
    for cl_peer in cl_res.get('peers', []):
        for cl_chan in cl_peer.get('channels', []):
            _add_channel(res, cl_peer, cl_chan, req.active_only)
    return res


def ListPayments(_req, ctx):
    """Return a list of lightning invoices paid by the running LN node."""
    rpc_cl = ClightningRPC()
    cl_res, is_err = rpc_cl.listsendpays(ctx)
    if is_err:
        _handle_error(ctx, cl_res)
    res = pb.ListPaymentsResponse()
    for cl_payment in cl_res.get('payments', []):
        _add_payment(res, cl_payment)
    return res


def ListPeers(_req, ctx):
    """Return a list of peers connected to the running LN node."""
    rpc_cl = ClightningRPC()
    cl_res, is_err = rpc_cl.listpeers(ctx)
    if is_err:
        _handle_error(ctx, cl_res)
    res = pb.ListPeersResponse()
    for peer in cl_res.get('peers', []):
        # Filtering disconnected peers
        if peer.get('connected') is not True:
            continue
        grpc_peer = res.peers.add(pubkey=peer.get('id'))
        if grpc_peer.pubkey:
            cl_req = {'node_id': grpc_peer.pubkey}
            cl_res, is_err = rpc_cl.listnodes(ctx, cl_req)
            nodes = cl_res.get('nodes', [])
            if len(nodes):
                node = nodes[0]
                grpc_peer.alias = node.get('alias', '')
                color = node.get('color')
                grpc_peer.color = f'#{color}' if color else ''
        addresses = peer.get('netaddr', [])
        if len(addresses):
            grpc_peer.address = addresses[0]
    return res


def NewAddress(req, ctx):
    """Create a new bitcoin address under control of the running LN node."""
    rpc_cl = ClightningRPC()
    cl_req = {}
    if req.addr_type == pb.Address.P2WPKH:
        cl_req['addresstype'] = 'bech32'
    elif req.addr_type == pb.Address.NP2WPKH:
        cl_req['addresstype'] = 'p2sh-segwit'
    cl_res, is_err = rpc_cl.newaddr(ctx, cl_req)
    if is_err:
        _handle_error(ctx, cl_res)
    res = pb.NewAddressResponse(address=cl_res.get('bech32'))
    if not res.address:
        res.address = cl_res.get('p2sh-segwit', '')
    return res


def OpenChannel(req, ctx):
    """Try to connect and open a channel with a peer."""
    check_req_params(ctx, req, 'node_uri', 'funding_sat')
    pubkey, _ = split_node_uri(ctx, req.node_uri)
    rpc_cl = ClightningRPC()
    cl_req = {'peer_id': req.node_uri}
    cl_res, is_err = rpc_cl.connect(ctx, cl_req)
    if is_err:
        Err().connect_failed(ctx)
    Enf.check_value(ctx, req.funding_sat, Enf.FUNDING_SATOSHIS)
    cl_req = {'node_id': pubkey, 'amount': req.funding_sat}
    if req.private:
        cl_req['announce'] = False
    if req.push_msat and Enf.check_value(ctx, req.push_msat, Enf.PUSH_MSAT):
        if req.push_msat >= 1000 * req.funding_sat:
            Err().value_too_high(ctx, req.push_msat)
        cl_req['push_msat'] = req.push_msat
    cl_res, is_err = rpc_cl.fundchannel(ctx, cl_req)
    if is_err:
        _handle_error(ctx, cl_res)
    return pb.OpenChannelResponse(funding_txid=cl_res.get('txid'))


def PayInvoice(req, ctx):
    """Try to pay a LN invoice from its payment request (bolt 11).

    An amount can be specified if the invoice doesn't already have it included.
    If a description hash is included in the invoice, its preimage must be
    included in the request.
    """
    check_req_params(ctx, req, 'payment_request')
    rpc_cl = ClightningRPC()
    cl_req = {'bolt11': req.payment_request}
    amount_encoded = has_amount_encoded(req.payment_request)
    if amount_encoded and req.amount_msat:
        Err().unsettable(ctx, 'amount_msat')
    elif req.amount_msat and not amount_encoded:
        Enf.check_value(ctx, req.amount_msat, enforce=Enf.LN_TX)
        cl_req['msatoshi'] = req.amount_msat
    elif not amount_encoded:
        check_req_params(ctx, req, 'amount_msat')
    if req.description:
        Err().unimplemented_parameter(ctx, 'description')
    if req.cltv_expiry_delta:
        Enf.check_value(ctx,
                        req.cltv_expiry_delta,
                        enforce=Enf.CLTV_EXPIRY_DELTA)
        cl_req['maxdelay'] = req.cltv_expiry_delta
    cl_res, is_err = rpc_cl.pay(ctx, cl_req)
    if is_err:
        _handle_error(ctx, cl_res)
    return pb.PayInvoiceResponse(
        payment_preimage=cl_res.get('payment_preimage'))


def PayOnChain(req, ctx):
    """Try to pay a bitcoin address."""
    rpc_cl = ClightningRPC()
    check_req_params(ctx, req, 'address', 'amount_sat')
    Enf.check_value(ctx, req.amount_sat, enforce=Enf.OC_TX)
    cl_req = {'destination': req.address, 'satoshi': req.amount_sat}
    if req.fee_sat_byte:
        Enf.check_value(ctx, req.fee_sat_byte, enforce=Enf.OC_FEE)
        cl_req['feerate'] = f'{req.fee_sat_byte * 1000}perkb'
    cl_res, is_err = rpc_cl.withdraw(ctx, cl_req)
    if is_err:
        _handle_error(ctx, cl_res)
    return pb.PayOnChainResponse(txid=cl_res.get('txid'))


def UnlockNode(_req, _ctx):
    """Try to unlock node."""
    return unlock_node(None, None)


def _add_channel(res, cl_peer, cl_chan, active_only):
    """Add a channel to a ListChannelsResponse."""
    state = _get_channel_state(cl_chan)
    active = state == pb.Channel.OPEN and cl_peer.get('connected')
    if state < 0 or (active_only and not active):
        return
    grpc_chan = res.channels.add(
        active=active,
        capacity_msat=int(cl_chan.get('msatoshi_total', 0)),
        channel_id=cl_chan.get('channel_id'),
        funding_txid=cl_chan.get('funding_txid'),
        local_balance_msat=int(cl_chan.get('msatoshi_to_us', 0)),
        local_reserve_sat=cl_chan.get('our_channel_reserve_satoshis'),
        private=cl_chan.get('private'),
        remote_pubkey=cl_peer.get('id'),
        remote_reserve_sat=cl_chan.get('their_channel_reserve_satoshis'),
        short_channel_id=cl_chan.get('short_channel_id'),
        state=state,
        to_self_delay=int(cl_chan.get('our_to_self_delay', 0)))
    grpc_chan.remote_balance_msat = \
        grpc_chan.capacity_msat - grpc_chan.local_balance_msat


def _add_payment(res, cl_payment):
    """Add a payment to a ListPaymentsResponse."""
    if cl_payment.get('status') == 'failed':
        return
    grpc_payment = res.payments.add(
        payment_hash=cl_payment.get('payment_hash'),
        amount_msat=int(cl_payment.get('msatoshi_sent', 0)),
        timestamp=cl_payment.get('created_at'),
        payment_preimage=cl_payment.get('payment_preimage'))
    grpc_payment.fee_msat = max(
        0, grpc_payment.amount_msat - int(cl_payment.get('msatoshi', 0)))


def _add_route_hint(res, cl_route):
    """Add a route hint and its hop hints to a DecodeInvoiceResponse."""
    grpc_route = res.route_hints.add()
    for cl_hop in cl_route:
        grpc_route.hop_hints.add(
            pubkey=cl_hop.get('pubkey'),
            short_channel_id=cl_hop.get('short_channel_id'),
            fee_base_msat=cl_hop.get('fee_base_msat'),
            fee_proportional_millionths=cl_hop.get(
                'fee_proportional_millionths'),
            cltv_expiry_delta=cl_hop.get('cltv_expiry_delta'))


@handle_thread
def _close_channel(cl_req):
    """Close a LN channel and return a closing TXID or raise an exception."""
    rpc_cl = ClightningRPC()
    cl_res = error = None
    try:
        cl_res, is_err = rpc_cl.close(FakeContext(), cl_req)
        if is_err:
            error = cl_res
        else:
            LOGGER.debug('[ASYNC] CloseChannel terminated with response: %s',
                         cl_res)
    except RuntimeError as err:
        error = str(err)
    if error:
        LOGGER.debug('[ASYNC] CloseChannel terminated with error: %s', error)
        raise RuntimeError(error)
    return cl_res


def _create_label():
    """Create a label using microseconds (c-lightning specific)."""
    return str(int(datetime.now().timestamp() * 1e6))


def _get_channel_state(cl_chan):  # pylint: disable=too-many-return-statements
    """Return the channel state."""
    cl_state = cl_chan.get('state')
    if not cl_state or cl_state in ('CLOSED', ):
        return -1
    cl_state_details = cl_chan.get('status', [])
    for detail in cl_state_details:
        if 'ONCHAIN:All outputs resolved:' in detail:
            return -1
    if cl_state in ('CHANNELD_AWAITING_LOCKIN', ):
        return pb.Channel.PENDING_OPEN
    if cl_state in ('CHANNELD_NORMAL', ):
        return pb.Channel.OPEN
    for detail in cl_state_details:
        if 'ONCHAIN:Tracking mutual close transaction' in detail:
            return pb.Channel.PENDING_MUTUAL_CLOSE
        if 'ONCHAIN:Tracking our own unilateral close' in detail or \
                'ONCHAIN:2 outputs unresolved:' in detail or \
                'ONCHAIN:1 outputs unresolved:' in detail or \
                'ONCHAIN:Tracking their unilateral close' in detail:
            return pb.Channel.PENDING_FORCE_CLOSE
    if cl_state in ('CHANNELD_SHUTTING_DOWN', 'CLOSINGD_SIGEXCHANGE',
                    'CLOSINGD_COMPLETE'):
        return pb.Channel.PENDING_MUTUAL_CLOSE
    if cl_state in ('ONCHAIN', 'AWAITING_UNILATERAL', 'FUNDING_SPEND_SEEN'):
        return pb.Channel.PENDING_FORCE_CLOSE
    return pb.Channel.UNKNOWN


def _get_invoice_state(cl_invoice):
    """Return the invoice state."""
    status = cl_invoice.get('status')
    if status == 'paid':
        return pb.Invoice.PAID
    if status == 'unpaid':
        return pb.Invoice.PENDING
    if status == 'expired':
        return pb.Invoice.EXPIRED
    return pb.Invoice.UNKNOWN


def _handle_error(ctx, cl_res):
    """Report errors of a c-lightning RPC response.

    This is always terminating: raises a grpc.RpcError to the API caller.
    """
    Err().report_error(ctx, cl_res)


class ClightningRPC():  # pylint: disable=too-few-public-methods
    """Create and mantain an RPC session with c-lightning."""
    def __init__(self):
        logger = getLogger(self.__class__.__name__)
        logger.setLevel(CRITICAL)
        self._session = LightningRpc(sett.RPC_URL, logger=logger)

    def __getattr__(self, name):
        def call_adapter(ctx, params=None):
            if not params:
                params = {}
            LOGGER.debug("RPC req: '%s' '%s'", name, params)
            try:
                res = getattr(self._session, name)(**params)
                LOGGER.debug('RPC res: %s', res)
                return res, False
            except ClightningRpcError as err:
                err_msg = err.error.get('message')
                LOGGER.debug('RPC err: %s', err_msg)
                return err_msg, True
            except OSError as err:
                return Err().node_error(ctx, str(err))

        return call_adapter
