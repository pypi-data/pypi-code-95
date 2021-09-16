# coding: utf-8

__all__ = ["Definition"]


from ._session_provider import _make_desktop_session_provider_by_arguments


class Definition(object):
    """
    Create definition object for desktop session.
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
        token: str
            access token
        dacs_position: str
            socket host position by name
        dacs_application_id: int
            dacs application id, default value: 256
    Raises
    ---------
    Exception
        If app-key is not found in the config file and in arguments.
    Examples
    --------
    >>> from refinitiv.data import session
    >>> definition = session.desktop.Definition(session_name="custom-session-name")
    >>> desktop_session = definition.get_session()
    """

    def __init__(
        self,
        session_name: str = "default-session",
        app_key: str = None,
        token: str = None,
        dacs_position: str = None,
        dacs_application_id: int = None,
    ):
        if not isinstance(session_name, str):
            raise ValueError("Invalid session name type, please provide string.")

        self._create_session = _make_desktop_session_provider_by_arguments(
            session_name=session_name,
            app_key=app_key,
            token=token,
            dacs_position=dacs_position,
            dacs_application_id=dacs_application_id,
        )

    def get_session(self):
        session = self._create_session()
        return session
