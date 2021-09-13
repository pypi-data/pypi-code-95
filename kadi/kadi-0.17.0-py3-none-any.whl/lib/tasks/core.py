# Copyright 2020 Karlsruhe Institute of Technology
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from uuid import uuid4

from celery import states
from celery.signals import task_postrun
from celery.signals import task_prerun
from flask import current_app

from .models import Task
from kadi.ext.celery import celery
from kadi.ext.db import db
from kadi.modules.notifications.models import Notification


@task_prerun.connect
def _task_prerun(task_id, **kwargs):
    kwargs = kwargs["kwargs"]

    if "_meta" in kwargs and kwargs["_meta"]["keep"]:
        task = Task.query.get(task_id)

        if task.state == "pending":
            task.state = "running"
            db.session.commit()


@task_postrun.connect
def _task_postrun(task_id, state, **kwargs):
    kwargs = kwargs["kwargs"]

    if "_meta" in kwargs and kwargs["_meta"]["keep"]:
        task = Task.query.get(task_id)

        if task.state == "running":
            if state == states.SUCCESS:
                task.state = "success"
            elif state == states.REVOKED:
                task.state = "revoked"
            else:
                task.state = "failure"

            db.session.commit()


def launch_task(name, args=(), kwargs=None, user=None, keep=False, notify=False):
    """Launch a new celery task by name.

    Note that this function issues one or more database commits if ``keep`` is ``True``.

    :param name: The name of the task.
    :param args: (optional) Positional arguments to pass to the task as tuple.
    :param kwargs: (optional) Keyword arguments to pass to the task as dictionary.
    :param user: (optional) The user that started the task.
    :param keep: (optional) Flag indicating whether the task should be kept in the
        database. See also :class:`.Task`.
    :param notify: (optional) Flag indicating whether the user that started the task
        should be notified about its status, in which case a new instance of
        :class:`.Notification` of type ``"task_status"`` will be created for that user.
        This requires that a valid user is passed and ``keep`` must be ``True`` as
        well.
    :return: A boolean indicating whether the task was launched successfully or not if
        ``keep`` is ``False``. A new :class:`.Task` object or ``None`` if ``keep`` is
        ``True``.
    """
    kwargs = kwargs if kwargs is not None else {}

    if name not in celery.tasks:
        current_app.logger.error(f"Task '{name}' is not registered.")
        return None if keep else False

    task = None
    if keep:
        task = Task.create(creator=user, name=name, args=list(args), kwargs=kwargs)
        db.session.commit()

    kwargs["_meta"] = {
        "user": user.id if user is not None else None,
        "keep": keep,
        "notify": notify,
    }

    try:
        task_id = str(task.id) if task else str(uuid4())
        celery.send_task(name, args=args, kwargs=kwargs, task_id=task_id)
    except Exception as e:
        current_app.logger.exception(e)

        if keep:
            db.session.delete(task)
            db.session.commit()
            return None

        return False

    if user is not None and keep and notify:
        Notification.create(
            user=user, name="task_status", data={"task_id": str(task.id)}
        )
        db.session.commit()

    return task if keep else True
