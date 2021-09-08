from typing import Any, Optional, Union, Type, List, Dict

import torch


class ModelDeploymentConfig:
    __slots__ = ('model_class', 'path', 'port', 'allocations', 'model_kwargs', 'use_torchscript', 'max_batch_size')

    def __init__(
            self, model_class: Type[torch.nn.Module], path: str, port: int,
            allocations: Union[List[int], str], model_kwargs: Optional[Dict[str, Any]] = None,
            use_torchscript: bool = True, max_batch_size: Optional[int] = None
    ):
        self.model_class = model_class
        self.path = path
        self.model_kwargs: Dict[str, Any] = {} if model_kwargs is None else model_kwargs
        self.port = port
        self.allocations: List[int] = list(
            map(int, allocations.split(','))) if type(allocations) == str else allocations
        self.use_torchscript = use_torchscript
        self.max_batch_size = max_batch_size
