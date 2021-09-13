"""
Simple scheduler to call task repeatedly.
"""
import bisect


class Scheduler:
    """Simple scheduler that will call tasks to
    update the state of a simulation.
    """

    def __init__(self, clock_ini, state_ini, params=None):
        """Initialize an empty simulator.

        Args:
            clock_ini (Union[int, datetime]): initial time in the simulation.
            state_ini (any): current state of the model at clock_ini
                             (will be modified by run method)
            params (any): Set of parameters to pass to each task that will remain
                          constant throughout the simulation.
        """
        self._queue = []  # internal queue of tasks that will be called
        # ordered by time and priority
        self._state = state_ini  # state that will be passed to processes
        self._params = params

        self._current_clock = clock_ini

    def current_clock(self):
        """Accessor to internal current clock."""
        return self._current_clock

    def state(self):
        """Accessor to internal state."""
        return self._state

    def set_state(self, state):
        """Set current state to work on."""
        self._state = state

    def params(self):
        """Accessor to internal params."""
        return self._params

    def set_params(self, params):
        """Set current params to work on."""
        self._params = params

    @staticmethod
    def _fetch_task(tasks, task_cls):
        """Find index of task in list

        Raises:
            UserWarning if none or multiple tasks found.

        Args:
            tasks (list): list of (clock, task)
            task_cls (Task): task class

        Returns:
            (int): index of task in list
        """
        indices = [i for i, (t0, task) in enumerate(tasks) if isinstance(task, task_cls)]
        if len(indices) == 0:
            raise UserWarning(f"No task of type {task_cls} found in queue")

        if len(indices) > 1:
            raise UserWarning(f"More than one task of type {task_cls} found in queue")

        return indices[0]

    def add_task(self, task, t0=None, after=None, before=None):
        """Add a new task in the scheduler.

        Notes: order of tasks
            Tasks are called according to clock first then by priority
            Priority is implicitely defined by the order in which they have been
            added to the scheduler.

        Args:
            task (Task): Any object with an update method
            t0 (Union[int, datetime]): first time this task will be called.
                           If None (default), task will be called at start time.
            after (Task): task will be inserted at the same initial time than this
                          one but with a lower prority (executed after).
            before (Task): task will be inserted at the same initial time than this
                          one but with a higher prority (exectued before).

        Returns:
            None
        """
        # compute list of tasks sorted by priority for reorganising pids
        # after editing queue
        tasks = [(t0, tsk) for t0, priority, tsk in sorted(self._queue, key=lambda tup: tup[1])]

        if after is not None:
            ref_ind = self._fetch_task(tasks, after)
            ref_t0, ref_task = tasks[ref_ind]
            tasks.insert(ref_ind + 1, (ref_t0, task))

        elif before is not None:
            ref_ind = self._fetch_task(tasks, before)
            ref_t0, ref_task = tasks[ref_ind]
            tasks.insert(ref_ind, (ref_t0, task))

        else:
            if t0 is None:
                t0 = self._current_clock
            elif t0 < self._current_clock:
                raise UserWarning("You cannot start a task before actual simulation time")

            tasks.append((t0, task))

        # reconstruct queue
        self._queue = []
        for priority, (t0, tsk) in enumerate(tasks):
            bisect.insort(self._queue, (t0, priority, tsk))

    def run(self, clock_end):
        """Run simulation until end of time.

        Args:
            clock_end (Union[int, datetime]): final time (inclusive) of simulation

        Returns:
            (tuple):
             - (Union[int, datetime]): actual end time of simulation (particularly
                                       relevant if simulation ends due to no more
                                       tasks to perform).
             - (Any): state of simulation at end time
        """
        if clock_end < self._current_clock:
            raise UserWarning("End time before simulation current time")

        while self._queue and self._queue[0][0] <= clock_end:
            # retrieve most pressing process to evaluate
            self._current_clock, priority, task = self._queue.pop(0)

            # update world
            next_eval = task.update(self._current_clock, self._state, self._params)

            # insert back task for next evaluation
            if next_eval is not None:
                bisect.insort(self._queue, (next_eval, priority, task))

        return self._current_clock, self._state
