from logging import Logger
from typing import Tuple, Mapping, Text, Any

from geyser import Geyser, Task
from geyser.utility import reflect, inject_logger
from torch.nn import Module
from torch.optim import Optimizer
from torch.utils.data import DataLoader, Dataset


@Geyser.task(provides=('loader',), requires=('dataset_params', 'loader_params'))
class DataLoaderProvider(Task):
    def execute(
            self, *args, logger: Logger, dataset_params: Mapping[Text, Any], loader_params: Mapping[Text, Any], **kwargs
    ) -> Tuple[DataLoader]:
        dataset_ref = dataset_params.pop('reference')
        dataset_type = reflect(dataset_ref)
        if issubclass(dataset_type, Dataset):
            dataset = inject_logger(dataset_type, **dataset_params)
            logger.debug(f'Finish building dataset "{dataset_ref}"')
            return inject_logger(DataLoader, dataset=dataset, **loader_params),
        else:
            raise ValueError(f'Reference "{dataset_ref}" is NOT a subclass of {Dataset.__module__}.{Dataset.__name__}')


@Geyser.task(provides=('model',), requires=('model_params',))
class ModelProvider(Task):
    def execute(
            self, *args, logger: Logger, model_params: Mapping[Text, Any], **kwargs
    ) -> Tuple[Module]:
        model_ref = model_params.pop('reference')
        model_type = reflect(model_ref)
        if issubclass(model_type, Module):
            model = inject_logger(model_type, **model_params)
            logger.debug(f'Finish building module "{model_ref}"')
            return model,
        else:
            raise ValueError(f'Reference "{model_ref}" is NOT a subclass of {Module.__module__}.{Module.__name__}')


@Geyser.task(provides=('loss',), requires=('loss_params',))
class LossProvider(ModelProvider):
    def execute(
            self, *args, logger: Logger, loss_params: Mapping[Text, Any], **kwargs
    ) -> Tuple[Module]:
        return super(LossProvider, self).execute(*args, logger=logger, model_params=loss_params, **kwargs)


@Geyser.task(provides=('optimizer',), requires=('optimizer_params', 'model'))
class OptimizerProvider(Task):
    def execute(
            self, *args, logger: Logger, optimizer_params: Mapping[Text, Any], model: Module, **kwargs
    ) -> Tuple[Optimizer]:
        optim_ref = optimizer_params.pop('reference')
        optim_type = reflect(optim_ref)
        if issubclass(optim_type, Optimizer):
            optimizer = inject_logger(optim_type, **optimizer_params)
            logger.debug(f'Finish building optimizer "{optim_ref}"')
            return optimizer
        else:
            raise ValueError(
                f'Reference "{optim_ref}" is NOT a subclass of {Optimizer.__module__}.{Optimizer.__name__}')
