from .exc import StateEventImplementationError
from abc import ABC, abstractmethod


class EventInterface(ABC):

    def __repr__(self):
        raise NotImplementedError


class Event(EventInterface):

    def __init__(self, *args, **kwargs):
        self.__name = self.__class__.__name__

    def __repr__(self):
        return f'({self.__name}, {id(self)})'


class StateEvent(Event):

    states = None

    @staticmethod
    def validate_states(states):
        if states is None:
            raise StateEventImplementationError
        elif type(states) is tuple:
            if len(states) != 2:
                raise StateEventImplementationError
            name, state = states
            if type(name) is not str:
                raise StateEventImplementationError
            if state is not None and type(state) is not str:
                raise StateEventImplementationError
        elif type(states) is dict:
            if len(states) > 1:
                raise StateEventImplementationError
            func, substates = next(iter(states.items()))
            if func not in {'or', 'and', 'not'}:
                raise StateEventImplementationError
            else:
                if func in {'or', 'and'}:
                    if type(substates) is not list:
                        raise StateEventImplementationError
                    elif len(substates) < 2:
                        raise StateEventImplementationError
                StateEvent.validate_states(substates)
        elif type(states) is list:
            for state in states:
                StateEvent.validate_states(state)
        else:
            raise StateEventImplementationError

    @classmethod
    def is_valid(cls):
        cls.validate_states(cls.states)
        return True


class EpsilonEvent(Event):

    def __init__(self, event: Event, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event = event

    def __getattr__(self, attr):
        return getattr(self.event, attr)

