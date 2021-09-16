import logging
import graphio
from typing import List, Dict, Type, Set, TYPE_CHECKING
from ..worker_base import WorkerBase
from .manager_workers_base import ManagerWorkersBase


if TYPE_CHECKING:
    from .manager import Manager

log = logging.getLogger(__name__)


class ManagerWorkersSourcing(ManagerWorkersBase):
    def __init__(self, manager: "Manager", worker_class: Type[WorkerBase]):
        super(type(self), self).__init__(manager, worker_class)
        # create workers distribute task parameters per worker
        log.debug(f"self.parent.worker_parameters: {self.parent.worker_parameters}")
        self._init_workers(parameters=self.parent.worker_parameters)
        self.worker_count_total = len(self.workers)

    def is_done(self):
        # Mom, Are We There Yet?
        if len(self.workers) == len(self._get_workers(status="closed")):
            return True
        else:
            return False

    def manage(self):
        available_cores = self.parent.strategy.amount_sourcing_cores()
        # Collect all running sourcing workers
        waiting_workers = self._get_workers(status="initial")
        new_worker_started = False
        # Start next worker
        if (
            len(self._get_workers(status="running")) < available_cores
            and len(waiting_workers) > 0
        ):
            new_worker_started = True
            next_worker = waiting_workers.pop(0)
            log.debug(f"CALL START ON SOURCING {next_worker} - {next_worker.params}")
            next_worker.start()
            next_worker.timer.__enter__()

        workers_did_finished = self._finish_workers()
        if workers_did_finished or new_worker_started:
            log.debug(
                f"SOURCING: {len(self.finished_workers) + len(self.failed_workers)} Workers finished / {len(self._get_workers('running'))} Workers running / {len(self._get_workers('initial'))} Workers waiting / {len(self.failed_workers)} Workers failed / {available_cores} Max sourcing workers running simultaneously"
            )
