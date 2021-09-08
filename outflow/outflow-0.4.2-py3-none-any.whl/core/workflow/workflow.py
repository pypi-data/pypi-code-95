# -*- coding: utf-8 -*-
from copy import deepcopy

import networkx

from outflow.core.pipeline import context


class Workflow:
    def __init__(self, manager_task=None, parent_workflow=None):
        """
        A class to store a task workflow

        Note: the workflow entrypoint can be any of the workflow tasks


        :param task: the entrypoint of the workflow
        """

        # self.task_key_mapping = {}
        self.digraph = networkx.DiGraph()
        self.manager_task = manager_task
        self.parent_workflow = parent_workflow

        self.db_workflow = self.create_workflow_in_db()

    # def get_or_create_key(self, task):
    #     if task in self.task_key_mapping:
    #         return self.task_key_mapping[task]
    #     else:
    #         task_key = task.name + "-" + str(uuid4())
    #         self.task_key_mapping[task] = task_key
    #         self.directed_graph.add_node(task_key)
    #         return task_key

    def add_node(self, task):
        # task_key = self.get_or_create_key(task)
        self.digraph.add_node(task)
        # self.db_workflow.tasks.append(task.db_task)

    def add_edge(self, parent_task, child_task):
        # parent_task_key = self.get_or_create_key(parent_task)
        # child_task_key = self.get_or_create_key(child_task)
        self.digraph.add_edge(parent_task, child_task)

    def add_external_edge(self, parent_task, child_task):
        if not self.manager_task:
            raise AttributeError(
                "Workflow must have a manager task to create external dependancies"
            )
        else:
            self.manager_task.add_external_edge(parent_task, child_task)

    # def merge(self, workflow):
    #   # self.task_key_mapping.update(workflow.task_key_mapping)
    # self.directed_graph.update(workflow.directed_graph)
    # for task in self.directed_graph:
    #     task.workflow = self

    def __deepcopy__(self, memodict={}):
        from outflow.core.tasks import BaseTask

        new_workflow = Workflow(self.manager_task, self.parent_workflow)
        mapping = {}

        # deepcopy all tasks of the workflow
        for task in self.digraph:
            new_task = deepcopy(task)
            mapping.update({task: new_task})

            # workflow attribute of task not copied, update it here
            new_task.workflow = new_workflow
            new_task.db_task = new_task.create_task_in_db()

            # if task is a manager task
            if hasattr(new_task, "inner_workflow"):
                # replace manager task with the copy
                new_task.inner_workflow.manager_task = new_task
                # same for the database row
                new_task.inner_workflow.db_workflow.manager_task = new_task.db_task

                # attribute external_edge of task not deepcopied
                # recreate the dict with the original task as key, the copied task of the subworkflow as value
                new_task.external_edges = {}
                for parent, child in task.external_edges.items():
                    new_child = [
                        c
                        for c in new_task.inner_workflow.digraph
                        if c.name == child.name
                    ]
                    if len(new_child) != 1:
                        raise Exception("Something is wrong with this workflow")
                    new_task.external_edges.update({parent: new_child[0]})

        new_workflow.digraph = networkx.relabel_nodes(self.digraph, mapping)
        edges = list(networkx.topological_sort(networkx.line_graph(self.digraph)))

        for parent, child in edges:

            BaseTask.add_edge_in_db(mapping[parent], mapping[child])

        for parent, child in self.manager_task.external_edges.items():
            if not hasattr(child, "inner_workflow"):
                try:
                    BaseTask.add_edge_in_db(parent, mapping[child])
                except KeyError:
                    continue

        memodict[id(self)] = new_workflow
        return new_workflow

    def get_parents(self, task):
        return self.digraph.predecessors(task)

    def get_children(self, task):
        return self.digraph.successors(task)

    def __iter__(self):
        for task in self.digraph:
            yield task

    def sorted_tasks(self):
        sorted_tasks = networkx.topological_sort(self.digraph)
        for task in sorted_tasks:
            yield task

    def start_nodes(self):
        start_nodes = []
        for node in self.digraph:
            if self.digraph.in_degree(node) == 0:
                start_nodes.append(node)

        return start_nodes

    def end_nodes(self):
        end_nodes = []
        for node in self.digraph:
            if self.digraph.out_degree(node) == 0:
                end_nodes.append(node)

        return end_nodes

    def create_workflow_in_db(self):
        from outflow.management.models.workflow import Workflow as WorkflowModel

        workflow_row = WorkflowModel.create(
            manager_task_id=self.manager_task.db_task.id if self.manager_task else None,
            parent_workflow_id=self.parent_workflow.db_workflow.id
            if self.parent_workflow
            else None,
            run=context.db_run,
        )

        return workflow_row
