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
"""Implementation of boltlight.proto defined methods for eclair."""

from ast import literal_eval
from concurrent.futures import TimeoutError as TimeoutFutError, \
    ThreadPoolExecutor
from contextlib import suppress
from logging import getLogger
from string import ascii_lowercase, digits
from time import time, sleep

from requests.auth import HTTPBasicAuth

from . import boltlight_pb2 as pb, settings as sett
from .errors import Err
from .utils.bitcoin import Enforcer as Enf, get_address_type, \
    get_channel_balances, has_amount_encoded, split_node_uri
from .utils.misc import handle_thread, set_defaults
from .utils.network import check_req_params, FakeContext, get_thread_timeout, \
    get_node_timeout, JSONRPCSession

LOGGER = getLogger(__name__)

ERRORS = {
    'balance too low': {
        'fun': 'insufficient_funds',
    },
    'bech32 address does not match our blockchain': {
        'fun': 'invalid',
        'params': 'address'
    },
    'cannot execute command=close in state': {
        'fun': 'closechannel_failed'
    },
    'cannot open connection with oneself': {
        'fun': 'connect_failed'
    },
    'cannot route to self': {
        'fun': 'route_not_found'
    },
    'closing already in progress': {
        'fun': 'invalid',
        'params': 'channel_id'
    },
    'Connection refused': {
        'fun': 'node_error'
    },
    'Could not resolve host': {
        'fun': 'node_error'
    },
    'is neither a valid Base58 address': {
        'fun': 'invalid',
        'params': 'address'
    },
    'incorrect payment details': {
        'fun': 'invalid',
        'params': 'payment_request'
    },
    'insufficient funds': {
        'fun': 'insufficient_funds'
    },
    'manually specify an amount': {
        'fun': 'amount_required'
    },
    'peer sent error: ascii=': {
        'fun': 'openchannel_failed'
    },
    'Recv failure: Connection reset by peer': {
        'fun': 'node_error'
    },
    'route not found': {
        'fun': 'route_not_found'
    },
    'The form field \'invoice\' was malformed:': {
        'fun': 'invalid',
        'params': 'payment_request'
    },
    'The supplied authentication is invalid': {
        'fun': 'node_error'
    }
}


def get_node_version():
    """Get node's version."""
    rpc_ecl = EclairRPC()
    with suppress(RuntimeError):
        ecl_res, is_err = rpc_ecl.getinfo(FakeContext())
        if not is_err:
            return ecl_res.get('version', '')
    return ''


def get_settings(config, sec):
    """Get eclair settings."""
    sett.IMPL_SEC_TYPE = 'password'
    ecl_values = ['ECL_HOST', 'ECL_PORT']
    set_defaults(config, ecl_values)
    ecl_host = config.get(sec, 'ECL_HOST')
    ecl_port = config.get(sec, 'ECL_PORT')
    sett.RPC_URL = f'http://{ecl_host}:{ecl_port}'


def unlock_node(_ctx, _password, _session=None):
    """Return a successful response (no locking system for eclair)."""
    return pb.UnlockNodeResponse()


def update_settings(password):
    """Update eclair specific settings."""
    ecl_pass = password.decode()
    sett.ECL_PASS = ecl_pass


def BalanceOffChain(_req, ctx):
    """Return the off-chain balance available across all channels."""
    channels = ListChannels(pb.ListChannelsRequest(), ctx).channels
    return get_channel_balances(channels)


def BalanceOnChain(_req, ctx):
    """Return the on-chain balance in satoshi of the running LN node."""
    rpc_ecl = EclairRPC()
    ecl_res, is_err = rpc_ecl.onchainbalance(ctx)
    if is_err:
        _handle_error(ctx, ecl_res)
    confirmed = int(ecl_res.get('confirmed', 0))
    return pb.BalanceOnChainResponse(
        confirmed_sat=confirmed,
        total_sat=int(ecl_res.get('unconfirmed', 0)) + confirmed)


def CheckInvoice(req, ctx):
    """Check if a LN invoice has been paid."""
    check_req_params(ctx, req, 'payment_hash')
    ecl_req = {'paymentHash': req.payment_hash}
    rpc_ecl = EclairRPC()
    ecl_res, is_err = rpc_ecl.getreceivedinfo(ctx, ecl_req)
    if is_err or not ecl_res.get('status'):
        Err().invalid(ctx, 'payment_hash')
    return pb.CheckInvoiceResponse(state=_get_invoice_state(ecl_res))


def CloseChannel(req, ctx):
    """Try to close a LN chanel."""
    check_req_params(ctx, req, 'channel_id')
    ecl_req = {'channelId': req.channel_id}
    with ThreadPoolExecutor(max_workers=1) as executor:
        client_exp_time = ctx.time_remaining() + time()
        close_time = get_node_timeout(ctx, min_time=sett.CLOSE_TIMEOUT_NODE)
        future = executor.submit(_close_channel, ecl_req, req.force,
                                 close_time, client_exp_time)
        try:
            ecl_res = future.result(timeout=get_thread_timeout(ctx))
            if ecl_res:
                return pb.CloseChannelResponse(closing_txid=ecl_res)
        except TimeoutFutError:
            executor.shutdown(wait=False)
        except RuntimeError as ecl_err:
            try:
                if str(ecl_err) == 'Bad Request':
                    Err().invalid(ctx, 'channel_id')
                error = literal_eval(str(ecl_err))
                _handle_error(ctx, error)
            except (SyntaxError, ValueError):
                Err().report_error(ctx, str(ecl_err))
    return pb.CloseChannelResponse()


def CreateInvoice(req, ctx):
    """Create a LN invoice (bolt 11)."""
    if req.min_final_cltv_expiry:
        Err().unimplemented_parameter(ctx, 'min_final_cltv_expiry')
    ecl_req = {'description': req.description if req.description else ''}
    if req.amount_msat and Enf.check_value(
            ctx, req.amount_msat, enforce=Enf.LN_PAYREQ):
        ecl_req['amountMsat'] = req.amount_msat
    ecl_req['expireIn'] = sett.EXPIRY_TIME
    if req.expiry:
        ecl_req['expireIn'] = req.expiry
    if req.fallback_addr:
        ecl_req['fallbackAddress'] = req.fallback_addr
    rpc_ecl = EclairRPC()
    ecl_res, is_err = rpc_ecl.createinvoice(ctx, ecl_req)
    if is_err:
        _handle_error(ctx, ecl_res)
    timestamp = ecl_res.get('timestamp')
    expiry = ecl_res.get('expiry')
    return pb.CreateInvoiceResponse(payment_request=ecl_res.get('serialized'),
                                    payment_hash=ecl_res.get('paymentHash'),
                                    expires_at=timestamp +
                                    expiry if timestamp and expiry else 0)


def DecodeInvoice(req, ctx):
    """Return information of an invoice from its payment request (bolt 11)."""
    check_req_params(ctx, req, 'payment_request')
    if req.description:
        Err().unimplemented_parameter(ctx, 'description')
    ecl_req = {'invoice': req.payment_request}
    rpc_ecl = EclairRPC()
    ecl_res, is_err = rpc_ecl.parseinvoice(ctx, ecl_req)
    if 'invalid payment request' in ecl_res:
        # checking manually as error is not in json
        Err().invalid(ctx, 'payment_request')
    elif is_err:
        _handle_error(ctx, ecl_res)
    res = pb.DecodeInvoiceResponse(
        amount_msat=int(ecl_res.get('amount', 0)),
        timestamp=ecl_res.get('timestamp'),
        destination_pubkey=ecl_res.get('nodeId'),
        payment_hash=ecl_res.get('paymentHash'),
        expiry=ecl_res.get('expiry'),
        min_final_cltv_expiry=ecl_res.get('minFinalCltvExpiry'))
    description = ecl_res.get('description')
    if description and _is_description_hash(description):
        res.description_hash = description
    elif description:
        res.description = description
    if 'routingInfo' in ecl_res:
        for ecl_route in ecl_res['routingInfo']:
            _add_route_hint(res, ecl_route)
    return res


def GetNodeInfo(_req, ctx):
    """Return info about the running LN node."""
    rpc_ecl = EclairRPC()
    ecl_res, is_err = rpc_ecl.getinfo(ctx)
    if is_err:
        _handle_error(ctx, ecl_res)
    res = pb.GetNodeInfoResponse(identity_pubkey=ecl_res.get('nodeId'),
                                 alias=ecl_res.get('alias'),
                                 color=ecl_res.get('color'),
                                 block_height=ecl_res.get('blockHeight'),
                                 network=pb.Network.REGTEST)
    addresses = ecl_res.get('publicAddresses', [])
    if len(addresses) and res.identity_pubkey:
        res.node_uri = f'{res.identity_pubkey}@{addresses[0]}'
    chain_hash = ecl_res.get('chainHash')
    if chain_hash == sett.TEST_HASH:
        res.network = pb.Network.TESTNET
    elif chain_hash == sett.MAIN_HASH:
        res.network = pb.Network.MAINNET
    return res


def ListChannels(req, ctx):
    """Return a list of channels of the running LN node."""
    rpc_ecl = EclairRPC()
    ecl_res, is_err = rpc_ecl.channels(ctx)
    if is_err:
        _handle_error(ctx, ecl_res)
    res = pb.ListChannelsResponse()
    for channel in ecl_res:
        _add_channel(res, channel, req.active_only)
    return res


def ListPeers(_req, ctx):
    """Return a list of peers connected to the running LN node."""
    rpc_ecl = EclairRPC()
    ecl_res, is_err = rpc_ecl.peers(ctx)
    if is_err:
        _handle_error(ctx, ecl_res)
    res = pb.ListPeersResponse()
    if not ecl_res:
        return res
    for peer in ecl_res:
        # Filtering disconnected peers
        if peer.get('state') == 'DISCONNECTED':
            continue
        res.peers.add(pubkey=peer.get('nodeId'), address=peer.get('address'))
    ecl_res, _ = rpc_ecl.nodes(ctx)
    if isinstance(ecl_res, list):
        for node in ecl_res:
            for peer in res.peers:
                if node.get('nodeId') == peer.pubkey:
                    peer.alias = node.get('alias', '')
                    peer.color = node.get('rgbColor', '')
    return res


def ListTransactions(_req, ctx):
    """Return a list of on-chain transactions of the running LN node."""
    rpc_ecl = EclairRPC()
    ecl_res, is_err = rpc_ecl.onchaintransactions(ctx)
    if is_err:
        _handle_error(ctx, ecl_res)
    res = pb.ListTransactionsResponse()
    for ecl_tx in ecl_res:
        _add_transaction(res, ecl_tx)
    return res


def NewAddress(req, ctx):
    """Create a new bitcoin address under control of the running LN node."""
    rpc_ecl = EclairRPC()
    res = pb.NewAddressResponse()
    ecl_res, is_err = rpc_ecl.getnewaddress(ctx)
    if is_err:
        _handle_error(ctx, ecl_res)
    if ecl_res:
        addr_type = get_address_type(ecl_res)
        if addr_type != req.addr_type:
            Err().unimplemented_param_value(
                ctx, 'addr_type', pb.Address.Type.Name(req.addr_type))
        res.address = ecl_res
    return res


def OpenChannel(req, ctx):
    """Try to connect and open a channel with a peer."""
    check_req_params(ctx, req, 'node_uri', 'funding_sat')
    pubkey, _ = split_node_uri(ctx, req.node_uri)
    ecl_req = {'uri': req.node_uri}
    rpc_ecl = EclairRPC()
    ecl_res, is_err = rpc_ecl.connect(ctx, ecl_req)
    if 'connected' not in ecl_res:
        Err().connect_failed(ctx)
    Enf.check_value(ctx, req.funding_sat, Enf.FUNDING_SATOSHIS)
    ecl_req = {'nodeId': pubkey, 'fundingSatoshis': req.funding_sat}
    if req.push_msat and Enf.check_value(ctx, req.push_msat, Enf.PUSH_MSAT):
        if req.push_msat >= 1000 * req.funding_sat:
            Err().value_too_high(ctx, req.push_msat)
        ecl_req['pushMsat'] = req.push_msat
    if req.private:
        ecl_req['channelFlags'] = 0
    ecl_res, is_err = rpc_ecl.open(ctx, ecl_req)
    if 'created channel' not in ecl_res or is_err:
        _handle_error(ctx, ecl_res)
    with suppress(IndexError):
        channel_id = ecl_res.split(' ')[2]
        ecl_req = {'channelId': channel_id}
        ecl_res, _ = rpc_ecl.channel(ctx, ecl_req)
        data = ecl_res.get('data')
        commitments = data.get('commitments') if data else None
        if commitments:
            commit_input = commitments.get('commitInput')
            outpoint = commit_input.get('outPoint') if commit_input else None
            funding_txid = outpoint.split(':')[0] if outpoint else ''
            return pb.OpenChannelResponse(funding_txid=funding_txid)
    return pb.OpenChannelResponse()


def PayInvoice(req, ctx):
    """Try to pay a LN invoice from its payment request (bolt 11).

    An amount can be specified if the invoice doesn't already have it included.
    If a description hash is included in the invoice, its preimage must be
    included in the request.
    """
    check_req_params(ctx, req, 'payment_request')
    if req.cltv_expiry_delta:
        Err().unimplemented_parameter(ctx, 'cltv_expiry_delta')
    ecl_req = {'invoice': req.payment_request, 'blocking': True}
    amount_encoded = has_amount_encoded(req.payment_request)
    if req.amount_msat and amount_encoded:
        Err().unsettable(ctx, 'amount_msat')
    elif req.amount_msat and not amount_encoded and Enf.check_value(
            ctx, req.amount_msat, Enf.LN_TX):
        ecl_req['amountMsat'] = req.amount_msat
    elif not amount_encoded:
        check_req_params(ctx, req, 'amount_msat')
    rpc_ecl = EclairRPC()
    ecl_res, is_err = rpc_ecl.payinvoice(ctx, ecl_req)
    if 'malformed' in ecl_res:
        Err().invalid(ctx, 'payment_request')
    elif is_err or 'failures' in ecl_res:
        _handle_error(ctx, ecl_res)
    if 'paymentPreimage' not in ecl_res:
        Err().payinvoice_failed(ctx)
    return pb.PayInvoiceResponse(payment_preimage=ecl_res['paymentPreimage'])


def PayOnChain(req, ctx):
    """Try to pay a bitcoin address."""
    check_req_params(ctx, req, 'address', 'amount_sat')
    ecl_req = {
        'address': req.address,
        'confirmationTarget': sett.ECL_CONFIRMATIONS
    }
    Enf.check_value(ctx, req.amount_sat, enforce=Enf.OC_TX)
    ecl_req['amountSatoshis'] = req.amount_sat
    if req.fee_sat_byte:
        Err().unimplemented_parameter(ctx, 'fee_sat_byte')
    rpc_ecl = EclairRPC()
    ecl_res, is_err = rpc_ecl.sendonchain(ctx, ecl_req)
    if is_err:
        _handle_error(ctx, ecl_res)
    return pb.PayOnChainResponse(txid=ecl_res)


def UnlockNode(_req, _ctx):
    """Try to unlock node."""
    return unlock_node(None, None)


def _add_channel(res, ecl_chan, active_only):
    """Add a channel to a ListChannelsResponse."""
    state = _get_channel_state(ecl_chan)
    active = state == pb.Channel.OPEN and ecl_chan.get('state') == 'NORMAL'
    if state < 0 or (active_only and not active):
        return
    grpc_chan = res.channels.add(active=active,
                                 channel_id=ecl_chan.get('channelId'),
                                 remote_pubkey=ecl_chan.get('nodeId'),
                                 state=state)
    data = ecl_chan.get('data')
    short_channel_id = data.get('shortChannelId') if data else ''
    if short_channel_id:
        grpc_chan.short_channel_id = short_channel_id
    commitments = data.get('commitments') if data else None
    if not commitments:
        return
    if commitments.get('channelFlags') == 0:
        grpc_chan.private = True
    commit_input = commitments.get('commitInput')
    outpoint = commit_input.get('outPoint') if commit_input else None
    grpc_chan.funding_txid = outpoint.split(':')[0] if outpoint else ''
    loc_p = commitments.get('localParams')
    grpc_chan.to_self_delay = loc_p.get('toSelfDelay') if loc_p else 0
    grpc_chan.local_reserve_sat = loc_p.get('channelReserve') if loc_p else 0
    rem_p = commitments.get('remoteParams')
    grpc_chan.remote_reserve_sat = rem_p.get('channelReserve') if rem_p else 0
    local_commit = commitments.get('localCommit')
    spec = local_commit.get('spec') if local_commit else None
    grpc_chan.local_balance_msat = int(spec.get('toLocal', 0)) if spec else 0
    grpc_chan.remote_balance_msat = int(spec.get('toRemote', 0)) if spec else 0
    grpc_chan.capacity_msat = \
        grpc_chan.local_balance_msat + grpc_chan.remote_balance_msat


def _add_route_hint(res, ecl_route):
    """Add a route hint and its hop hints to a DecodeInvoiceResponse."""
    grpc_route = res.route_hints.add()
    for ecl_hop in ecl_route:
        grpc_route.hop_hints.add(
            pubkey=ecl_hop.get('nodeId'),
            short_channel_id=ecl_hop.get('shortChannelId'),
            fee_base_msat=ecl_hop.get('feeBase'),
            fee_proportional_millionths=ecl_hop.get(
                'feeProportionalMillionths'),
            cltv_expiry_delta=ecl_hop.get('cltvExpiryDelta'))


def _add_transaction(res, ecl_tx):
    """Add a transaction to a ListTransactionsResponse."""
    res.transactions.add(txid=ecl_tx.get('txid'),
                         amount_sat=int(ecl_tx.get('amount', 0)),
                         confirmations=ecl_tx.get('confirmations'),
                         timestamp=ecl_tx.get('timestamp'),
                         block_hash=ecl_tx.get('blockHash'),
                         fee_sat=ecl_tx.get('fees'))


# pylint: disable=too-many-locals, too-many-branches
@handle_thread
def _close_channel(ecl_req, force, close_timeout, client_expiry):
    """Close a LN channel and return a closing TXID or raise an exception."""
    ecl_res = error = None
    try:
        # subtracting timeout to close channel call to retrieve closing txid
        close_time = close_timeout - sett.IMPL_MIN_TIMEOUT
        if close_time < sett.IMPL_MIN_TIMEOUT:
            close_time = sett.IMPL_MIN_TIMEOUT
        rpc_ecl = EclairRPC()
        if force:
            ecl_res, is_err = rpc_ecl.forceclose(FakeContext(), ecl_req,
                                                 close_time)
        else:
            ecl_res, is_err = rpc_ecl.close(FakeContext(), ecl_req, close_time)
        chan_id = ecl_req['channelId']
        if chan_id in ecl_res and 'closed channel' not in ecl_res[chan_id]:
            raise RuntimeError(ecl_res[chan_id])
        if is_err:
            error = ecl_res
        else:
            LOGGER.debug('[ASYNC] CloseChannel terminated with response: %s',
                         ecl_res)
            ecl_res = None
            # while client has still time we check if txid is available
            while client_expiry > time() and not ecl_res:
                sleep(1)
                ecl_chan, is_err = rpc_ecl.channel(FakeContext(), ecl_req,
                                                   sett.IMPL_MIN_TIMEOUT)
                if is_err or not isinstance(ecl_chan,
                                            dict):  # pragma: no cover
                    continue
                data = ecl_chan.get('data')
                if data:
                    mut_closes = data.get('mutualClosePublished')
                    if len(mut_closes):
                        mut_close = mut_closes[0]
                        ecl_res = mut_close.get('txid')
                    loc_commit = data.get('localCommitPublished')
                    if loc_commit:
                        commit_tx = loc_commit.get('commitTx')
                        ecl_res = commit_tx.get('txid') if commit_tx else None
    except RuntimeError as err:
        error = str(err)
    if error:
        if isinstance(error, str):
            error = error.strip()
        LOGGER.debug('[ASYNC] CloseChannel terminated with error: %s', error)
        raise RuntimeError(error)
    return ecl_res


# pylint: enable=too-many-locals, too-many-branches


def _get_channel_state(ecl_chan):
    """Return the channel state."""
    ecl_state = ecl_chan.get('state')
    if ecl_state in ('CLOSED', ):
        return -1
    if ecl_state in ('WAIT_FOR_FUNDING_CONFIRMED', ):
        return pb.Channel.PENDING_OPEN
    if ecl_state in ('NORMAL', 'OFFLINE'):
        return pb.Channel.OPEN
    data = ecl_chan.get('data')
    if data:
        if data.get('mutualClosePublished'):
            return pb.Channel.PENDING_MUTUAL_CLOSE
        if data.get('localCommitPublished') or data.get(
                'remoteCommitPublished'):
            return pb.Channel.PENDING_FORCE_CLOSE
    return pb.Channel.UNKNOWN


def _get_invoice_state(ecl_invoice):
    """Return the invoice state."""
    status = ecl_invoice.get('status')
    status_type = status.get('type') if status else None
    if status_type == 'received':
        return pb.Invoice.PAID
    if status_type == 'pending':
        return pb.Invoice.PENDING
    if status_type == 'expired':
        return pb.Invoice.EXPIRED
    return pb.Invoice.UNKNOWN


def _handle_error(ctx, ecl_res):
    """Report errors of an eclair RPC response.

    This is always terminating: raises a grpc.RpcError to the API caller.
    """
    if not isinstance(ecl_res, dict):
        Err().report_error(ctx, ecl_res)
    failures = ecl_res.get('failures')
    if not failures:
        Err().report_error(ctx, ecl_res)
    errors = []
    for failure in failures:
        for value in failure.values():
            if isinstance(value, str):
                errors.append(value)
            elif isinstance(value, dict) and 'failureMessage' in value:
                errors.append(value['failureMessage'])
    error = ' + '.join(errors)
    Err().report_error(ctx, error)


def _is_description_hash(description):
    """Check if description is a hash."""
    allowed_set = set(ascii_lowercase + digits)
    return len(description) == 64 and ' ' not in description and \
        set(description).issubset(allowed_set)


class EclairRPC(JSONRPCSession):
    """Create and mantain an RPC session with eclair."""
    def __init__(self):
        super().__init__(auth=HTTPBasicAuth('', sett.ECL_PASS))

    def __getattr__(self, name):
        def call_adapter(ctx, data=None, timeout=None):
            url = f'{sett.RPC_URL}/{name}'
            if data is None:
                data = {}
            LOGGER.debug('RPC req: %s', data)
            # pylint: disable=super-with-arguments
            return super(EclairRPC, self).call(ctx, data, url, timeout)

        return call_adapter
