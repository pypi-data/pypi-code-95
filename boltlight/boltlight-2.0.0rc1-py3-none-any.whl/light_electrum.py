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
"""Implementation of boltlight.proto defined methods for electrum."""

from ast import literal_eval
from json import dumps
from concurrent.futures import TimeoutError as TimeoutFutError, \
    ThreadPoolExecutor
from contextlib import ExitStack, suppress
from logging import getLogger

from . import boltlight_pb2 as pb, settings as sett
from .errors import Err
from .utils.bitcoin import convert, Enforcer as Enf, get_address_type, \
    get_channel_balances, has_amount_encoded
from .utils.db import session_scope
from .utils.misc import handle_thread, set_defaults
from .utils.network import check_req_params, get_thread_timeout, \
    FakeContext, JSONRPCSession
from .utils.security import get_secret, unlock_node_with_password

LOGGER = getLogger(__name__)

ERRORS = {
    'Bad bech32 checksum': {
        'fun': 'invalid',
        'params': 'payment_request'
    },
    'Forbidden': {
        'fun': 'wrong_node_password'
    },
    'Hostname does not resolve': {
        'fun': 'connect_failed'
    },
    'Invalid node ID, must be 33 bytes and hexadecimal': {
        'fun': 'invalid',
        'params': 'node_uri'
    },
    'This invoice has expired': {
        'fun': 'invoice_expired'
    },
    'wallet not loaded': {
        'fun': 'node_locked'
    }
}

ELE_LN_TX = {'min_value': 1, 'max_value': 2**32, 'unit': Enf.SATS}


def get_node_version():
    """Get node's version."""
    rpc_ele = ElectrumRPC()
    with suppress(RuntimeError):
        ele_res, is_err = rpc_ele.getinfo(FakeContext())
        if not is_err:
            return ele_res.get('version', '')
    return ''


def get_settings(config, sec):
    """Get electrum settings."""
    ele_values = ['ELE_HOST', 'ELE_PORT', 'ELE_USER']
    set_defaults(config, ele_values)
    sett.ELE_HOST = config.get(sec, 'ELE_HOST')
    sett.ELE_PORT = config.get(sec, 'ELE_PORT')
    sett.ELE_USER = config.get(sec, 'ELE_USER')
    sett.IMPL_SEC_TYPE = 'password'


def unlock_node(ctx, password, session=None):
    """Unlock node with password saved in boltlight's DB."""
    with ExitStack() if session else session_scope(ctx) as ses:
        if session:
            ses = session
        ele_pass = get_secret(ctx, ses, password, 'electrum', 'password')
        # update password, allowing to change it during boltlight execution
        update_settings(ele_pass)
        rpc_ele = ElectrumRPC()
        ele_res, is_err = rpc_ele.load_wallet(ctx)
        if is_err:
            _handle_error(ctx, ele_res)


def update_settings(password):
    """Update electrum specific settings."""
    ele_pass = password.decode()
    sett.RPC_URL = \
        f'http://{sett.ELE_USER}:{ele_pass}@{sett.ELE_HOST}:{sett.ELE_PORT}'


def BalanceOffChain(_req, ctx):
    """Return the off-chain balance available across all channels."""
    channels = ListChannels(pb.ListChannelsRequest(), ctx).channels
    return get_channel_balances(channels)


def BalanceOnChain(_req, ctx):
    """Return the on-chain balance in satoshi of the running LN node."""
    rpc_ele = ElectrumRPC()
    ele_res, is_err = rpc_ele.getbalance(ctx)
    if is_err:
        _handle_error(ctx, ele_res)
    res = pb.BalanceOnChainResponse(confirmed_sat=convert(
        ctx, Enf.BTC, Enf.SATS, ele_res.get('confirmed'), Enf.SATS))
    res.total_sat = res.confirmed_sat + convert(
        ctx, Enf.BTC, Enf.SATS, ele_res.get('unconfirmed'), Enf.SATS)
    return res


def CheckInvoice(req, ctx):
    """Check if a LN invoice has been paid."""
    check_req_params(ctx, req, 'payment_hash')
    rpc_ele = ElectrumRPC()
    ele_req = {'key': req.payment_hash}
    ele_res, is_err = rpc_ele.getrequest(ctx, ele_req)
    if is_err:
        _handle_error(ctx, ele_res)
    return pb.CheckInvoiceResponse(state=_get_invoice_state(ele_res))


def CloseChannel(req, ctx):
    """Try to close a LN channel."""
    check_req_params(ctx, req, 'channel_id')
    rpc_ele = ElectrumRPC()
    ele_res, is_err = rpc_ele.list_channels(ctx)
    if is_err:
        _handle_error(ctx, ele_res)
    ele_req = {}
    for ele_chan in ele_res:
        if ele_chan.get('channel_id') == req.channel_id:
            ele_req['channel_point'] = ele_chan['channel_point']
            break
    if 'channel_point' not in ele_req:
        Err().invalid(ctx, 'channel_id')
    if req.force:
        ele_req['force'] = True
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_close_channel, ele_req)
        try:
            ele_res = future.result(timeout=get_thread_timeout(ctx))
            if ele_res:
                return pb.CloseChannelResponse(closing_txid=ele_res)
        except RuntimeError as ele_err:
            try:
                error = literal_eval(str(ele_err))
                if isinstance(error, bytes):
                    error = ('Bytes received instead of string (hint: trying '
                             'to close a channel while the peer is offline?)')
                _handle_error(ctx, error)
            except (SyntaxError, ValueError):
                Err().report_error(ctx, str(ele_err))
        except TimeoutFutError:
            executor.shutdown(wait=False)
    return pb.CloseChannelResponse()


def CreateInvoice(req, ctx):
    """Create a LN invoice (bolt 11)."""
    check_req_params(ctx, req, 'amount_msat')
    if req.min_final_cltv_expiry:
        Err().unimplemented_parameter(ctx, 'min_final_cltv_expiry')
    if req.fallback_addr:
        Err().unimplemented_parameter(ctx, 'fallback_addr')
    amount_btc = convert(ctx,
                         Enf.MSATS,
                         Enf.BTC,
                         req.amount_msat,
                         Enf.MSATS,
                         enforce=ELE_LN_TX)
    ele_req = {'amount': amount_btc, 'expiration': sett.EXPIRY_TIME}
    if req.expiry:
        ele_req['expiration'] = req.expiry
    if req.description:
        ele_req['memo'] = req.description
    rpc_ele = ElectrumRPC()
    ele_res, is_err = rpc_ele.add_lightning_request(ctx, ele_req)
    if is_err:
        _handle_error(ctx, ele_res)
    timestamp = ele_res.get('timestamp')
    expires_in = ele_res.get('expiration')
    return pb.CreateInvoiceResponse(
        payment_request=ele_res.get('invoice'),
        payment_hash=ele_res.get('rhash'),
        expires_at=timestamp + expires_in if timestamp and expires_in else 0)


def DecodeInvoice(req, ctx):
    """Return information of an invoice from its payment request (bolt 11)."""
    check_req_params(ctx, req, 'payment_request')
    if req.description:
        Err().unimplemented_parameter(ctx, 'description')
    ele_req = {'invoice': req.payment_request}
    rpc_ele = ElectrumRPC()
    ele_res, is_err = rpc_ele.decode_invoice(ctx, ele_req)
    if is_err:
        _handle_error(ctx, ele_res)
    return pb.DecodeInvoiceResponse(amount_msat=int(
        ele_res.get('amount_msat', 0)),
                                    timestamp=ele_res.get('time'),
                                    payment_hash=ele_res.get('rhash'),
                                    destination_pubkey=ele_res.get('pubkey'),
                                    description=ele_res.get('message'),
                                    expiry=ele_res.get('exp'))


def GetNodeInfo(_req, ctx):
    """Return info about the running LN node."""
    rpc_ele = ElectrumRPC()
    ele_res, is_err = rpc_ele.nodeid(ctx)
    if is_err:
        _handle_error(ctx, ele_res)
    identity_pubkey = node_uri = ''
    if ele_res:
        identity_pubkey = ele_res
        if '@' in ele_res:
            identity_pubkey = ele_res.split('@')[0]
            node_uri = ele_res
    ele_res, is_err = rpc_ele.getinfo(ctx)
    if is_err:
        _handle_error(ctx, ele_res)
    res = pb.GetNodeInfoResponse(identity_pubkey=identity_pubkey,
                                 node_uri=node_uri,
                                 block_height=max(
                                     0, ele_res.get('blockchain_height')))
    ele_path = ele_res.get('path')
    if ele_path:
        res.network = pb.Network.MAINNET
        if ele_path.split('/')[-1] == 'testnet':
            res.network = pb.Network.TESTNET
        elif ele_path.split('/')[-1] == 'regtest':
            res.network = pb.Network.REGTEST
    return res


def ListChannels(req, ctx):
    """Return a list of channels of the running LN node."""
    rpc_ele = ElectrumRPC()
    ele_res, is_err = rpc_ele.list_channels(ctx)
    if is_err:
        _handle_error(ctx, ele_res)
    res = pb.ListChannelsResponse()
    for ele_chan in ele_res:
        _add_channel(ctx, res, ele_chan, req.active_only)
    return res


# pylint: disable=too-many-branches
def ListInvoices(req, ctx):
    """Return a list of lightning invoices created by the running LN node."""
    if not req.max_items:
        req.max_items = sett.MAX_INVOICES
    res = pb.ListInvoicesResponse()
    ele_req = {
        'paid': req.paid,
        'pending': req.pending,
        'expired': req.expired
    }
    filter_inv = True
    # Return unfiltered invoices list if no filter parameter is given
    if not any(
            getattr(req, f)
            for f in ('paid', 'pending', 'expired', 'unknown')):
        filter_inv = False
    rpc_ele = ElectrumRPC()
    ele_res, is_err = rpc_ele.list_requests(ctx, ele_req)
    if is_err:
        _handle_error(ctx, ele_res)
    ele_res = sorted(ele_res,
                     reverse=req.search_order,
                     key=lambda t: t.get('timestamp', 0))
    for ele_inv in ele_res:
        if req.search_timestamp:
            inv_ts = ele_inv.get('timestamp', 0)
            if req.search_order and inv_ts > req.search_timestamp:
                continue
            if not req.search_order and inv_ts < req.search_timestamp:
                continue
        state = _get_invoice_state(ele_inv)
        if filter_inv:
            if not req.paid and state == pb.Invoice.PAID:
                continue
            if not req.pending and state == pb.Invoice.PENDING:
                continue
            if not req.expired and state == pb.Invoice.EXPIRED:
                continue
            if not req.unknown and state == pb.Invoice.UNKNOWN:
                continue
        _add_invoice(res, ele_inv)
        if len(res.invoices) == req.max_items:
            break
    if req.list_order != req.search_order:
        res.CopyFrom(pb.ListInvoicesResponse(invoices=reversed(res.invoices)))
    return res


# pylint: enable=too-many-branches


def ListPayments(_req, ctx):
    """Return a list of lightning invoices paid by the running LN node."""
    rpc_ele = ElectrumRPC()
    ele_res, is_err = rpc_ele.lightning_history(ctx)
    if is_err:
        _handle_error(ctx, ele_res)
    res = pb.ListPaymentsResponse()
    for ele_payment in ele_res:
        _add_payment(res, ele_payment)
    return res


def ListPeers(_req, ctx):
    """Return a list of peers connected to the running LN node."""
    rpc_ele = ElectrumRPC()
    ele_res, is_err = rpc_ele.list_peers(ctx)
    if is_err:
        _handle_error(ctx, ele_res)
    res = pb.ListPeersResponse()
    for ele_peer in ele_res:
        res.peers.add(address=ele_peer.get('address'),
                      pubkey=ele_peer.get('node_id'))
        # alias and RGB color not available in electrum response
    return res


def ListTransactions(_req, ctx):
    """Return a list of on-chain transactions of the running LN node."""
    rpc_ele = ElectrumRPC()
    ele_res, is_err = rpc_ele.onchain_history(ctx)
    if is_err:
        _handle_error(ctx, ele_res)
    res = pb.ListTransactionsResponse()
    for ele_tx in ele_res.get('transactions', []):
        _add_transaction(ctx, res, ele_tx)
    return res


def NewAddress(req, ctx):
    """Create a new bitcoin address under control of the running LN node."""
    rpc_ele = ElectrumRPC()
    res = pb.NewAddressResponse()
    ele_req = {'unused': True, 'receiving': True}
    ele_res, is_err = rpc_ele.listaddresses(ctx, ele_req)
    if is_err:
        _handle_error(ctx, ele_res)
    LOGGER.debug('Listaddress response: %s, %s', ele_res, is_err)
    if ele_res:
        addr_type = get_address_type(ele_res[0])
        LOGGER.debug('The address types are: %s, %s', addr_type, req.addr_type)
        if addr_type != req.addr_type:
            Err().unimplemented_param_value(
                ctx, 'addr_type', pb.Address.Type.Name(req.addr_type))
        for addr in ele_res:
            if addr not in sett.ELE_RELEASED_ADDRESSES:
                sett.ELE_RELEASED_ADDRESSES.append(addr)
                res.address = addr
                break
    if not res.address:
        LOGGER.debug('The list of addresses provided by the listaddresses '
                     'API is exhausted, re-using existing ones')
        sett.ELE_RELEASED_ADDRESSES = [ele_res[0]]
        res.address = ele_res[0]
    return res


def OpenChannel(req, ctx):
    """Try to connect and open a channel with a peer."""
    check_req_params(ctx, req, 'node_uri', 'funding_sat')
    if not req.private:
        Err().unimplemented_param_value(ctx, 'private', 'False')
    rpc_ele = ElectrumRPC()
    amount_btc = convert(ctx,
                         Enf.SATS,
                         Enf.BTC,
                         req.funding_sat,
                         Enf.SATS,
                         enforce=Enf.FUNDING_SATOSHIS)
    ele_req = {'connection_string': req.node_uri, 'amount': amount_btc}
    if req.push_msat:
        if req.push_msat >= 1000 * req.funding_sat:
            Err().value_too_high(ctx, req.push_msat)
        ele_req['push_amount'] = convert(ctx,
                                         Enf.MSATS,
                                         Enf.BTC,
                                         req.push_msat,
                                         Enf.SATS,
                                         enforce=Enf.PUSH_MSAT)
    ele_res, is_err = rpc_ele.open_channel(ctx, ele_req)
    if is_err:
        _handle_error(ctx, ele_res)
    return pb.OpenChannelResponse(funding_txid=ele_res.split(':')[0])


def PayInvoice(req, ctx):
    """Try to pay a LN invoice from its payment request (bolt 11).

    Electrum doesn't currently support the payment of invoices:
    - with amount not set (or 0)
    - with description_hash encoded (description needed to decode/pay invoice)
    - that set a custom expiry (cltv_expiry_delta) for the payment
    """
    check_req_params(ctx, req, 'payment_request')
    amount_encoded = has_amount_encoded(req.payment_request)
    if amount_encoded and req.amount_msat:
        Err().unsettable(ctx, 'amount_msat')
    if req.amount_msat:
        Err().unimplemented_parameter(ctx, 'amount_msat')
    if not amount_encoded:
        Err().amount_required(ctx)
    if req.description:
        Err().unimplemented_parameter(ctx, 'description')
    if req.cltv_expiry_delta:
        Err().unimplemented_parameter(ctx, 'cltv_expiry_delta')
    rpc_ele = ElectrumRPC()
    ele_req = {'invoice': req.payment_request}
    ele_res, is_err = rpc_ele.lnpay(ctx, ele_req)
    if is_err:
        _handle_error(ctx, ele_res)
    elif not ele_res.get('success'):
        Err().payinvoice_failed(ctx)
    return pb.PayInvoiceResponse(payment_preimage=ele_res.get('preimage'))


def PayOnChain(req, ctx):
    """Try to pay a bitcoin address."""
    check_req_params(ctx, req, 'address', 'amount_sat')
    Enf.check_value(ctx, req.amount_sat, enforce=Enf.OC_TX)
    ele_req = {'destination': req.address, 'amount': req.amount_sat}
    if req.fee_sat_byte:
        Enf.check_value(ctx, req.fee_sat_byte, enforce=Enf.OC_FEE)
        ele_req['feerate'] = req.fee_sat_byte
    rpc_ele = ElectrumRPC()
    ele_res, is_err = rpc_ele.payto(ctx, ele_req)
    if is_err:
        _handle_error(ctx, ele_res)
    ele_req = {'tx': ele_res}
    ele_res, is_err = rpc_ele.broadcast(ctx, ele_req)
    if is_err:
        _handle_error(ctx, ele_res)
    return pb.PayOnChainResponse(txid=ele_res)


def UnlockNode(req, ctx):
    """Try to unlock node."""
    return unlock_node_with_password(ctx, req, unlock_node)


def _add_channel(ctx, res, ele_chan, active_only):
    """Add a channel to a ListChannelsResponse."""
    state = _get_channel_state(ele_chan)
    active = state == pb.Channel.OPEN and ele_chan.get('peer_state') == 'GOOD'
    if state < 0 or (active_only and not active):
        return
    grpc_chan = res.channels.add(
        state=state,
        remote_pubkey=ele_chan.get('remote_pubkey'),
        short_channel_id=ele_chan.get('short_channel_id'),
        channel_id=ele_chan.get('channel_id'),
        active=active,
        local_balance_msat=convert(ctx, Enf.SATS, Enf.MSATS,
                                   ele_chan.get('local_balance'), Enf.MSATS),
        remote_balance_msat=convert(ctx, Enf.SATS, Enf.MSATS,
                                    ele_chan.get('remote_balance'), Enf.MSATS))
    loc_reserve = ele_chan.get('local_reserve', 0)
    grpc_chan.local_reserve_sat = int(loc_reserve) if loc_reserve else 0
    rem_reserve = ele_chan.get('remote_reserve', 0)
    grpc_chan.remote_reserve_sat = int(rem_reserve) if rem_reserve else 0
    chan_point = ele_chan.get('channel_point')
    if chan_point:
        grpc_chan.funding_txid = chan_point.split(':')[0]
    grpc_chan.capacity_msat = \
        grpc_chan.remote_balance_msat + grpc_chan.local_balance_msat


def _add_invoice(res, ele_inv):
    """Add an invoice to a ListInvoicesResponse."""
    invoice = res.invoices.add(amount_encoded_msat=ele_inv.get('amount_msat'),
                               timestamp=ele_inv.get('timestamp'),
                               payment_hash=ele_inv.get('rhash'),
                               description=ele_inv.get('message'),
                               state=_get_invoice_state(ele_inv),
                               payment_request=ele_inv.get('invoice'))
    expires_in = ele_inv.get('expiration')
    invoice.expiry = invoice.timestamp + expires_in \
        if invoice.timestamp and expires_in else 0


def _add_payment(res, ele_payment):
    """Add a payment to a ListPaymentsResponse."""
    if (ele_payment.get('type') == 'payment'
            and ele_payment.get('direction') == 'sent'):
        res.payments.add(payment_hash=ele_payment.get('payment_hash'),
                         amount_msat=int(-ele_payment.get('amount_msat', 0)),
                         timestamp=ele_payment.get('timestamp'),
                         fee_msat=ele_payment.get('fee_msat'),
                         payment_preimage=ele_payment.get('preimage'))


def _add_transaction(ctx, res, ele_tx):
    """Add a transaction to a ListTransactionsResponse."""
    res.transactions.add(txid=ele_tx.get('txid'),
                         confirmations=ele_tx.get('confirmations'),
                         block_height=ele_tx.get('height'),
                         timestamp=ele_tx.get('timestamp'),
                         fee_sat=ele_tx.get('fee_sat'),
                         amount_sat=convert(ctx, Enf.BTC, Enf.SATS,
                                            ele_tx.get('bc_value'), Enf.SATS))


@handle_thread
def _close_channel(ele_req):
    """Close a LN channel and return a closing TXID or raise an exception."""
    rpc_ele = ElectrumRPC()
    ele_res = error = None
    try:
        ele_res, is_err = rpc_ele.close_channel(FakeContext(), ele_req)
        if is_err:
            error = ele_res
        else:
            LOGGER.debug('[ASYNC] CloseChannel terminated with response: %s',
                         ele_res)
    except RuntimeError as err:
        error = str(err)
    if error:
        LOGGER.debug('[ASYNC] CloseChannel terminated with error: %s', error)
        raise RuntimeError(error)
    return ele_res


def _get_channel_state(ele_chan):
    """Return the channel state."""
    state = ele_chan.get('state')
    if state in (
            'CLOSED',
            'REDEEMED',
    ):
        return -1
    if state in (
            'FUNDED',
            'OPENING',
            'PREOPENING',
    ):
        return pb.Channel.PENDING_OPEN
    if state in ('OPEN', ):
        return pb.Channel.OPEN
    if state in ('FORCE_CLOSING', ):
        return pb.Channel.PENDING_FORCE_CLOSE
    if state in ('CLOSING', 'SHUTDOWN'):
        return pb.Channel.PENDING_MUTUAL_CLOSE
    return pb.Channel.UNKNOWN


def _get_invoice_state(ele_inv):
    """Return the invoice state.

    States of electrum payment requests:
    PR_UNPAID   = 0
    PR_EXPIRED  = 1
    PR_UNKNOWN  = 2     # sent but not propagated
    PR_PAID     = 3     # send and propagated
    PR_INFLIGHT = 4     # unconfirmed
    PR_FAILED   = 5
    PR_ROUTING  = 6
    """
    status = ele_inv.get('status')
    if status in (3, ):
        return pb.Invoice.PAID
    if status in (
            0,
            2,
            4,
            6,
    ):
        return pb.Invoice.PENDING
    if status in (1, ):
        return pb.Invoice.EXPIRED
    return pb.Invoice.UNKNOWN


def _handle_error(ctx, ele_res):
    """Report errors of an electrum RPC response.

    This is always terminating: raises a grpc.RpcError to the API caller.
    """
    Err().report_error(ctx, ele_res)


class ElectrumRPC(JSONRPCSession):
    """Create and mantain an RPC session with electrum."""
    def __init__(self):
        super().__init__(headers={'content-type': 'application/json'})

    def __getattr__(self, name):
        def call_adapter(ctx, params=None, timeout=None):
            if not params:
                params = {}
            payload = dumps({
                'id': self._id_count,
                'method': name,
                'params': params,
                'jsonrpc': self._jsonrpc_ver
            })
            LOGGER.debug('RPC req: %s', payload)
            # pylint: disable=super-with-arguments
            return super(ElectrumRPC, self).call(ctx, payload, timeout=timeout)

        return call_adapter
