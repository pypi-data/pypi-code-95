# --------------------------------------
# PUBLIC API
# --------------------------------------


def set_default(session) -> None:
    """
    Set default session.
    Parameters
    ----------
    session: Session

    Returns
    -------
    """
    _rd_default_session_manager.set_default_session(session)


def get_default():
    """
    Get default session

    Returns
    -------
    """
    return _rd_default_session_manager.try_get_default_session()


# --------------------------------------
# PRIVATE API
# --------------------------------------


class EikonDefaultSessionManager:
    def __init__(self, session=None) -> None:
        if not isinstance(session, Wrapper):
            session = Wrapper(session)

        self._session_wrapper: Wrapper = session

    def get_default_session(self, app_key=None):
        from ...core.session import DesktopSession

        if self._session_wrapper.get() is None:
            if app_key is None:
                return None
            self._session_wrapper.set(DesktopSession(app_key))

        elif app_key is not None and app_key != self._session_wrapper.get().app_key:
            self._session_wrapper.get().close()
            self._session_wrapper.set(DesktopSession(app_key))

        return self._session_wrapper.get()

    def set_default_session(self, session):
        from ...core.session import Session

        if isinstance(session, Session):
            self._session_wrapper.set(session)

    def close_default_session(self):
        if self._session_wrapper.get() is not None:
            self._session_wrapper.get().close()

    def clear_default_session(self):
        self.close_default_session()
        self._session_wrapper.set(None)

    def has_session(self):
        return not self._session_wrapper.get() is None


class RDDefaultSessionManager:
    def __init__(self, session=None) -> None:
        if not isinstance(session, Wrapper):
            session = Wrapper(session)

        self._session_wrapper: Wrapper = session

    def set_default_session(self, session) -> None:
        """
        Set default session.

        Parameters
        ----------
            session: Session
                session object

        Raises
        ----------
        Exception
            If user provided invalid data type
        """
        from ..session import Session

        if session is None:
            return self.clear_default_session()

        if not isinstance(session, Session):
            raise TypeError("Invalid argument")

        self._session_wrapper.set(session)

    def try_get_default_session(self):
        """
        Returns default session or raise exception if user didn't set default session.

        Raises
        ------
        Exception
            If user didn't set default session

        Returns
        ------
        Session object
        """
        if not self._session_wrapper.get():
            raise AttributeError(
                "No default session created yet. Please create a session first!"
            )
        return self._session_wrapper.get()

    def close_default_session(self):
        if self._session_wrapper.get() is not None:
            self._session_wrapper.get().close()

    def clear_default_session(self):
        self.close_default_session()
        self._session_wrapper.set(None)

    def has_session(self):
        return not self._session_wrapper.get() is None

    def set_session(self, session):
        self._session_wrapper.set(session)


class Wrapper:
    def __init__(self, wrapped=None):
        self._wrapped = wrapped

    def get(self):
        return self._wrapped

    def set(self, value):
        self._wrapped = value


def get_valid_session(session):
    if session is None:
        session = get_default()
    if session is None:
        raise AttributeError("A Session must be started")
    return session


_session_wrapper = Wrapper()
_rd_default_session_manager = RDDefaultSessionManager(_session_wrapper)
_eikon_default_session_manager = EikonDefaultSessionManager(_session_wrapper)
