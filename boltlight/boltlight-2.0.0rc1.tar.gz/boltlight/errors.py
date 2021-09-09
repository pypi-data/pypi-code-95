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
"""The errors module for boltlight."""

from importlib import import_module
from logging import getLogger
from re import sub

from grpc import StatusCode

from . import settings as sett

LOGGER = getLogger(__name__)

ERRORS = {
    'amount_required': {
        'code': 'INVALID_ARGUMENT',
        'msg': 'A positive amount is required for empty invoices'
    },
    'connect_failed': {
        'code': 'CANCELLED',
        'msg': 'Connection to peer failed'
    },
    'closechannel_failed': {
        'code': 'CANCELLED',
        'msg': 'Failed to close channel'
    },
    'db_error': {
        'code': 'CANCELLED',
        'msg': 'Error accessing database'
    },
    'incorrect_description': {
        'code': 'INVALID_ARGUMENT',
        'msg': 'Provided description doesn\'t match the payment request one'
    },
    'insufficient_fee': {
        'code': 'OUT_OF_RANGE',
        'msg': 'Fees are insufficient'
    },
    'insufficient_funds': {
        'code': 'FAILED_PRECONDITION',
        'msg': 'Funds are insufficient'
    },
    'invalid': {
        'code': 'INVALID_ARGUMENT',
        'msg': "Invalid parameter '%PARAM%'"
    },
    'invoice_expired': {
        'code': 'OUT_OF_RANGE',
        'msg': 'Invoice expired'
    },
    'invoice_not_found': {
        'code': 'NOT_FOUND',
        'msg': 'Invoice not found'
    },
    'missing_parameter': {
        'code': 'INVALID_ARGUMENT',
        'msg': "Parameter '%PARAM%' is necessary"
    },
    'node_error': {
        'code': 'UNAVAILABLE',
        'msg': '[node error] %PARAM%'
    },
    'node_locked': {
        'code': 'UNAVAILABLE',
        'msg': 'Node locked, unlock it by calling UnlockNode'
    },
    'openchannel_failed': {
        'code': 'CANCELLED',
        'msg': 'Failed to open channel'
    },
    'payinvoice_failed': {
        'code': 'CANCELLED',
        'msg': 'Invoice payment has failed'
    },
    'payonchain_failed': {
        'code': 'CANCELLED',
        'msg': 'On-chain payment has failed'
    },
    'route_not_found': {
        'code': 'NOT_FOUND',
        'msg': 'Can\'t find route to node'
    },
    'unimplemented_method': {
        'code':
        'UNIMPLEMENTED',
        'msg': ("The gRPC method '%PARAM%' is not supported for this "
                'implementation')
    },
    'unimplemented_parameter': {
        'code':
        'UNIMPLEMENTED',
        'msg': ("The gRPC parameter '%PARAM%' is not supported for this "
                'implementation')
    },
    'unimplemented_param_value': {
        'code':
        'UNIMPLEMENTED',
        'msg': ("Field '%PARAM%' doesn't support value '%PARAM%' on this "
                "implementation")
    },
    'unsettable': {
        'code': 'INVALID_ARGUMENT',
        'msg': "Parameter '%PARAM%' unsettable"
    },
    'value_error': {
        'code': 'INVALID_ARGUMENT',
        'msg': "Value '%PARAM%' exceeds maximum precision"
    },
    'value_too_low': {
        'code': 'OUT_OF_RANGE',
        'msg': "Value '%PARAM%' is below minimum threshold"
    },
    'value_too_high': {
        'code': 'OUT_OF_RANGE',
        'msg': "Value '%PARAM%' exceeds maximum treshold"
    },
    'wrong_node_password': {
        'code':
        'INVALID_ARGUMENT',
        'msg': ('Stored node password is incorrect, update it by running '
                'boltlight-secure')
    },
    'wrong_password': {
        'code': 'INVALID_ARGUMENT',
        'msg': 'Wrong password'
    },
    'internal_value_error': {
        'code': 'INTERNAL',
        'msg': "Value '%PARAM%' received from node is not a number"
    },
    # Fallback
    'unexpected_error': {
        'code': 'UNKNOWN'
    }
}


class Err():  # pylint: disable=too-few-public-methods
    """Boltlight errors class."""
    def __getattr__(self, name):
        """Dispatch the called error dynamically."""
        def error_dispatcher(context, *params):
            """Abort gRPC call raising a grpc.RpcError to the API caller."""
            if name in ERRORS.keys():
                scode = getattr(StatusCode, ERRORS[name]['code'])
                msg = ''
                if 'msg' in ERRORS[name]:
                    msg = ERRORS[name]['msg']
                if params:
                    for param in params:
                        msg = sub('%PARAM%', str(param), msg, 1)
                if name == 'unexpected_error':
                    msg = params[0]
                    LOGGER.error('Unexpected error: %s', msg)
                LOGGER.error('> %s', msg)
                context.abort(scode, msg)
            else:
                LOGGER.error('Unmapped error key')

        return error_dispatcher

    def report_error(self, context, error, always_abort=True):
        """Call the proper error method or throw an unexpected_error."""
        module = import_module(f'..light_{sett.IMPLEMENTATION}', __name__)
        for msg, act in module.ERRORS.items():
            if msg in error:
                args = [context, act['params']] if 'params' in act \
                    else [context]
                if act['fun'] == 'node_error':
                    args = [context, error]
                getattr(self, act['fun'])(*args)
        if always_abort:
            self.unexpected_error(context, str(error))
