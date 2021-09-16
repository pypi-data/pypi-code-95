import logging
from typing import List, Dict, Type, Union, Tuple, Set, TYPE_CHECKING
from ..worker_base import WorkerBase, Progress
from ..cache_backend import SetsMetaBase
from multiprocessing.context import ProcessError

if TYPE_CHECKING:
    from .manager import Manager

log = logging.getLogger(__name__)


class ManagerWorkersBase:
    parent: "Manager" = None
    worker_class: Type[WorkerBase] = None

    def __init__(self, manager: "Manager", worker_class: Type[WorkerBase]):
        self.parent = manager
        self.workers: List[WorkerBase] = []
        self.finished_workers: List[WorkerBase] = []
        self.failed_workers: List[WorkerBase] = []
        self.worker_class = worker_class

        # Setup caching backend on worker class

        self.worker_class.cache_backend = self.parent.cache_backend
        self.worker_class.cache_backend_params = self.parent.cache_backend_params

    def is_done(self):
        raise NotImplementedError

    def _get_process_status(self, worker):
        if worker.is_alive():
            return "running"
        else:
            if worker.exitcode is None:
                return "initial"
            elif worker.exitcode == 0 and worker not in self.finished_workers:
                return "exited"
            elif worker.exitcode != 0 and worker not in self.failed_workers:
                return "failed"
            elif worker in self.finished_workers + self.failed_workers:
                return "closed"
        raise ValueError(
            "Could not determine process status. Something went wrong",
            worker.exitcode,
            worker,
        )

    def _init_workers(
        self, parameters: List[Dict], names: List[str] = None, tags: List = None
    ):
        if not names:
            names = [hash(str(p)) for p in parameters]
        for name, params in zip(names, parameters):
            name = f"{self.worker_class.__name__}-{';'.join(tags or [])}-{name}"
            w: WorkerBase = self.worker_class(name=name, **params)
            log.debug(f"INIT WORKER {w.name}")
            w.tags = tags
            w.params = params
            self.workers.append(w)

    def _finish_workers(self, tag: str = None) -> bool:
        did_any_workers_finish = False
        for fin_worker in self._get_workers("exited", tag=tag):
            did_any_workers_finish = True
            fin_worker.join()
            fin_worker.timer.__exit__(None, None, None)
            self.parent._release_loading_block_label(fin_worker.id)
            fin_worker.progress = Progress.COMPLETE
            self.finished_workers.append(fin_worker)

            log.debug(f"Exit worker '{fin_worker.name}'")
        # Exit failed worker
        for fail_worker in self._get_workers("failed", tag=tag):
            did_any_workers_finish = True
            fail_worker.join()
            fail_worker.timer.__exit__(None, None, None)
            # release any nodeset blocks
            self.parent.blocked_labels.pop(fail_worker.id, None)
            self.failed_workers.append(fail_worker)
            self.parent._release_loading_block_label(fail_worker.id)
            fail_worker.progress = Progress.COMPLETE
            log.error(
                f"Exit failed worker '{fail_worker.name}' \n other workers currently running are {self._get_workers('running')}"
            )
            raise ProcessError(f"'{fail_worker.name}' failed")
        return did_any_workers_finish

    def _get_workers(
        self,
        status: Union[str, List, Tuple, Set] = None,
        progress: Union[str, List, Tuple, Set] = None,
        tag=None,
    ):
        return [
            w
            for w in self.workers
            if (tag is None or tag in w.tags)
            and (
                status is None
                or (isinstance(status, str) and self._get_process_status(w) == status)
                or (
                    isinstance(status, (list, set, tuple))
                    and self._get_process_status(w) in status
                )
            )
            and (
                progress is None
                or (isinstance(progress, str) and w.progress == progress)
                or (isinstance(progress, (list, set, tuple)) and w.progress in progress)
            )
        ]
