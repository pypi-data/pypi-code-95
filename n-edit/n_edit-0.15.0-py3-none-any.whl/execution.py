import abc
import asyncio
import collections
import dataclasses
import heapq
import logging
import typing as t

from n_edit import model

log = logging.getLogger(__name__)


class NodeExecutor(abc.ABC):
    @abc.abstractmethod
    async def execute_node(self, node: model.Node, inputs: dict[str, t.Any]) -> None:
        raise NotImplemented


class LocalExecutor(NodeExecutor):
    def __init__(self, context: t.Any) -> None:
        self.context = context

    async def execute_node(self, node: model.Node, inputs: dict[str, t.Any]) -> None:
        return await node.execute(self.context, **inputs)  # type: ignore


class NodeNotRunnable(Exception):
    pass


@dataclasses.dataclass(order=True)
class _TaskDefinition:
    priority: int
    node: model.Node = dataclasses.field(compare=False)
    inputs: dict[str, t.Any] = dataclasses.field(compare=False)


@dataclasses.dataclass
class _EdgeResult:
    use: t.Callable[[], t.Any]


def _const_callable(value: t.Any) -> t.Callable[[], t.Any]:
    return lambda: value


class Run:
    def __init__(
        self,
        graph: model.Graph,
        node_executor: NodeExecutor,
        pending_tasks_limit: t.Optional[int] = 10,
    ) -> None:
        self.graph = graph
        self.node_executor = node_executor
        self.edge_queues: dict[int, collections.deque[t.Any]] = {
            edge_id: collections.deque() for edge_id in self.graph.edges
        }
        self.task_node_id_map: dict[asyncio.Task, int] = {}
        self._static_result_cache: dict[int, t.Any] = {}
        self._executed_nodes: set[int] = set()
        self.pending_tasks: set[asyncio.Task] = set()
        self.pending_tasks_limit = pending_tasks_limit

        self._tasks_to_create: list[_TaskDefinition] = [
            self._create_task_definition(source_node)
            for source_node in self.graph.source_nodes()
        ]
        heapq.heapify(self._tasks_to_create)

    async def run(self) -> None:
        await self._create_pending_tasks()
        while self.pending_tasks:
            log.debug(
                "pending tasks: %s, tasks to create: %s, static results: %s, task node id map: %s",
                len(self.pending_tasks),
                len(self._tasks_to_create),
                len(self._static_result_cache),
                len(self.task_node_id_map),
            )
            done, self.pending_tasks = await asyncio.wait(
                self.pending_tasks, return_when=asyncio.FIRST_COMPLETED
            )
            for task in done:
                self.handle_finished_task(task)
            await self._create_pending_tasks()

    def _is_task_limit_reached(self) -> bool:
        if self.pending_tasks_limit is None:
            return False
        return len(self.pending_tasks) >= self.pending_tasks_limit

    async def _create_pending_tasks(self) -> None:
        while self._tasks_to_create and not self._is_task_limit_reached():
            await self._create_task(heapq.heappop(self._tasks_to_create))

    def _append_results(self, node_id: int, results: t.Any) -> None:
        node = self.graph.nodes[node_id]
        if node.has_iterable_output:
            for single_result in results:
                self._append_single_result_to_edges(node_id, single_result)
        else:
            if self.graph.is_node_static(node_id):
                self._store_static_result_for_edges(node_id, results)
            else:
                self._append_single_result_to_edges(node_id, results)

    def _append_single_result_to_edges(self, node_id: int, result: t.Any) -> None:
        for edge in self.graph.get_outgoing_edges(node_id):
            self.edge_queues[edge.id_].append(result)

    def _store_static_result_for_edges(self, node_id: int, result: t.Any) -> None:
        for edge in self.graph.get_outgoing_edges(node_id):
            self._static_result_cache[edge.id_] = result

    def handle_finished_task(self, task: asyncio.Task) -> None:
        node_id = self.task_node_id_map[task]
        del self.task_node_id_map[task]
        self._append_results(node_id, task.result())
        for node in self.graph.downstream_nodes(node_id):
            while True:
                try:
                    task_definition = self._create_task_definition(node)
                except NodeNotRunnable:
                    break
                heapq.heappush(self._tasks_to_create, task_definition)
                self._executed_nodes.add(node.id_)

    def _create_task_definition(self, node: model.Node) -> _TaskDefinition:
        inputs = self._collect_all_input_values(node.id_)
        priority = self.graph.distance_from_end(node.id_)
        return _TaskDefinition(priority, node, inputs)

    async def _create_task(self, task_definition: _TaskDefinition) -> asyncio.Task:
        name = f"{task_definition.node.type_name}.{task_definition.node.id_}({task_definition.inputs})"
        task = asyncio.create_task(
            self.node_executor.execute_node(
                task_definition.node, task_definition.inputs
            ),
            name=name,
        )
        self.task_node_id_map[task] = task_definition.node.id_
        self.pending_tasks.add(task)
        return task

    def _collect_all_dynamic_edge_inputs(
        self, input_edges: dict[str, model.Edge]
    ) -> dict[str, _EdgeResult]:
        return {
            slot_name: _EdgeResult(self.edge_queues[edge.id_].popleft)
            for slot_name, edge in input_edges.items()
            if self.edge_queues[edge.id_]
        }

    def _collect_all_static_edge_inputs(
        self, input_edges: dict[str, model.Edge]
    ) -> dict[str, _EdgeResult]:
        result = {}
        for slot_name, edge in input_edges.items():
            try:
                static_result = self._static_result_cache[edge.id_]
            except KeyError:
                continue
            result[slot_name] = _EdgeResult(_const_callable(static_result))
        return result

    def _collect_defaults(self, node_id: int) -> dict[str, _EdgeResult]:
        return {
            name: _EdgeResult(_const_callable(default))
            for name, default in self.graph.get_slot_defaults(node_id).items()
        }

    def _collect_all_input_values(self, node_id: int) -> dict[str, t.Any]:
        input_edges = self.graph.get_incoming_edges(node_id)

        default_results = {
            name: result
            for name, result in self._collect_defaults(node_id).items()
            if name not in input_edges
        }
        static_input_results = self._collect_all_static_edge_inputs(input_edges)
        dynamic_input_results = self._collect_all_dynamic_edge_inputs(input_edges)

        if not dynamic_input_results and node_id in self._executed_nodes:
            # If all results are static or default then we only want to consume them
            # once.
            raise NodeNotRunnable("Node is static and has been executed already")

        all_results = default_results | static_input_results | dynamic_input_results

        if self.graph.slot_names(node_id) != set(all_results.keys()):
            raise NodeNotRunnable(
                f"Node {node_id} is not ready for execution. Input edges:"
                f"{list(set(input_edges.keys()))} "
                f" Results:g{list(set(all_results.keys()))}"
            )

        return {name: result.use() for name, result in all_results.items()}
