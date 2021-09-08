# -*- coding: utf-8 -*-
from copy import deepcopy
from uuid import uuid4

from outflow.core.exceptions import TaskException, IOCheckerError
from outflow.core.generic.string import to_camel_case
from outflow.core.pipeline import context, config
from outflow.core.workflow import WorkflowManager
from outflow.core.logging import logger

from .metaclass import TaskMeta
from ..target import NoDefault


class BaseTask(metaclass=TaskMeta):
    inputs = None
    outputs = None
    parameters = None

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # reset the targets definition attribute to avoid sharing targets definition with subclasses
        cls.inputs = {}
        cls.outputs = {}
        cls.parameters = {}

    def __init__(self, *args, **kwargs):
        self.uuid = str(uuid4())
        self.bind_kwargs = kwargs
        # self.workflow = Workflow(self)
        self.workflow = WorkflowManager.get_context()["workflow"]
        self.workflow.add_node(self)
        self.terminating = False
        self.num_cpus = 1
        self.db_task = self.create_task_in_db()
        self._skip = False

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    @classmethod
    def add_input(cls, target):
        # create the targets def dict if not defined
        cls.inputs.update({target.name: target})

    @classmethod
    def add_output(cls, target):
        cls.outputs.update({target.name: target})

    @classmethod
    def add_parameter(cls, target):
        if target.name in cls.inputs:
            del cls.inputs[target.name]
        cls.parameters.update({target.name: target})

    @property
    def id(
        self,
    ):
        return self.name + "-" + str(self.uuid)

    @classmethod
    def as_task(
        cls,
        run_func=None,
        *,
        name=None,
        with_self=False,
        checkpoint=False,
        parallel=False,
        plugin_name=None,
    ):
        """
        Transform the decorated function into a outflow task.

        Args:
            run_func: The decorated function.
            name (str): Name of the task. By default, this is the name of the
                function in snake case.
            with_self (bool): If true, the run function will be called as a
                regular method, so the "self" of the task is available in the
                task code.
            checkpoint (bool): *NOT IMPLEMENTED* If true, save output targets
                in configured location, and skip tasks if files exists.
            parallel (bool): If true, the task will be running in its own
                actor, so it can run concurrently as other parallel tasks.

        Returns:
            A task class that run the decorated function
        """

        if checkpoint:
            raise NotImplementedError

        if run_func is None:

            def inner_function(_run_func):
                return cls.as_task(
                    _run_func,
                    name=name,
                    with_self=with_self,
                    checkpoint=checkpoint,
                    parallel=parallel,
                    plugin_name=plugin_name,
                )

            return inner_function
        else:
            if name is None:
                name = run_func.__name__

            task_class = type(
                to_camel_case(name),
                (cls,),
                {
                    "run": run_func,
                    "parallel": parallel,
                    "with_self": with_self,
                    "plugin_name": plugin_name,
                },
            )

            return task_class

    def __lshift__(self, task_or_list):
        """
        Link task or list of tasks

        Example: task_or_list = self << task_or_list
        """

        try:
            iter(task_or_list)
        except TypeError:
            self.add_parent(task_or_list)
        else:
            for task in task_or_list:
                self << task

        return task_or_list

    def __rshift__(self, task_or_list):
        """
        Link task or list of tasks

        Example: task_or_list = self >> task_or_list
        """
        try:
            iter(task_or_list)
        except TypeError:
            task_or_list.add_parent(self)
        else:
            for task in task_or_list:
                self >> task

        return task_or_list

    @staticmethod
    def add_edge(parent_task, child_task, save_in_db=True):
        if save_in_db:
            BaseTask.add_edge_in_db(parent_task, child_task)  # TODO

        if parent_task.workflow == child_task.workflow:
            parent_task.workflow.add_edge(parent_task, child_task)
        else:
            workflow = child_task.workflow
            workflow.add_external_edge(parent_task, child_task)
            BaseTask.add_edge(parent_task, workflow.manager_task, save_in_db=False)

    def add_child(self, child_task, save_in_db=True):
        self.add_edge(self, child_task, save_in_db)

    def add_parent(self, parent_task, save_in_db=True):
        self.add_edge(parent_task, self, save_in_db)

    @property
    def parents(self):
        return self.workflow.get_parents(self)

    @property
    def children(self):
        return self.workflow.get_children(self)

    def run(self, *args, **kwargs):
        pass

    @property
    def parameterized_kwargs(self):
        """Generate the parameters kwargs dict from the config file content

        'parameterized_kwargs' refers to parameters used as task arguments and declared in the configuration file.

        Raises:
            TaskException: Raise an exception if task parameters are set but no parameters configuration is found

        Returns:
            dict: kwargs dict generated from the config file content
        """
        if self.parameters:
            try:
                kwargs = config["tasks"][self.name]["parameters"]
            except KeyError as err:
                raise TaskException(
                    f"Could not find parameters of task {self.name} in configuration file"
                ) from err
        else:
            kwargs = {}
        return kwargs

    def __call__(self, *args, **kwargs):
        logger.debug(f"Running task {self.name}")
        if args:
            raise Exception(
                "Task use keyword-only arguments but positional arguments were passed to the run function"
            )

    def bind(self, **kwargs):
        self.bind_kwargs.update(kwargs)

    def __deepcopy__(self, memodict={}):

        cls = self.__class__
        task_copy = cls.__new__(cls)
        memodict[id(self)] = task_copy
        for k, v in self.__dict__.items():
            if k not in ["uuid", "workflow", "db_task", "external_edges"]:
                setattr(task_copy, k, deepcopy(v, memodict))
        task_copy.uuid = uuid4()
        task_copy.workflow = self.workflow
        return task_copy

    @property
    def skip(self):
        return self._skip

    @skip.setter
    def skip(self, val: bool):
        if val:
            self.db_task.skip()
        self._skip = val

        if hasattr(self, "inner_workflow"):
            for inner_task in self.inner_workflow:
                inner_task.skip = val

    def create_task_in_db(self):
        from outflow.management.models.task import Task as TaskModel

        json_inputs, json_outputs = (
            {
                target.name: {
                    "type": getattr(target.type, "__name__", None) or repr(target.type),
                    "default": repr(target.default),
                }
                for target in io
            }
            for io in [self.inputs.values(), self.outputs.values()]
        )
        task_row = TaskModel.create(
            plugin=self.plugin_name,
            name=self.name,
            run=context.db_run,
            uuid=self.uuid,
            input_targets=json_inputs,
            output_targets=json_outputs,
            workflow=self.workflow.db_workflow,
        )

        return task_row

    @staticmethod
    def add_edge_in_db(parent_task, child_task):
        if context.db_untracked:
            return

        logger.debug(f"adding edge {parent_task} >> {child_task}")
        parent_task.db_task.downstream_tasks.append(child_task.db_task)
        context.session.commit()

    def check_inputs(self, task_inputs):
        for target_name, target in self.inputs.items():
            if (
                target_name not in task_inputs
                and self.inputs[target_name].default == NoDefault
                and target_name not in self.bind_kwargs
            ):
                raise IOCheckerError(
                    f"Task {self.name} did not get all expected inputs: expected {[k for k in self.inputs.keys()]}, got "
                    f"{[k for k in task_inputs.keys()]}"
                )
