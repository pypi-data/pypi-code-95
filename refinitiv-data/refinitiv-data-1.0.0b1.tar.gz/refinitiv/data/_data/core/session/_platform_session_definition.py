# coding: utf-8

__all__ = ["Definition"]


from ._session_provider import _make_platform_session_provider_by_arguments


class Definition(object):
    """
    Create definition object for platform session.
    When user provides "session-name", then it is checked
    in the config file for matches, if match is found,
    then this session will be taken, otherwise, an exception will be raised

    When user doesn't provide a session name,
    then the default session from the config file is taken

    Parameters
    ----------
        session_name: str
            name of the session in config. For example: 'default-session'
        app_key: str
            application key
        grant: GrantPassword object
            GrantPassword object created based on user's password and username
        signon_control: bool
            signon_control value to take sign on control
        deployed_platform_host: str
            for Deployed platform connection.
            The host contains host name and
            port i.e. 127.0.0.0:15000
        deployed_platform_username: str
            deployed platform username
        dacs_position: str
            socket host position by name
        dacs_application_id: str
            dacs application id, default value: 256

    Raises
    ----------
    Exception
        If app-key is not found in the config file and in arguments.

    Examples
    --------
    >>> import refinitiv.data as rd
    >>> definition = rd.session.platform.Definition(session_name="custom-session-name")
    >>> platform_session = definition.get_session()
    """

    def __init__(
        self,
        session_name: str = "default-session",
        app_key: str = None,
        grant=None,
        signon_control: bool = None,
        deployed_platform_host: str = None,
        deployed_platform_username: str = None,
        dacs_position: str = None,
        dacs_application_id: str = None,
    ) -> None:
        if not isinstance(session_name, str):
            raise ValueError("Invalid session name type, please provide string.")

        self._create_session = _make_platform_session_provider_by_arguments(
            session_name=session_name,
            app_key=app_key,
            signon_control=signon_control,
            deployed_platform_host=deployed_platform_host,
            deployed_platform_username=deployed_platform_username,
            dacs_position=dacs_position,
            dacs_application_id=dacs_application_id,
            grant=grant,
        )

    def get_session(self):
        session = self._create_session()
        return session
