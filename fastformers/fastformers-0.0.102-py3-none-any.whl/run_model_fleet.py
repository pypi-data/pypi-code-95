from typing import Any, Type, List, Dict

import multiprocessing
import torch

from .multiprocess_api import ModelServer, ModelDeploymentConfig


def run_server(
        model_class: Type[torch.nn.Module], path: str, model_kwargs: Dict[str, Any], device: str, port: int,
        torchscript: bool, verbose: bool
):
    model = model_class.from_pretrained(path, **model_kwargs).to(device)
    if torchscript:
        model = torch.jit.script(model)
    server = ModelServer(port=port, model=model, verbose=verbose)
    try:
        server.run()
    finally:
        server.close()


def run_worker_server(model_config: ModelDeploymentConfig, worker: int, verbose: bool):
    run_server(
        model_class=model_config.model_class, path=model_config.path, model_kwargs=model_config.model_kwargs,
        device=f'cuda:{model_config.allocations[worker]}', port=model_config.port + worker,
        torchscript=model_config.use_torchscript, verbose=verbose
    )


def run_model_fleet(
        model_deployments: Dict[str, ModelDeploymentConfig], verbose: bool = False
) -> List[multiprocessing.Process]:
    all_processes: List[multiprocessing.Process] = []
    for model_config in model_deployments.values():
        processes = [
            multiprocessing.Process(target=run_worker_server, args=(model_config, worker, verbose))
            for worker in range(len(model_config.allocations))
        ]
        for process in processes:
            process.start()
        all_processes.extend(processes)
    return all_processes
