import json
import time
from typing import Dict, Any

from atlas_engine_client.core.api import FlowNodeInstancesQuery
from atlas_engine_client.core.api import FlowNodeInstanceResponse

from robot.api import logger

from ._retry_helper import retry_on_exception


class ProcessInstanceKeyword:

    def __init__(self, client, **kwargs):
        self._client = client

        self._max_retries = kwargs.get('max_retries', 5)
        self._backoff_factor = kwargs.get('backoff_factor', 2)
        self._delay = kwargs.get('delay', 0.1)

    @retry_on_exception
    def get_processinstance(self, **kwargs) -> FlowNodeInstanceResponse:

        query_dict = {
            'state': 'finished',
            'limit': 1,
            'flow_node_type': 'bpmn:EndEvent',
        }

        query_dict.update(**kwargs)

        current_retry = 0
        current_delay = self._delay

        while True:

            query = FlowNodeInstancesQuery(**query_dict)

            flow_node_instances = self._client.flow_node_instance_get(query)

            if len(flow_node_instances) == 1:
                flow_node_instance = flow_node_instances[0]
            else:
                flow_node_instance = {}

            if flow_node_instance:
                break
            else:
                time.sleep(current_delay)
                current_retry = current_retry + 1
                current_delay = current_delay * self._backoff_factor
                if current_retry > self._max_retries:
                    break
                logger.info(
                    f"Retry count: {current_retry}; delay: {current_delay}")

        return flow_node_instance

    @retry_on_exception
    def get_processinstance_result(self, **kwargs) -> Dict[str, Any]:
        result = self.get_processinstance(**kwargs)

        if result:
            payload = result.tokens[0]['payload']
            if payload is not None:
                try:
                    payload = json.loads(payload)
                except json.decoder.JSONDecodeError:
                    payload = {}
        else:
            payload = {}

        logger.info(f"type(payload) {type(payload)}")

        return payload
