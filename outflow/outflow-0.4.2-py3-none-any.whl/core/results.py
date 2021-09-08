# -*- coding: utf-8 -*-
class Results:
    """Expose a read-only dict for results"""

    def __init__(self):
        # store the results
        self._results = {}

    def __getitem__(self, task_id):
        return self._results[task_id]

    def _set(self, task_id, value):
        """A private method to set results dict values

        Args:
            task_id (str): A task id
            value (Any): a reference to the task result
        """
        self._results[task_id] = value

    def __contains__(self, task_id):
        return task_id in self._results

    def resolve(self, task_id):
        return self._results[task_id]

    def get_item_reference(self, task_id, result_key):
        return self._results[task_id][result_key]
