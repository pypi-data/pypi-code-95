from typing import Dict


class StatesMixin(object):

    _states: Dict[str, list]

    @property
    def states(self) -> Dict[str, list]:
        """
        Return a dictionary mapping names of variables to their possible states.
        """
        return self._states
