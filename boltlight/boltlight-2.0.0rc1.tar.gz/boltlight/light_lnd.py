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
"""Implementation of boltlight.proto defined methods for lnd."""

from binascii import hexlify, unhexlify
from codecs import encode
from concurrent.futures import TimeoutError as TimeoutFutError, \
    ThreadPoolExecutor
from contextlib import contextmanager, ExitStack, suppress
from datetime import datetime
from functools import wraps
from logging import getLogger
from os import path

from grpc import channel_ready_future, composite_channel_credentials, \
    FutureTimeoutError, metadata_call_credentials, RpcError, secure_channel, \
    ssl_channel_credentials

from . import boltlight_pb2 as pb, rpc_pb2 as ln, rpc_pb2_grpc as lnrpc, \
    settings as sett, walletunlocker_pb2 as wu_ln, \
    walletunlocker_pb2_grpc as wu_lnrpc
from .errors import Err
from .utils.bitcoin import convert, Enforcer as Enf, get_channel_balances, \
    has_amount_encoded
from .utils.db import session_scope
from .utils.misc import get_path, handle_thread, set_defaults
from .utils.network import check_req_params, FakeContext, get_thread_timeout, \
    get_node_timeout
from .utils.security import get_secret, unlock_node_with_password

LOGGER = getLogger(__name__)

ERRORS = {
    'already connected to peer': {
        'fun': 'connect_failed'
    },
    'amount must be specified when paying a zero amount invoice': {
        'fun': 'amount_required'
    },
    'chain backend is still syncing': {
        'fun': 'node_error'
    },
    'channels cannot be created before the wallet is fully synced': {
        'fun': 'openchannel_failed'
    },
    'checksum failed': {
        'fun': 'invalid',
        'params': 'payment_request'
    },
    'checksum mismatch': {
        'fun': 'invalid',
        'params': 'address'
    },
    'Deadline Exceeded': {
        'fun': 'node_error'
    },
    'decoded address is of unknown format': {
        'fun': 'invalid',
        'params': 'address'
    },
    'edge not found': {
        'fun': 'invalid',
        'params': 'channel_id'
    },
    'encoding/hex': {
        'fun': 'invalid',
        'params': 'payment_hash'
    },
    'expected 1 macaroon, got': {
        'fun': 'node_error'
    },
    'greater than max expiry of': {
        'fun': 'invalid',
        'params': 'expiry'
    },
    'i/o timeout': {
        'fun': 'node_error'
    },
    'insufficient_balance': {
        'fun': 'insufficient_funds'
    },
    'invalid bech32 string length': {
        'fun': 'invalid',
        'params': 'payment_request'
    },
    'invalid index of': {
        'fun': 'invalid',
        'params': 'payment_request'
    },
    'invoice expired': {
        'fun': 'invoice_expired'
    },
    'invalid funding_satoshis': {
        'fun': 'openchannel_failed'
    },
    'invalid passphrase for master public key': {
        'fun': 'wrong_node_password'
    },
    'invoice is already paid': {
        'fun': 'invalid',
        'params': 'payment_request'
    },
    'is not online': {
        'fun': 'connect_failed'
    },
    'Name resolution failure': {
        'fun': 'node_error'
    },
    'no_route': {
        'fun': 'payinvoice_failed'
    },
    'Number of pending channels exceed maximum': {
        'fun': 'openchannel_failed'
    },
    'payment hash must': {
        'fun': 'invalid',
        'params': 'payment_hash'
    },
    'received funding error from': {
        'fun': 'openchannel_failed'
    },
    'signature mismatch': {
        'fun': 'node_error'
    },
    'Socket closed': {
        'fun': 'node_error'
    },
    'string not all lowercase or all uppercase': {
        'fun': 'invalid',
        'params': 'payment_request'
    },
    'unable to find a path to destination': {
        'fun': 'route_not_found'
    },
    'unable to find arbitrator': {
        'fun': 'closechannel_failed'
    },
    'unable to get best block info': {
        'fun': 'node_error'
    },
    'unable to gracefully close channel while peer is offline': {
        'fun': 'closechannel_failed'
    },
    'unable to locate invoice': {
        'fun': 'invoice_not_found'
    },
    'unable to route payment to destination: FeeInsufficient': {
        'fun': 'insufficient_fee'
    },
    'unable to route payment to destination: TemporaryChannelFailure': {
        'fun': 'payinvoice_failed'
    },
    'unknown service lnrpc.Lightning': {
        'fun': 'node_locked'
    }
}

LND_LN_TX = {'min_value': 1, 'max_value': 2**32 / 1000, 'unit': Enf.SATS}
LND_PUSH = {'min_value': 0, 'max_value': 2**24, 'unit': Enf.SATS}


def get_node_version():
    """Get node's version."""
    with suppress(RuntimeError):
        with _connect(FakeContext()) as stub:
            with suppress(RpcError):
                lnd_res = stub.GetInfo(ln.GetInfoRequest(),
                                       timeout=sett.IMPL_MIN_TIMEOUT)
                return lnd_res.version
    return ''


def get_settings(config, sec):
    """Get lnd settings."""
    sett.IMPL_SEC_TYPE = 'macaroon'
    lnd_values = ['LND_HOST', 'LND_PORT', 'LND_CERT']
    set_defaults(config, lnd_values)
    lnd_host = config.get(sec, 'LND_HOST')
    lnd_port = config.get(sec, 'LND_PORT')
    sett.LND_ADDR = f'{lnd_host}:{lnd_port}'
    lnd_tls_cert_dir = get_path(config.get(sec, 'LND_CERT_DIR'))
    lnd_tls_cert = config.get(sec, 'LND_CERT')
    lnd_tls_cert_path = path.join(lnd_tls_cert_dir, lnd_tls_cert)
    with open(lnd_tls_cert_path, 'rb') as file:
        cert = file.read()
    # Build ssl credentials using the cert
    sett.LND_CREDS_FULL = sett.LND_CREDS_SSL = ssl_channel_credentials(cert)


def unlock_node(ctx, password, session=None):
    """Unlock node with password saved in boltlight's DB."""
    with ExitStack() if session else session_scope(ctx) as ses:
        if session:
            ses = session
        lnd_pass = get_secret(ctx, ses, password, 'lnd', 'password')
        if not lnd_pass:
            Err().node_error(
                ctx, 'No password stored, add one by '
                'running boltlight-secure')
        lnd_req = wu_ln.UnlockWalletRequest(wallet_password=lnd_pass)
        try:
            with _connect(ctx,
                          stub_class=wu_lnrpc.WalletUnlockerStub,
                          force_no_macaroon=True) as stub:
                stub.UnlockWallet(lnd_req, timeout=get_node_timeout(ctx))
        except RpcError as err:
            if 'unknown service' in str(err):
                LOGGER.info('Node is already unlocked')
            else:
                _handle_error(ctx, str(err))


def update_settings(macaroon):
    """Update lnd specific settings."""
    if macaroon:
        LOGGER.info('Connecting to lnd in secure mode (tls + macaroon)')
        sett.LND_MAC = macaroon
        # Build meta data credentials
        auth_creds = metadata_call_credentials(_metadata_callback)
        # Combine the cert credentials and the macaroon auth credentials
        # Such that every call is properly encrypted and authenticated
        sett.LND_CREDS_FULL = composite_channel_credentials(
            sett.LND_CREDS_SSL, auth_creds)
    else:
        LOGGER.info('Connecting to lnd in insecure mode')


def _handle_rpc_errors(func):
    """Catch gRPC errors."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RpcError as error:
            return _handle_error(args[1], error)

    return wrapper


@_handle_rpc_errors
def BalanceOffChain(_req, ctx):
    """Return the off-chain balance available across all channels."""
    channels = ListChannels(pb.ListChannelsRequest(), ctx).channels
    return get_channel_balances(channels)


@_handle_rpc_errors
def BalanceOnChain(_req, ctx):
    """Return the on-chain balance in satoshi of the running LN node."""
    res = pb.BalanceOnChainResponse()
    lnd_req = ln.WalletBalanceRequest()
    with _connect(ctx) as stub:
        lnd_res = stub.WalletBalance(lnd_req, timeout=get_node_timeout(ctx))
        res = pb.BalanceOnChainResponse(
            total_sat=lnd_res.total_balance,
            confirmed_sat=lnd_res.confirmed_balance)
    return res


@_handle_rpc_errors
def CheckInvoice(req, ctx):
    """Check if a LN invoice has been paid."""
    check_req_params(ctx, req, 'payment_hash')
    res = pb.CheckInvoiceResponse()
    lnd_req = ln.PaymentHash(r_hash=unhexlify(req.payment_hash))
    with _connect(ctx) as stub:
        lnd_res = stub.LookupInvoice(lnd_req, timeout=get_node_timeout(ctx))
        res.state = _get_invoice_state(lnd_res)
    return res


@_handle_rpc_errors
def CloseChannel(req, ctx):
    """Try to close a LN chanel."""
    check_req_params(ctx, req, 'channel_id')
    channel_id = 0
    try:
        channel_id = int(req.channel_id)
    except ValueError:
        Err().invalid(ctx, 'channel_id')
    lnd_req = ln.ChanInfoRequest(chan_id=channel_id)
    with _connect(ctx) as stub:
        lnd_res = stub.GetChanInfo(lnd_req, timeout=get_node_timeout(ctx))
        txid, vout = lnd_res.chan_point.split(':')
        chan_point = ln.ChannelPoint(funding_txid_str=txid,
                                     output_index=int(vout))
        lnd_req = ln.CloseChannelRequest(channel_point=chan_point,
                                         force=req.force)
        with ThreadPoolExecutor(max_workers=1) as executor:
            close_time = get_node_timeout(ctx,
                                          min_time=sett.CLOSE_TIMEOUT_NODE)
            future = executor.submit(_close_channel, lnd_req, close_time)
            try:
                lnd_res = future.result(timeout=get_thread_timeout(ctx))
                if lnd_res:
                    return pb.CloseChannelResponse(closing_txid=lnd_res)
            except TimeoutFutError:
                executor.shutdown(wait=False)
            except RpcError as err:
                _handle_error(ctx, err)
            except RuntimeError as err:
                _handle_error(ctx, str(err))
    return pb.CloseChannelResponse()


@_handle_rpc_errors
def CreateInvoice(req, ctx):
    """Create a LN invoice (bolt 11)."""
    expiry = sett.EXPIRY_TIME
    if req.expiry:
        expiry = req.expiry
    lnd_req = ln.Invoice(memo=req.description,
                         expiry=expiry,
                         fallback_addr=req.fallback_addr)
    if req.min_final_cltv_expiry:
        Enf.check_value(ctx,
                        req.min_final_cltv_expiry,
                        enforce=Enf.MIN_FINAL_CLTV_EXPIRY)
        lnd_req.cltv_expiry = req.min_final_cltv_expiry
    if req.amount_msat:
        lnd_req.value_msat = req.amount_msat
    res = pb.CreateInvoiceResponse()
    with _connect(ctx) as stub:
        lnd_res = stub.AddInvoice(lnd_req, timeout=get_node_timeout(ctx))
        payment_hash_str = ''
        if lnd_res.r_hash:
            payment_hash_str = hexlify(lnd_res.r_hash).decode()
        res.payment_hash = payment_hash_str
        res.payment_request = lnd_res.payment_request
        if payment_hash_str:
            lnd_req = ln.PaymentHash(r_hash=lnd_res.r_hash)
            lnd_res = stub.LookupInvoice(lnd_req,
                                         timeout=get_node_timeout(ctx))
            res.expires_at = lnd_res.creation_date + lnd_res.expiry
    return res


@_handle_rpc_errors
def DecodeInvoice(req, ctx):
    """Return information of an invoice from its payment request (bolt 11)."""
    check_req_params(ctx, req, 'payment_request')
    if req.description:
        Err().unimplemented_parameter(ctx, 'description')
    lnd_req = ln.PayReqString(pay_req=req.payment_request)
    res = pb.DecodeInvoiceResponse()
    with _connect(ctx) as stub:
        lnd_res = stub.DecodePayReq(lnd_req, timeout=get_node_timeout(ctx))
        res.amount_msat = lnd_res.num_satoshis * 1000
        res.timestamp = lnd_res.timestamp
        res.payment_hash = lnd_res.payment_hash
        res.description = lnd_res.description
        res.destination_pubkey = lnd_res.destination
        res.description_hash = lnd_res.description_hash
        res.expiry = lnd_res.expiry
        res.min_final_cltv_expiry = lnd_res.cltv_expiry
        res.fallback_addr = lnd_res.fallback_addr
        for lnd_route in lnd_res.route_hints:
            _add_route_hint(res, lnd_route)
    return res


@_handle_rpc_errors
def GetNodeInfo(_req, ctx):
    """Return info about the running LN node."""
    res = pb.GetNodeInfoResponse()
    lnd_req = ln.GetInfoRequest()
    with _connect(ctx) as stub:
        lnd_res = stub.GetInfo(lnd_req, timeout=get_node_timeout(ctx))
        res = pb.GetNodeInfoResponse(identity_pubkey=lnd_res.identity_pubkey,
                                     alias=lnd_res.alias,
                                     color=lnd_res.color,
                                     block_height=lnd_res.block_height)
        if lnd_res.chains[0].network == 'mainnet':
            res.network = pb.Network.MAINNET
        elif lnd_res.chains[0].network == 'testnet':
            res.network = pb.Network.TESTNET
        elif lnd_res.chains[0].network == 'regtest':
            res.network = pb.Network.REGTEST
        if lnd_res.uris:
            res.node_uri = lnd_res.uris[0]
    return res


@_handle_rpc_errors
def ListChannels(req, ctx):
    """Return a list of channels of the running LN node."""
    res = pb.ListChannelsResponse()
    lnd_req = ln.ListChannelsRequest()
    with _connect(ctx) as stub:
        lnd_res = stub.ListChannels(lnd_req, timeout=get_node_timeout(ctx))
        for lnd_chan in lnd_res.channels:
            _add_channel(res,
                         lnd_chan,
                         pb.Channel.OPEN,
                         active_only=req.active_only,
                         open_chan=True)
        if not req.active_only:
            lnd_req = ln.PendingChannelsRequest()
            lnd_res = stub.PendingChannels(lnd_req,
                                           timeout=get_node_timeout(ctx))
            for lnd_chan in lnd_res.pending_open_channels:
                _add_channel(res, lnd_chan, pb.Channel.PENDING_OPEN)
            for lnd_chan in lnd_res.pending_closing_channels:
                _add_channel(res, lnd_chan, pb.Channel.PENDING_MUTUAL_CLOSE)
            for lnd_chan in lnd_res.pending_force_closing_channels:
                _add_channel(res, lnd_chan, pb.Channel.PENDING_FORCE_CLOSE)
            for lnd_chan in lnd_res.waiting_close_channels:
                _add_channel(res, lnd_chan, pb.Channel.UNKNOWN)
    return res


@_handle_rpc_errors
def ListInvoices(req, ctx):
    """Return a list of lightning invoices created by the running LN node."""
    if not req.max_items:
        req.max_items = sett.MAX_INVOICES
    res = pb.ListInvoicesResponse()
    lnd_req = ln.ListInvoiceRequest(reversed=req.search_order,
                                    num_max_invoices=req.max_items *
                                    sett.INVOICES_TIMES)
    stop = False
    with _connect(ctx) as stub:
        while True:
            lnd_res = stub.ListInvoices(lnd_req, timeout=get_node_timeout(ctx))
            if not lnd_res.invoices:
                break
            if req.search_order:
                lnd_res.CopyFrom(
                    ln.ListInvoiceResponse(
                        invoices=reversed(lnd_res.invoices),
                        first_index_offset=lnd_res.first_index_offset,
                        last_index_offset=lnd_res.last_index_offset))
            stop = _parse_invoices(res, lnd_res.invoices, req)
            if stop:
                break
            if req.search_order:
                lnd_req.index_offset = lnd_res.first_index_offset
            else:
                lnd_req.index_offset = lnd_res.last_index_offset
        if req.list_order != req.search_order:
            res.CopyFrom(
                pb.ListInvoicesResponse(invoices=reversed(res.invoices)))
    return res


@_handle_rpc_errors
def ListPayments(_req, ctx):
    """Return a list of lightning invoices paid by the running LN node."""
    res = pb.ListPaymentsResponse()
    lnd_req = ln.ListPaymentsRequest()
    with _connect(ctx) as stub:
        lnd_res = stub.ListPayments(lnd_req, timeout=get_node_timeout(ctx))
        for lnd_payment in lnd_res.payments:
            _add_payment(res, lnd_payment)
    return res


@_handle_rpc_errors
def ListPeers(_req, ctx):
    """Return a list of peers connected to the running LN node."""
    res = pb.ListPeersResponse()
    lnd_req = ln.ListPeersRequest()
    with _connect(ctx) as stub:
        lnd_res = stub.ListPeers(lnd_req, timeout=get_node_timeout(ctx))
        for lnd_peer in lnd_res.peers:
            peer = res.peers.add(pubkey=lnd_peer.pub_key,
                                 address=lnd_peer.address)
            lnd_req = ln.NodeInfoRequest(pub_key=lnd_peer.pub_key)
            with suppress(RpcError):
                lnd_res = stub.GetNodeInfo(lnd_req,
                                           timeout=get_node_timeout(ctx))
                peer.alias = lnd_res.node.alias
                peer.color = lnd_res.node.color
    return res


@_handle_rpc_errors
def ListTransactions(_req, ctx):
    """Return a list of on-chain transactions of the running LN node."""
    res = pb.ListTransactionsResponse()
    lnd_req = ln.GetTransactionsRequest()
    with _connect(ctx) as stub:
        lnd_res = stub.GetTransactions(lnd_req, timeout=get_node_timeout(ctx))
        for lnd_transaction in lnd_res.transactions:
            _add_transaction(res, lnd_transaction)
    return res


@_handle_rpc_errors
def NewAddress(req, ctx):
    """Create a new bitcoin address under control of the running LN node."""
    res = pb.NewAddressResponse()
    if req.addr_type == pb.Address.P2WPKH:
        # in lnd WITNESS_PUBKEY_HASH = 0;
        lnd_req = ln.NewAddressRequest(type=0)
    else:
        # in lnd NESTED_PUBKEY_HASH = 1;
        lnd_req = ln.NewAddressRequest(type=1)
    with _connect(ctx) as stub:
        lnd_res = stub.NewAddress(lnd_req, timeout=get_node_timeout(ctx))
        res = pb.NewAddressResponse(address=lnd_res.address)
    return res


@_handle_rpc_errors
def OpenChannel(req, ctx):
    """Try to connect and open a channel with a peer."""
    res = pb.OpenChannelResponse()
    check_req_params(ctx, req, 'node_uri', 'funding_sat')
    try:
        pubkey, host = req.node_uri.split('@')
    except ValueError:
        Err().invalid(ctx, 'node_uri')
    peer_address = ln.LightningAddress(pubkey=pubkey, host=host)
    lnd_req = ln.ConnectPeerRequest(addr=peer_address, perm=True)
    with _connect(ctx) as stub:
        try:
            lnd_res = stub.ConnectPeer(lnd_req, timeout=get_node_timeout(ctx))
        except RpcError as err:
            # pylint: disable=no-member
            if 'already connected to peer' not in err.details():
                # pylint: enable=no-member
                Err().connect_failed(ctx)
        Enf.check_value(ctx, req.funding_sat, Enf.FUNDING_SATOSHIS)
        lnd_req = ln.OpenChannelRequest(node_pubkey=unhexlify(pubkey),
                                        private=req.private,
                                        local_funding_amount=req.funding_sat)
        if req.push_msat:
            if req.push_msat >= 1000 * req.funding_sat:
                Err().value_too_high(ctx, req.push_msat)
            lnd_req.push_sat = convert(ctx,
                                       Enf.MSATS,
                                       Enf.SATS,
                                       req.push_msat,
                                       Enf.SATS,
                                       enforce=LND_PUSH)
        lnd_res = stub.OpenChannelSync(lnd_req, timeout=get_node_timeout(ctx))
        res.funding_txid = lnd_res.funding_txid_str
        if not lnd_res.funding_txid_str:
            txid = _txid_bytes_to_str(lnd_res.funding_txid_bytes)
            res.funding_txid = txid
    return res


@_handle_rpc_errors
def PayInvoice(req, ctx):
    """Try to pay a LN invoice from its payment request (bolt 11).

    An amount can be specified if the invoice doesn't already have it included.
    If a description hash is included in the invoice, its preimage must be
    included in the request.
    """
    check_req_params(ctx, req, 'payment_request')
    amount_encoded = has_amount_encoded(req.payment_request)
    res = pb.PayInvoiceResponse()
    lnd_req = ln.SendRequest(payment_request=req.payment_request)
    if req.cltv_expiry_delta:
        Enf.check_value(ctx,
                        req.cltv_expiry_delta,
                        enforce=Enf.CLTV_EXPIRY_DELTA)
        lnd_req.final_cltv_delta = req.cltv_expiry_delta
    if req.amount_msat and amount_encoded:
        Err().unsettable(ctx, 'amount_msat')
    elif req.amount_msat and not amount_encoded and Enf.check_value(
            ctx, req.amount_msat, LND_LN_TX):
        lnd_req.amt_msat = req.amount_msat
    elif not amount_encoded:
        check_req_params(ctx, req, 'amount_msat')
    with _connect(ctx) as stub:
        lnd_res = stub.SendPaymentSync(lnd_req, timeout=get_node_timeout(ctx))
        if lnd_res.payment_preimage:
            res.payment_preimage = hexlify(lnd_res.payment_preimage)
        elif lnd_res.payment_error:
            _handle_error(ctx, lnd_res.payment_error)
    return res


@_handle_rpc_errors
def PayOnChain(req, ctx):
    """Try to pay a bitcoin address."""
    check_req_params(ctx, req, 'address', 'amount_sat')
    Enf.check_value(ctx, req.amount_sat, enforce=Enf.OC_TX)
    lnd_req = ln.SendCoinsRequest(addr=req.address, amount=req.amount_sat)
    if req.fee_sat_byte:
        Enf.check_value(ctx, req.fee_sat_byte, enforce=Enf.OC_FEE)
        lnd_req.sat_per_byte = req.fee_sat_byte
    res = pb.PayOnChainResponse()
    with _connect(ctx) as stub:
        lnd_res = stub.SendCoins(lnd_req, timeout=get_node_timeout(ctx))
        res.txid = lnd_res.txid
    return res


@_handle_rpc_errors
def UnlockNode(req, ctx):
    """Try to unlock node."""
    return unlock_node_with_password(ctx, req, unlock_node)


# pylint: disable=too-many-arguments,too-many-branches
def _add_channel(res, lnd_chan, state, active_only=False, open_chan=False):
    """Add a channel to a ListChannelsResponse."""
    if active_only and not lnd_chan.active:
        return
    if lnd_chan.ListFields():
        if not open_chan:
            pending_chan = lnd_chan
            lnd_chan = pending_chan.channel
            if not lnd_chan.ListFields():
                return
        local_balance = lnd_chan.local_balance
        remote_balance = lnd_chan.remote_balance
        channel = res.channels.add(
            funding_txid=lnd_chan.channel_point.split(':')[0],
            capacity_msat=int(lnd_chan.capacity * 1000),
            state=state,
            local_reserve_sat=lnd_chan.local_chan_reserve_sat,
            remote_reserve_sat=lnd_chan.remote_chan_reserve_sat)
        if open_chan:
            if lnd_chan.initiator:
                if remote_balance < lnd_chan.local_constraints.dust_limit_sat:
                    local_balance += lnd_chan.commit_fee - remote_balance
                else:
                    local_balance += lnd_chan.commit_fee
            else:
                if local_balance < lnd_chan.local_constraints.dust_limit_sat:
                    remote_balance += lnd_chan.commit_fee - local_balance
                else:
                    remote_balance += lnd_chan.commit_fee
            channel.remote_pubkey = lnd_chan.remote_pubkey
            channel.channel_id = str(lnd_chan.chan_id)
            channel.to_self_delay = lnd_chan.csv_delay
            channel.private = lnd_chan.private
            channel.active = lnd_chan.active
        else:
            channel.remote_pubkey = lnd_chan.remote_node_pub
            channel.active = False
            commit_fee = 0
            if isinstance(pending_chan,
                          ln.PendingChannelsResponse.PendingOpenChannel):
                commit_fee = pending_chan.commit_fee
            if isinstance(pending_chan,
                          ln.PendingChannelsResponse.WaitingCloseChannel):
                commit_fee = lnd_chan.capacity - local_balance - remote_balance
            if commit_fee:
                if lnd_chan.initiator == ln.INITIATOR_LOCAL:
                    local_balance += commit_fee
                elif lnd_chan.initiator == ln.INITIATOR_REMOTE:
                    remote_balance += commit_fee
        if lnd_chan.capacity == local_balance + remote_balance:
            channel.local_balance_msat = int(local_balance * 1000)
            channel.remote_balance_msat = int(remote_balance * 1000)
    # pylint: enable=too-many-arguments,too-many-branches


def _add_invoice(res, lnd_invoice, invoice_state):
    """Add an invoice to a ListInvoicesResponse."""
    if lnd_invoice.ListFields():
        invoice = res.invoices.add(
            timestamp=lnd_invoice.creation_date,
            payment_hash=hexlify(lnd_invoice.r_hash),
            description=lnd_invoice.memo,
            description_hash=hexlify(lnd_invoice.description_hash),
            expiry=lnd_invoice.expiry,
            fallback_addr=lnd_invoice.fallback_addr,
            state=invoice_state,
            payment_request=lnd_invoice.payment_request,
            amount_received_msat=lnd_invoice.amt_paid_msat)
        invoice.amount_encoded_msat = lnd_invoice.value * 1000
        if lnd_invoice.value_msat:
            invoice.amount_encoded_msat = lnd_invoice.value_msat
        for lnd_route in lnd_invoice.route_hints:
            _add_route_hint(invoice, lnd_route)


def _add_payment(res, lnd_payment):
    """Add a payment to a ListPaymentsResponse."""
    if lnd_payment.ListFields():
        res.payments.add(payment_hash=lnd_payment.payment_hash,
                         amount_msat=lnd_payment.value_msat,
                         timestamp=int(lnd_payment.creation_time_ns / 10**9),
                         fee_msat=lnd_payment.fee_msat,
                         payment_preimage=lnd_payment.payment_preimage)


def _add_route_hint(res, lnd_route):
    """Add a route hint and its hop hints to a DecodeInvoiceResponse."""
    if lnd_route.ListFields():
        grpc_route = res.route_hints.add()
    for lnd_hop in lnd_route.hop_hints:
        grpc_route.hop_hints.add(
            pubkey=lnd_hop.node_id,
            short_channel_id=str(lnd_hop.chan_id),
            fee_base_msat=lnd_hop.fee_base_msat,
            fee_proportional_millionths=lnd_hop.fee_proportional_millionths,
            cltv_expiry_delta=lnd_hop.cltv_expiry_delta)


def _add_transaction(res, lnd_transaction):
    """Add a transaction to a ListTransactionsResponse."""
    if lnd_transaction.ListFields():
        res.transactions.add(txid=lnd_transaction.tx_hash,
                             amount_sat=lnd_transaction.amount,
                             confirmations=lnd_transaction.num_confirmations,
                             block_hash=lnd_transaction.block_hash,
                             block_height=lnd_transaction.block_height,
                             timestamp=lnd_transaction.time_stamp,
                             fee_sat=lnd_transaction.total_fees)


def _check_timestamp(req, lnd_invoice):
    """Decide if invoice has to be skipped (not added to response).

    Check creation_date against search_timestamp in order to decide.
    """
    if not req.search_timestamp:
        return False
    if req.list_order:
        # descending list_order
        if req.search_order:
            # descending search_order: use descending list, skip newer invoices
            # will stop when list reaches max_items size
            if lnd_invoice.creation_date >= req.search_timestamp:
                return True
        else:
            # ascending search_order: use ascending list, skip older invoices
            # must flip the list at the end
            if lnd_invoice.creation_date <= req.search_timestamp:
                return True
    else:
        # ascending list_order
        if req.search_order:
            # descending search_order: use descending list, skip newer invoices
            # must flip the list at the end
            if lnd_invoice.creation_date >= req.search_timestamp:
                return True
        else:
            # ascending search_order: use ascending list, skip older invoices
            # will stop when list reaches max_items size
            if lnd_invoice.creation_date <= req.search_timestamp:
                return True
    return False


@handle_thread
def _close_channel(lnd_req, close_timeout):
    """Close a LN channel and return a closing TXID or raise an exception."""
    lnd_res = None
    try:
        with _connect(FakeContext()) as stub:
            for lnd_res in stub.CloseChannel(lnd_req, timeout=close_timeout):
                LOGGER.debug('[ASYNC] CloseChannel released response: %s',
                             str(lnd_res).replace('\n', ''))
                if lnd_res.close_pending.txid:
                    lnd_res = _txid_bytes_to_str(lnd_res.close_pending.txid)
                    break
    except RpcError as err:
        # pylint: disable=no-member
        error = err.details() if hasattr(err, 'details') else err
        # pylint: enable=no-member
        LOGGER.debug('[ASYNC] CloseChannel terminated with error: %s', error)
        raise err
    except RuntimeError as err:
        raise err
    return lnd_res


@contextmanager
def _connect(ctx, stub_class=None, force_no_macaroon=False):
    """Securely connect to the lnd node using gRPC."""
    creds = sett.LND_CREDS_FULL
    if force_no_macaroon:
        creds = sett.LND_CREDS_SSL
    channel = secure_channel(sett.LND_ADDR, creds)
    future_channel = channel_ready_future(channel)
    try:
        future_channel.result(timeout=get_node_timeout(ctx))
    except FutureTimeoutError:
        # Handle gRPC channel that did not connect
        Err().node_error(ctx, 'Failed to dial server')
    else:
        if stub_class is None:
            stub_class = lnrpc.LightningStub
        stub = stub_class(channel)
        yield stub
        channel.close()


def _get_invoice_state(lnd_invoice):
    """Return the invoice state."""
    now = datetime.now().timestamp()
    if lnd_invoice.state == ln.Invoice.SETTLED:
        return pb.Invoice.PAID
    if lnd_invoice.state == ln.Invoice.OPEN or \
            lnd_invoice.state == ln.Invoice.ACCEPTED:
        if (lnd_invoice.creation_date + lnd_invoice.expiry) < now:
            return pb.Invoice.EXPIRED
        return pb.Invoice.PENDING
    if lnd_invoice.state == ln.Invoice.CANCELED:
        return pb.Invoice.EXPIRED
    return pb.Invoice.UNKNOWN


def _handle_error(ctx, error):
    """Report error received by lnd.

    This is always terminating: raises a grpc.RpcError to the API caller.
    """
    error = error.details() if hasattr(error, 'details') else error
    if not isinstance(error, str):
        error = 'Could not decode error message'
    Err().report_error(ctx, error)


def _metadata_callback(_ctx, callback):
    """Get lnd macaroon."""
    macaroon = encode(sett.LND_MAC, 'hex')
    callback([('macaroon', macaroon)], None)


def _parse_invoices(res, invoices, req):
    """Decide if invoice has to be added and which with state.

    Return True when added max_items invoices."""
    if not any([req.paid, req.pending, req.expired, req.unknown]):
        req.paid = req.pending = req.expired = req.unknown = True
    for lnd_invoice in invoices:
        if _check_timestamp(req, lnd_invoice):
            continue
        invoice_state = _get_invoice_state(lnd_invoice)
        if req.paid and invoice_state == pb.Invoice.PAID:
            _add_invoice(res, lnd_invoice, invoice_state)
        if req.pending and invoice_state == pb.Invoice.PENDING:
            _add_invoice(res, lnd_invoice, invoice_state)
        if req.expired and invoice_state == pb.Invoice.EXPIRED:
            _add_invoice(res, lnd_invoice, invoice_state)
        if req.unknown and invoice_state == pb.Invoice.UNKNOWN:
            _add_invoice(res, lnd_invoice, invoice_state)
        if len(res.invoices) == req.max_items:
            return True
    return False


def _txid_bytes_to_str(txid):
    """Decode big-endian TXID bytes to a little-endian TXID string."""
    return encode(txid[::-1], 'hex').decode()
