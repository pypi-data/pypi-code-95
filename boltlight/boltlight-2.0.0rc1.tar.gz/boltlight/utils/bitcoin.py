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
"""Bitcoin and Lightning Network utils module."""

from decimal import Context, Decimal, Inexact, InvalidOperation
from logging import getLogger

from .. import boltlight_pb2 as pb, settings as sett
from ..errors import Err

LOGGER = getLogger(__name__)


# pylint: disable=too-many-arguments
def convert(context, source, target, amount, max_precision, enforce=None):
    """Convert amount from source to target unit.

    Round the result to the specified maximum precision. If the output unit
    matches the max precision, the value is returned as an integer.

    If enforce is set, check the value against the given boundaries.
    """
    if not amount:
        return 0
    try:
        amount = Decimal(str(amount))
    except InvalidOperation:
        # An invalid number would be blocked by the interface,
        # so this case has to come from the node
        return Err().internal_value_error(context, amount)
    if enforce:
        ratio = enforce['unit']['decimal'] - source['decimal']
        Enforcer.check_value(context, amount.scaleb(ratio), enforce)
    ratio = target['decimal'] - source['decimal']
    decimals = target['decimal'] - max_precision['decimal']
    try:
        converted = amount.scaleb(ratio)
        # cuts the amount to the required precision,
        # raising exceptions in case of inexact conversion
        result = converted.quantize(
            Decimal(1).scaleb(decimals),
            context=Context(traps=[Inexact, InvalidOperation]))
        if max_precision['decimal'] == target['decimal']:
            return int(result)
        return float(result)
    except (Inexact, InvalidOperation):
        return Err().value_error(context, amount)


# pylint: enable=too-many-arguments


def get_address_type(address):
    """Return the type of a bitcoin address."""
    if address[0] in ['b', 't']:
        return pb.Address.P2WPKH
    return pb.Address.NP2WPKH


def get_channel_balances(channels):
    """Calculate channel balances from a ListChannelsResponse."""
    out_tot = out_tot_now = in_tot = in_tot_now = 0
    for chan in channels:
        if chan.state != pb.Channel.OPEN:
            continue
        out_tot += chan.local_balance_msat
        in_tot += chan.remote_balance_msat
        if not chan.active:
            continue
        local_reserve = chan.local_reserve_sat * 1000
        remote_reserve = chan.remote_reserve_sat * 1000
        out_tot_now += max(0, chan.local_balance_msat - local_reserve)
        in_tot_now += max(0, chan.remote_balance_msat - remote_reserve)
    return pb.BalanceOffChainResponse(out_tot_msat=int(out_tot),
                                      out_tot_now_msat=int(out_tot_now),
                                      in_tot_msat=int(in_tot),
                                      in_tot_now_msat=int(in_tot_now))


def has_amount_encoded(payment_request):
    """Check if a bech32 payment request has any amount encoded."""
    separator = payment_request.rfind('1')
    hrp = payment_request[:separator]
    return _has_numbers(set(hrp))


def split_node_uri(ctx, node_uri):
    """Split a LN node URI into pubkey and host address.

    If the URI is invalid terminate the RPC with an invalid node_uri error.
    """
    try:
        pubkey, host_addr = node_uri.split('@')
        if not pubkey or not host_addr:
            raise ValueError
        return pubkey, host_addr
    except ValueError:
        return Err().invalid(ctx, 'node_uri')


def _has_numbers(input_string):
    """Check if string contains any number."""
    return any(char.isdigit() for char in input_string)


class Enforcer():  # pylint: disable=too-few-public-methods
    """Enforce BOLTs rules and value limits."""

    BTC = {'name': 'btc', 'decimal': 0}
    MBTC = {'name': 'mbtc', 'decimal': 3}
    BITS = {'name': 'bits', 'decimal': 6}
    SATS = {'name': 'sats', 'decimal': 8}
    MSATS = {'name': 'msats', 'decimal': 11}

    DEFAULT = {'min_value': 0, 'unit': MSATS}

    # BOLT2 suggests (but does not enforce) a reserve of 1% of the channel
    # funding total, and the reserve cannot be lower than the dust limit.
    FUNDING_SATOSHIS = {
        'min_value': 100 * sett.DUST_LIMIT_SAT,
        'max_value': 2**24,
        'unit': SATS
    }
    PUSH_MSAT = {'max_value': 2**24 * 1000, 'unit': MSATS}
    LN_PAYREQ = {'min_value': 0, 'max_value': 2**32, 'unit': MSATS}
    LN_TX = {'min_value': 1, 'max_value': 2**32, 'unit': MSATS}

    OC_TX = {'min_value': 1, 'max_value': 21 * 10**14, 'unit': SATS}
    # assuming minimum 220 bytes tx and single 21M BTC input
    OC_FEE = {'min_value': 1, 'max_value': 21 * 10**14 // 220, 'unit': SATS}

    MIN_FINAL_CLTV_EXPIRY = {'min_value': 1, 'max_value': 5 * 10**8}
    CLTV_EXPIRY_DELTA = {'min_value': 1, 'max_value': 2**16}

    @staticmethod
    def check_value(context, value, enforce=None):
        """Check that value is between min_value and max_value."""
        if not enforce:
            enforce = Enforcer.DEFAULT
        if sett.ENFORCE:
            if 'min_value' in enforce and value < enforce['min_value']:
                Err().value_too_low(context, value)
            if 'max_value' in enforce and value > enforce['max_value']:
                Err().value_too_high(context, value)
        return True
