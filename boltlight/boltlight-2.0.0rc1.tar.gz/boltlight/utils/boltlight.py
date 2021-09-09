# Boltlight - a LN node wrapper
#
# Copyright (C) 2021 boltlight contributors
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
"""Utils module for boltlight.py."""

from grpc import StatusCode


class RuntimeTerminate:
    """Provide methods to terminate a runtime gRPC call.

    All methods deny API access to the caller and provide information on the
    reason why it happened.
    """
    @staticmethod
    def missing_macaroon(_ignored_request, context):
        """Terminate gRPC call due to missing authentication."""
        context.abort(StatusCode.UNAUTHENTICATED,
                      'Macaroon authentication missing')

    @staticmethod
    def macaroon_error(_ignored_request, context):
        """Terminate gRPC call due to authentication error."""
        context.abort(StatusCode.PERMISSION_DENIED,
                      'Macaroon authentication error')

    @staticmethod
    def already_unlocked(_ignored_request, context):
        """Terminate unlock gRPC call since boltlight is already unlocked."""
        context.abort(StatusCode.FAILED_PRECONDITION,
                      'Boltlight is already unlocked')

    @staticmethod
    def not_runtime(_ignored_request, context):
        """Terminate gRPC call since the called method does not exist."""
        context.abort(StatusCode.UNIMPLEMENTED, 'Not a runtime method')
