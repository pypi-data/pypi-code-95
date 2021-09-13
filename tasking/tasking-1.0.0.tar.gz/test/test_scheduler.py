import pytest

from tasking.scheduler import Scheduler
from tasking.task import Task


def test_scheduler_raises_error_if_timing_incorrect():
    sch = Scheduler(10, {})

    with pytest.raises(UserWarning):
        sch.run(5)


def test_scheduler_add_task_raises_error_if_timing_incorrect():
    sch = Scheduler(10, {})
    with pytest.raises(UserWarning):
        sch.add_task(Task(), 5)


def test_scheduler_pass_state_and_params_to_tasks():
    task_args = []

    class MyTask(Task):
        def update(self, t, state, params):
            task_args.append((t, state, params))
            return t + 1

    t_ini = 0
    state = {}
    params = {}
    sch = Scheduler(t_ini, state, params)
    sch.add_task(MyTask())

    sch.run(3)

    assert len(task_args) > 0
    t_call, state_call, params_call = task_args[0]
    assert t_call == t_ini
    assert state_call is state
    assert params_call is params


def test_scheduler_stops_when_no_more_tasks_to_evaluate():
    sch = Scheduler(0, {})
    sch.add_task(Task())

    t_fin = 10
    last_time, state = sch.run(t_fin)

    assert last_time < t_fin


def test_scheduler_runs_until_t_end():
    eval_nb = dict(d=0, h=0)

    class TaskD(Task):
        def update(self, t, state, params):
            eval_nb['d'] += 1
            return t + 6

    class TaskH(Task):
        def update(self, t, state, params):
            eval_nb['h'] += 1
            return t + 1

    sch = Scheduler(1, {})
    sch.add_task(TaskD())
    sch.add_task(TaskH())
    sch.add_task(TaskD())

    t_fin = 36
    last_time, state = sch.run(t_fin)

    assert last_time == t_fin
    assert eval_nb['d'] == 6 * 2
    assert eval_nb['h'] == 36


def test_scheduler_returns_last_time_and_last_state():
    class MyTask(Task):
        def update(self, t, state, params):
            state['tugudu'] = t
            return t + 1

    sch = Scheduler(1, {'tugudu': 0})
    sch.add_task(MyTask())

    t_fin = 3
    last_time, state = sch.run(t_fin)

    assert last_time == t_fin
    assert state['tugudu'] == t_fin


def test_scheduler_add_task_raises_error_if_no_task_found_to_add_after():
    class T0(Task):
        pass

    class T1(Task):
        pass

    sch = Scheduler(0, {})
    with pytest.raises(UserWarning):
        sch.add_task(T1(), after=T0)


def test_scheduler_add_task_raises_error_if_no_task_found_to_add_before():
    class T0(Task):
        pass

    class T1(Task):
        pass

    sch = Scheduler(0, {})
    with pytest.raises(UserWarning):
        sch.add_task(T1(), before=T0)


def test_scheduler_add_task_raises_error_if_too_many_tasks_found_to_add_after():
    class T0(Task):
        pass

    class T1(Task):
        pass

    sch = Scheduler(0, {})
    sch.add_task(T0())
    sch.add_task(T0())
    with pytest.raises(UserWarning):
        sch.add_task(T1(), after=T0)


def test_scheduler_add_task_raises_error_if_too_many_tasks_found_to_add_before():
    class T0(Task):
        pass

    class T1(Task):
        pass

    sch = Scheduler(0, {})
    sch.add_task(T0())
    sch.add_task(T0())
    with pytest.raises(UserWarning):
        sch.add_task(T1(), before=T0)


def test_scheduler_add_task_handles_after():
    task_args = []

    class T0(Task):
        def update(self, t, state, params):
            task_args.append(0)
            return t + 1

    class T1(Task):
        def update(self, t, state, params):
            task_args.append(1)
            return t + 1

    class T2(Task):
        def update(self, t, state, params):
            task_args.append(2)
            return t + 1

    sch = Scheduler(1, {})
    sch.add_task(T0())
    sch.add_task(T1())
    sch.add_task(T2(), after=T0)

    t_fin = 3
    last_time, state = sch.run(t_fin)

    assert last_time == t_fin
    assert len(task_args) == 9
    assert all(val == 0 for val in task_args[::3])
    assert all(val == 2 for val in task_args[1::3])
    assert all(val == 1 for val in task_args[2::3])


def test_scheduler_add_task_handles_before():
    task_args = []

    class T0(Task):
        def update(self, t, state, params):
            task_args.append(0)
            return t + 1

    class T1(Task):
        def update(self, t, state, params):
            task_args.append(1)
            return t + 1

    class T2(Task):
        def update(self, t, state, params):
            task_args.append(2)
            return t + 1

    sch = Scheduler(1, {})
    sch.add_task(T0())
    sch.add_task(T1())
    sch.add_task(T2(), before=T1)

    t_fin = 3
    last_time, state = sch.run(t_fin)

    assert last_time == t_fin
    assert len(task_args) == 9
    assert all(val == 0 for val in task_args[::3])
    assert all(val == 2 for val in task_args[1::3])
    assert all(val == 1 for val in task_args[2::3])


def test_scheduler_respects_order_of_process_insertion():
    task_args = []

    class T0(Task):
        def update(self, t, state, params):
            task_args.append(0)
            return t + 1

    class T1(Task):
        def update(self, t, state, params):
            task_args.append(1)
            return t + 1

    class T2(Task):
        def update(self, t, state, params):
            task_args.append(2)
            return t + 1

    sch = Scheduler(1, {})
    sch.add_task(T0())
    sch.add_task(T1())

    _ = sch.run(3)
    assert task_args == [0, 1, 0, 1, 0, 1]

    task_args.clear()
    sch = Scheduler(1, {})
    sch.add_task(T0(), t0=3)
    sch.add_task(T1())
    sch.add_task(T2())

    _ = sch.run(3)
    assert task_args == [1, 2, 1, 2, 0, 1, 2]
