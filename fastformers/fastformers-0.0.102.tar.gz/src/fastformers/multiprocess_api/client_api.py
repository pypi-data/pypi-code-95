from typing import Any, Optional, Union, Tuple, List, Dict

import time
import select
import socket
import io
import threading
import operator
import uuid
import pickle as pkl
import torch

from ..utils import logger
from .socket_connection import SocketConnection
from .model_deployment_config import ModelDeploymentConfig
from .configs import Config


class ClientSocket(SocketConnection):
    __slots__ = ('message_id', 'batch_ind')

    def __init__(self, connection: socket.socket, message_size: int):
        super().__init__(connection, message_size)
        self.message_id: Optional[bytes] = None
        self.batch_ind: int = -1

    def request_server(self):
        self.connection.send(Config.request_signal)

    def cancel_request(self):
        self.connection.send(Config.request_cancelled)

    def send_inputs(self, data: Any, batch_ind: int):
        self.message_id = uuid.uuid4().bytes[:Config.message_id_len]
        buffer = io.BytesIO()
        torch.save(data, buffer)
        self.send_data(self.message_id + buffer.getvalue())
        self.batch_ind = batch_ind

    def receive_outputs(self) -> Optional[Tuple[int, Any]]:
        data = self.read_buffer()
        response_message_id = data[:Config.message_id_len]
        if response_message_id != self.message_id:
            logger.warning(f'Skipping response with wrong message id')
            return None
        data = data[Config.message_id_len:]
        self.message_id = None
        if data.startswith(Config.error_prefix):
            raise ConnectionError(data[len(Config.error_prefix):].decode('utf-8'))
        return self.batch_ind, pkl.loads(data)


class ClientAPI:
    client_sockets: Dict[bytes, Dict[str, List[ClientSocket]]] = {}

    def __init__(self, model: str, model_config: ModelDeploymentConfig):
        self.model = model
        self.num_models = len(model_config.allocations)
        self.port = model_config.port
        self.max_batch_size = model_config.max_batch_size

    @staticmethod
    def create_sockets(
            model: str, num_models: int, port: int, attempts: int, wait_time: float) -> List[ClientSocket]:
        logger.debug('Connecting to model workers')
        model_sockets: List[ClientSocket] = []
        for worker_ind in range(num_models):
            client_socket = socket.socket()
            for _ in range(attempts):
                try:
                    client_socket.connect((Config.host, port + worker_ind))
                    logger.debug(f'{model} model worker {worker_ind} connected')
                    model_sockets.append(
                        ClientSocket(connection=client_socket, message_size=Config.client_message_size))
                    break
                except ConnectionRefusedError:
                    time.sleep(wait_time)
        return model_sockets

    @staticmethod
    def split_inputs_to_batches(inputs: Dict, max_batch_size: int) -> List[Dict]:
        batch_size = next(iter(inputs.values())).shape[0]
        if max_batch_size is None or batch_size <= max_batch_size:
            return [inputs]
        return [
            {key: value[ind: ind + max_batch_size] for key, value in inputs.items()}
            for ind in range(0, batch_size, max_batch_size)
        ]

    @staticmethod
    def split_batch(inputs: Dict, batch_size: int) -> Dict:
        outputs = {}
        for key, values in inputs.items():
            outputs[key] = values[:batch_size]
            inputs[key] = values[batch_size:]
        return outputs

    @staticmethod
    def concat_lists_or_tensors(items: Union[List[List], List[torch.Tensor]]) -> Union[List, torch.Tensor]:
        return (
            torch.cat(items) if isinstance(items[0], torch.Tensor)
            else [value for sample_values in items for value in sample_values]
        )

    @classmethod
    def stack_outputs(cls, outputs: List) -> Any:
        sample = outputs[0]
        if len(outputs) == 1:
            return sample
        if isinstance(sample, dict):
            return {
                key: cls.concat_lists_or_tensors(list(map(operator.itemgetter(key), outputs))) for key in sample.keys()
            }
        return cls.concat_lists_or_tensors(outputs)

    @staticmethod
    def clear_sockets(socket_list: List[ClientSocket]):
        while True:
            active_sockets: List[ClientSocket] = select.select(socket_list, [], [], 0)[0]
            if not active_sockets:
                break
            for client_socket in active_sockets:
                client_socket.connection.recv(client_socket.message_size)

    def forward(self, **inputs):
        thread_id = threading.get_ident().to_bytes(length=Config.thread_id_len, byteorder='big', signed=False)

        if thread_id not in self.client_sockets:
            self.client_sockets[thread_id] = {}
        if self.model not in self.client_sockets[thread_id]:
            self.client_sockets[thread_id][self.model] = self.create_sockets(
                self.model, self.num_models, self.port, attempts=120, wait_time=10)

        client_sockets = self.client_sockets[thread_id][self.model]

        self.clear_sockets(client_sockets)

        total_batch_size = next(iter(inputs.values())).shape[0]

        outputs: List = []
        received_counter = 0
        cur_ind = 0

        for client_socket in client_sockets:
            client_socket.request_server()

        while total_batch_size or received_counter < len(outputs):
            ready_sockets: List[ClientSocket] = select.select(
                client_sockets if total_batch_size else
                [client_socket for client_socket in client_sockets if client_socket.message_id is not None],
                [], [], None
            )[0]
            input_sockets: List[ClientSocket] = []
            output_sockets: List[ClientSocket] = []
            for client_socket in ready_sockets:
                (input_sockets if client_socket.message_id is None else output_sockets).append(client_socket)

            added_connections = min(len(input_sockets), total_batch_size)
            outputs.extend(None for _ in range(added_connections))

            if added_connections:
                preferred_batch_size = (total_batch_size - 1) // added_connections + 1
                if self.max_batch_size is not None and preferred_batch_size > self.max_batch_size:
                    total_batch_size -= self.max_batch_size * added_connections
                    leftover_num = 0
                    batch_size = self.max_batch_size
                else:
                    leftover_num = total_batch_size % added_connections
                    total_batch_size = 0
                    batch_size = preferred_batch_size
                    if leftover_num:
                        batch_size -= 1
            else:
                batch_size = leftover_num = 0

            selected_sockets: List[ClientSocket] = input_sockets[:added_connections]

            self.clear_sockets(input_sockets)

            for ind, client_socket in enumerate(selected_sockets):
                sample_batch_size = batch_size
                if ind < leftover_num:
                    sample_batch_size += 1
                client_socket.send_inputs(self.split_batch(inputs, sample_batch_size), cur_ind + ind)

            cur_ind += added_connections

            if added_connections and not total_batch_size:
                for client_socket in client_sockets:
                    if client_socket.message_id is None:
                        client_socket.cancel_request()

            for client_socket in output_sockets:
                socket_outputs = client_socket.receive_outputs()
                if socket_outputs is None:
                    continue
                batch_ind, data = socket_outputs
                outputs[batch_ind] = data
                received_counter += 1
                if total_batch_size:
                    client_socket.request_server()

        return self.stack_outputs(outputs)

    def __call__(self, **kwargs):
        return self.forward(**kwargs)

    def close(self):
        for client_sockets in self.client_sockets.values():
            for sockets in client_sockets.values():
                for client_socket in sockets:
                    client_socket.close()
