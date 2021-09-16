from enum import Enum, unique


@unique
class SessionState(Enum):
    """
    Define the state of the session.

    Closed  : The session is closed and ready to be opened.
    Pending : The session is in a pending state. Upon success,
              the session will move into an open state, otherwise will be closed.
    Open    : The session is opened and ready for use.
    """

    Closed = 1
    Pending = 2
    Open = 3
