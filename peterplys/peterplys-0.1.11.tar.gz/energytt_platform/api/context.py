import re
from abc import abstractmethod
from typing import Dict, Optional
from functools import cached_property

from energytt_platform.tokens import TokenEncoder
from energytt_platform.models.auth import InternalToken

from .responses import Unauthorized


class Context(object):
    """
    Context for a single incoming HTTP request.
    """

    TOKEN_HEADER = 'Authorization'
    TOKEN_PATTERN = re.compile(r'^Bearer:\s*(.+)$', re.IGNORECASE)

    def __init__(self, token_encoder: TokenEncoder[InternalToken]):
        """
        :param token_encoder:
        """
        self.token_encoder = token_encoder

    @property
    @abstractmethod
    def headers(self) -> Dict[str, str]:
        """
        Returns request headers.
        """
        raise NotImplementedError

    @cached_property
    def raw_token(self) -> Optional[str]:
        """
        Returns request Bearer token.
        """
        if self.TOKEN_HEADER in self.headers:
            matches = self.TOKEN_PATTERN \
                .findall(self.headers[self.TOKEN_HEADER])

            if matches:
                return matches[0]

    @cached_property
    def token(self) -> Optional[InternalToken]:
        """
        Parses token into an OpaqueToken.
        """
        if self.raw_token is not None:
            try:
                internal_token = self.token_encoder.decode(self.raw_token)
            except self.token_encoder.DecodeError:
                # TODO Raise exception if in debug mode?
                return None

            if internal_token.is_expired:
                # TODO Raise exception if in debug mode?
                return None

            return internal_token

    @property
    def is_authorized(self) -> bool:
        """
        Check whether or not the client provided a valid token.
        """
        return self.token is not None

    def has_scope(self, scope: str) -> bool:
        """
        TODO
        """
        if self.token:
            return scope in self.token.scope
        return False

    def get_token(self, required=True) -> Optional[InternalToken]:
        """
        TODO
        """
        if self.token:
            return self.token
        elif required:
            raise Unauthorized('')  # TODO Error message

    def get_subject(self, required=True) -> Optional[str]:
        """
        TODO
        """
        if self.token:
            return self.token.subject
        elif required:
            raise Unauthorized('')  # TODO Error message
