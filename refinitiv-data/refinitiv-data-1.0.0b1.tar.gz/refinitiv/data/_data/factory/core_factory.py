# coding: utf8


__all__ = [
    "CoreFactory",
    "open_desktop_session",
    "open_platform_session",
    "create_session",
]

from ..core.session import (
    Session,
    DesktopSession,
    PlatformSession,
    GrantPassword,
    _rd_default_session_manager,
)


class CoreFactory:
    @staticmethod
    def create_session(session_params):
        if isinstance(session_params, Session.Params):
            # check the platform
            if isinstance(session_params, DesktopSession.Params):
                return DesktopSession(
                    app_key=session_params._app_key,
                    on_state=session_params._on_state_cb,
                    on_event=session_params._on_event_cb,
                    token=session_params._dacs_params.authentication_token,
                    deployed_platform_username=session_params._dacs_params.deployed_platform_username,
                    dacs_position=session_params._dacs_params.dacs_position,
                    dacs_application_id=session_params._dacs_params.dacs_application_id,
                )
            elif isinstance(session_params, PlatformSession.Params):
                return PlatformSession(
                    app_key=session_params._app_key,
                    grant=session_params.get_grant(),
                    deployed_platform_host=session_params._deployed_platform_host,
                    # Deployed Platform parameter
                    signon_control=session_params.take_signon_control(),
                    on_state=session_params._on_state_cb,
                    on_event=session_params._on_event_cb,
                    token=session_params._dacs_params.authentication_token,
                    deployed_platform_username=session_params._dacs_params.deployed_platform_username,
                    dacs_position=session_params._dacs_params.dacs_position,
                    dacs_application_id=session_params._dacs_params.dacs_application_id,
                )
        else:
            raise Exception("Wrong session parameter")

    @staticmethod
    def create_desktop_session(
        app_key, on_state=None, on_event=None, session_name=None
    ) -> DesktopSession:
        return DesktopSession(app_key, on_state, on_event, session_name=session_name)

    @staticmethod
    def create_platform_session(
        app_key,
        oauth_grant_type=None,
        deployed_platform_host=None,  # Deployed Platform parameter
        authentication_token=None,  # Deployed Platform parameter
        take_signon_control=True,
        deployed_platform_username=None,
        dacs_position=None,
        dacs_application_id=None,
        on_state=None,
        on_event=None,
    ):
        return PlatformSession(
            app_key=app_key,
            grant=oauth_grant_type,
            deployed_platform_host=deployed_platform_host,
            # Deployed Platform parameter
            authentication_token=authentication_token,  # Deployed Platform parameter
            signon_control=take_signon_control,
            deployed_platform_username=deployed_platform_username,
            dacs_application_id=dacs_application_id,
            dacs_position=dacs_position,
            on_state=on_state,
            on_event=on_event,
        )


def open_desktop_session(app_key):
    from ..core.session import set_default

    session = CoreFactory.create_desktop_session(app_key)
    _rd_default_session_manager.close_default_session()
    set_default(session)
    session.open()
    return session


def open_platform_session(
    app_key,
    # for RDP
    grant=None,
    # for deployed platform
    deployed_platform_host=None,
    deployed_platform_username=None,
):
    from ..core.session import set_default

    session = CoreFactory.create_platform_session(
        app_key,
        #  for RDP
        oauth_grant_type=grant,
        deployed_platform_host=deployed_platform_host,
        deployed_platform_username=deployed_platform_username,
    )
    _rd_default_session_manager.close_default_session()
    set_default(session)
    session.open()
    return session


def create_session(session_name):
    from .. import RDError

    def validate(d, keys):
        not_defined = [k for k in keys if k not in d]
        if not_defined:
            raise RDError(1, f'Configuration does not define "{not_defined}"')

    from .. import configure

    platform_session_config = configure.get(
        configure.keys.platform_session(session_name), None
    )
    desktop_session_config = configure.get(
        configure.keys.desktop_session(session_name), None
    )

    if desktop_session_config and platform_session_config:
        # alert !
        desktop_session_config = None

    elif not desktop_session_config and not platform_session_config:
        raise RDError(
            1, f'Cannot find session configuration with name "{session_name}"'
        )

    session = None

    if platform_session_config:
        config = platform_session_config
        validate(config, ["app_key", "username", "password"])

        session = CoreFactory.create_platform_session(
            app_key=config.get_str("app_key"),
            oauth_grant_type=GrantPassword(
                username=config.get_str("username"),
                password=config.get_str("password"),
                token_scope=config.get("token_scope", ""),
            ),
        )

    elif desktop_session_config:
        config = desktop_session_config
        validate(config, ["app_key"])

        session = CoreFactory.create_desktop_session(
            app_key=config.get_str("app_key"),
            session_name=session_name,
        )

    return session
