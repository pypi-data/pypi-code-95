from typing import Optional

from ..core.session import Session
from ..core.session._session_definition import Definition
from ..core.session import get_default, set_default

from ..config_functions import load_config, get_config


def open_session(
    app_key: Optional[str] = None,
    name: Optional[str] = None,
    config_name: Optional[str] = None,
) -> Session:
    """
    Opens session.
    Without params opens default session from default config

    Parameters
    ----------
        app_key: str,
            if provided overrides app_key
        name: str,
            if provided opens named session from config,
            It should be in the following format: 'session_type.session_name'
        config_name: str,
            if provided overrides config and set it as default

    Returns
    -------
    Session
    """
    # Because it's a path in configuration profile, not a session name,
    # but we can't change argument name, because it's a public API
    config_path = name
    del name

    _definition = Definition
    _load_config = load_config
    _config_object = get_config()
    _set_default = set_default
    return _open_session(**locals())


def close_session() -> None:
    """
    Close default session

    Returns
    -------
    None
    """
    _get_default = get_default
    _close_session(**locals())


def _open_session(**kwargs) -> Session:
    config_name_for_err = "default"
    app_key = kwargs.pop("app_key")
    config_name = kwargs.pop("config_name")

    _definition = kwargs.pop("_definition")
    _load_config = kwargs.pop("_load_config")
    _config_object = kwargs.pop("_config_object")
    _set_default = kwargs.pop("_set_default")

    if config_name:
        _load_config(config_name)
        config_name_for_err = "config_name"

    name = kwargs.pop("config_path") or _config_object.get_param("sessions.default")

    try:
        _config_object.get_param(f"sessions.{name}")
    except Exception:
        raise NameError(
            f"Cannot open session {name}\n"
            f"This session is not defined in the {config_name_for_err} configuration file"
        )

    if app_key:
        _config_object.set_param(param=f"sessions.{name}.app-key", value=app_key)

    session = _definition(session_name=name).get_session()

    _set_default(session)
    session.open()

    return session


def _close_session(**kwargs) -> None:
    _get_default = kwargs.pop("_get_default")

    try:
        default_session = _get_default()
    except AttributeError:
        print("Nо default session to close")
    else:
        if default_session.is_open:
            default_session.info("Closing session")
            default_session.close()
        if default_session.is_closed:
            default_session.info("Session is closed")
