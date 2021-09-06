# -*- coding: utf-8 -*-
from typing import List, Callable

import bottle
from pip_services3_commons.errors.UnauthorizedException import UnauthorizedException

from pip_services3_rpc.services.HttpResponseSender import HttpResponseSender


class RoleAuthorizer:
    def user_in_roles(self, roles: List[str]) -> Callable:
        def inner():
            user = bottle.request.user
            if user is None:
                HttpResponseSender.send_error(UnauthorizedException(
                    None,
                    'NOT_SIGNED',
                    'User must be signed in to perform this operation'
                ).with_status(401))
            else:
                authorized = False
                for role in roles:
                    authorized = authorized or role in user.roles

                if not authorized:
                    HttpResponseSender.send_error(UnauthorizedException(
                        None,
                        'NOT_IN_ROLE',
                        'User must be ' +
                        ' or '.join(roles) + ' to perform this operation'
                    ).with_details('roles', roles).with_status(403))

        return inner

    def user_in_role(self, role: str) -> Callable:
        return self.user_in_roles([role])

    def admin(self) -> Callable:
        return self.user_in_role('admin')
