# coding: utf-8

__all__ = ["Definition"]

from ._session_provider import get_session_type, _make_session_provider_by_arguments
from ._session_type import SessionType
from ... import configure


def _retrieve_config_and_set_type(session_name, session_type):
    if session_type == SessionType.PLATFORM:
        session_config = configure.get(
            configure.keys.platform_session(session_name), {}
        )
    elif session_type == SessionType.DESKTOP:
        session_config = configure.get(configure.keys.desktop_session(session_name), {})
    else:
        raise TypeError(
            f"Invalid session type: {session_type}, please set 'desktop' or 'platform'."
        )

    if not session_config:
        raise ValueError(
            f"Can't get config by name: {session_name}. Please check config name"
        )

    return session_config


def _get_session_type_and_name(config_path: str):
    try:
        config_path = config_path or configure.get("sessions.default")
        session_type, session_name = config_path.split(".")

    except ValueError:
        raise ValueError(
            "Please check your 'session_name'. It should be in the following way: 'session_type.session_name'"
        )

    except AttributeError:
        raise AttributeError("Invalid type, please provide string")

    return session_name, get_session_type(session_type)


class Definition(object):
    """
    Create definition object for desktop or platform session.
    When user provides "session-name", then it is checked
    in the config file for matches, if match is found,
    then this session will be taken, otherwise, an exception will be raised

    When user doesn't provide a session name,
    then the default session from the config file
    is taken by using "sessions.default" parameter.

    Parameters
    ----------
        session_name: str
            name of the session in config. For example: 'platform.default-session'

    Raises
    ----------
    Exception
        1. If user provided invalid session type in session name.
            Type should be 'platform' or 'desktop'
        2. If app-key not found in config and arguments.

    Examples
    --------
    >>> import refinitiv.data as rd
    >>> platform_session = rd.session.Definition(session_name="platform.custom-session").get_session()
    """

    def __init__(self, session_name: str = None) -> None:
        self._create_session = _make_session_provider_by_arguments(session_name)

    def get_session(self):
        session = self._create_session()
        return session
