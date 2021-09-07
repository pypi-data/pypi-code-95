# -*- coding: utf-8 -*-
from typing import Callable

import bottle
from pip_services3_commons.errors.UnauthorizedException import UnauthorizedException

from pip_services3_rpc.services.HttpResponseSender import HttpResponseSender


class OwnerAuthorizer:

    def owner(self, id_param: str = 'user_id') -> Callable:
        def inner():
            if bottle.request.user is None:
                HttpResponseSender.send_error(UnauthorizedException(
                    None,
                    'NOT_SIGNED',
                    'User must be signed in to perform this operation'
                ).with_status(401))
            else:
                user_id = dict(bottle.request.query.decode()).get(id_param)
                if bottle.request.user_id != user_id:
                    HttpResponseSender.send_error(UnauthorizedException(
                        None,
                        'FORBIDDEN',
                        'Only data owner can perform this operation'
                    ).with_status(403))

        return inner

    def owner_or_admin(self, id_param: str = 'user_id'):
        def inner():
            if bottle.request.user is None:
                HttpResponseSender.send_error(UnauthorizedException(
                    None,
                    'NOT_SIGNED',
                    'User must be signed in to perform this operation'
                ).with_status(401))
            else:
                user_id = dict(bottle.request.query.decode()).get(id_param)
                if hasattr(bottle.request, 'user'):
                    roles = bottle.request.user.roles
                else:
                    roles = None
                admin = 'admin' in roles
                if bottle.request.user_id != user_id and not admin:
                    HttpResponseSender.send_error(UnauthorizedException(
                        None,
                        'FORBIDDEN',
                        'Only data owner can perform this operation'
                    ).with_status(403))

        return inner
