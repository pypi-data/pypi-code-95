from tasking.task import TaskRecord


def test_task_record_stores_data():
    task = TaskRecord()
    task.append(1)
    task.append('a')
    task.append(3.14159)

    assert tuple(task.retrieve()) == (1, 'a', 3.14159)


def test_task_record_returns_last_entry():
    task = TaskRecord()
    assert task.last_entry() is None

    task.append(1)
    assert task.last_entry() == 1

    task.append((1, 2))
    assert task.last_entry() == (1, 2)
