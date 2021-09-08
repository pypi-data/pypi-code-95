# -*- coding: utf-8 -*-
from outflow.core.results import Results as CoreResults

import ray


class RayResults(CoreResults):
    def resolve(self, task_id):
        import ray

        result = self._results[task_id]

        if result:
            if isinstance(result, ray._raylet.ObjectRef):
                result = ray.get(result)

            for key, output in result.items():
                if isinstance(output, ray._raylet.ObjectID):
                    result[key] = ray.get(output)
        return result

    def get_item_reference(self, task_id, result_key):
        if isinstance(self._results[task_id], ray._raylet.ObjectRef):
            result = ray.get(self._results[task_id])
            return result[result_key]
        else:
            return super().get_item_reference(task_id, result_key)
