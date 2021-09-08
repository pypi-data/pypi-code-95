# -*- coding: utf-8 -*-
from outflow.core.commands import RootCommand, Command
from outflow.library.tasks import IPythonTask
from outflow.core.pipeline import config


@RootCommand.subcommand(invokable=False, db_untracked=True, backend="default")
def Management():
    pass


@Management.subcommand(with_task_context=True)
def DisplayConfig(self):
    print(config)


@Management.subcommand(db_untracked=False)
class Shell(Command):
    """
    Run an interactive shell with access to the pipeline context. The shell is either a basic python interpreter
    or an IPython interpreter depending on the presence of the flag --ipython
    """

    def setup_tasks(self):
        return IPythonTask()
