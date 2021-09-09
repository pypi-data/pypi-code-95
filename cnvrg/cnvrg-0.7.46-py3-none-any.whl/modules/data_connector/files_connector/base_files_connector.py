from cnvrg.modules.data_connector.base_connector import BaseConnector

class BaseFileConnector(BaseConnector):
    def __init__(self, data_connector):
        super(BaseFileConnector, self).__init__(data_connector)
        self._files_callback = lambda x: x

    def __len__(self):
        raise Exception("Not implemented")

    def __getitem__(self, item):
        raise Exception("Not implemented")

    @property
    def working_dir(self):
        raise Exception("Not implemented")


    def torch_ds(self, callback=None):
        from torch.utils.data.dataset import Dataset as TorchDataset
        class TorchDs(TorchDataset):
            def __init__(self, dc):
                self.__dc = dc
            def __getitem__(self, item):
                o = self.__dc[item]
                if callback:
                    return callback(o)
                return o
            def __len__(self):
                return len(self.__dc)
        return TorchDs(self)

    def data_loader(self, **kwargs):
        # Arguments:
        #         #         dataset (Dataset): dataset from which to load the data.
        #         #         batch_size (int, optional): how many samples per batch to load
        #         #             (default: ``1``).
        #         #         shuffle (bool, optional): set to ``True`` to have the data reshuffled
        #         #             at every epoch (default: ``False``).
        #         #         sampler (Sampler, optional): defines the strategy to draw samples from
        #         #             the dataset. If specified, ``shuffle`` must be False.
        #         #         batch_sampler (Sampler, optional): like sampler, but returns a batch of
        #         #             indices at a time. Mutually exclusive with :attr:`batch_size`,
        #         #             :attr:`shuffle`, :attr:`sampler`, and :attr:`drop_last`.
        #         #         num_workers (int, optional): how many subprocesses to use for data
        #         #             loading. 0 means that the data will be loaded in the main process.
        #         #             (default: ``0``)
        #         #         collate_fn (callable, optional): merges a list of samples to form a mini-batch.
        #         #         pin_memory (bool, optional): If ``True``, the data loader will copy tensors
        #         #             into CUDA pinned memory before returning them.  If your data elements
        #         #             are a custom type, or your ``collate_fn`` returns a batch that is a custom type
        #         #             see the example below.
        #         #         drop_last (bool, optional): set to ``True`` to drop the last incomplete batch,
        #         #             if the dataset size is not divisible by the batch size. If ``False`` and
        #         #             the size of dataset is not divisible by the batch size, then the last batch
        #         #             will be smaller. (default: ``False``)
        #         #         timeout (numeric, optional): if positive, the timeout value for collecting a batch
        #         #             from workers. Should always be non-negative. (default: ``0``)
        #         #         worker_init_fn (callable, optional): If not ``None``, this will be called on each
        #         #             worker subprocess with the worker id (an int in ``[0, num_workers - 1]``) as
        #         #             input, after seeding and before data loading. (default: ``None``)
        #         #         sort_fn (list) -> list: a callback which get a list of files to download and should return a sorted list of
        #         #           files, (default lambda x: x)
        from torch.utils import data
        class DataLoader(data.DataLoader):
            def __init__(self, dc, **kwargs):
                callback = kwargs.get("callback")
                if 'callback' in kwargs: del kwargs["callback"]
                super(DataLoader, self).__init__(dc.torch_ds(callback=callback), **kwargs)
        self._files_callback = kwargs.get("sort_fn") or (lambda x: x)
        if 'sort_fn' in kwargs: del kwargs["sort_fn"]
        len(self) ## trigger first fetching.
        return DataLoader(self, **kwargs)