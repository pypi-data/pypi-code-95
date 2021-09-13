"""
Set of classes to be executed repeatedly
"""


class Task:
    """Base class for all task that will change the state of a simulation.
    """

    def update(self, clock, state, params):
        """Update the state of the model.

        Notes: state is modified in place.

        Args:
            clock (Union[int, datetime]): current 'time'
            state (any): current state of the model
            params (Params): extra parameters, i.e. values that are not modified
                             throughout call to differend tasks

        Returns:
            (Union[int, datetime, None]): next time this task must be performed.
                                 if None, this task won't be evaluated anymore.
        """
        return None


class TaskRecord(Task):
    """Simple task to store some information on the run.
    """

    def __init__(self):
        super().__init__()

        self._mem = []

    def last_entry(self):
        """Return last append entry

        Returns:
            (any)
        """
        if len(self._mem) > 0:
            return self._mem[-1]
        else:
            return None

    def append(self, data):
        """Append some data in memory.

        Args:
            data (any): whatever

        Returns:
            None
        """
        self._mem.append(data)

    def retrieve(self):
        """Retrieve the list of stored data.

        Returns:
            (list)
        """
        return self._mem
