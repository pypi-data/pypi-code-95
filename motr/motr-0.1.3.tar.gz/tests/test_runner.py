import contextlib
import itertools

import attr
import pyrsistent
import pytest
import trio

EMPTY_MAP = pyrsistent.pmap()


@attr.dataclass(frozen=True)
class null_action:
    result: object

    async def __call__(self):
        return self.result


@attr.dataclass(frozen=True)
class SynchAction:
    result: object  # Filled in by test.
    before: trio.Event
    after: trio.Event

    async def __call__(self):
        await self.before.wait()
        self.after.set()
        return self.result


@contextlib.contextmanager
def null_report(action):
    yield


def test_import(runner):
    assert runner


def test_task_wrapper(runner):
    wrapper = runner.TaskWrapper()
    run_count = 0

    async def run():
        nonlocal run_count
        run_count += 1

    trio.run(wrapper, run)
    assert run_count == 1
    trio.run(wrapper, run)
    assert run_count == 1


@pytest.mark.parametrize("count", list(range(10)))
def test_run_all(runner, count):
    run_count = 0

    async def run(arg):
        nonlocal run_count
        run_count += 1

    trio.run(runner.run_all, run, [None] * count)
    assert run_count == count


def test_target_action_comprehensive(exc, result, runner, api):
    pass_result = result.Result.PASSED
    fail_result = result.Result.FAILED
    abort_result = result.Result.ABORTED
    first_action = null_action((pass_result, EMPTY_MAP))
    second_action = null_action((abort_result, EMPTY_MAP))
    third_action = null_action((pass_result, EMPTY_MAP.set(1, 1)))
    reg = api.build(
        itertools.chain(
            api.action(first_action),
            api.target("first_res", first_action),
            api.action(second_action, "first_res"),
            api.target("second_res", second_action),
            api.action(third_action, "second_res"),
            api.target("third_res", third_action),
        ),
    )
    results = {pass_result: [], fail_result: [], abort_result: []}
    target = runner.Target(reg, null_report, results)

    with pytest.raises(exc.MOTRTaskError):
        trio.run(target, "third_res")

    assert results == {
        pass_result: [(first_action, EMPTY_MAP)],
        fail_result: [],
        abort_result: [(second_action, EMPTY_MAP)],
    }


@pytest.mark.parametrize(
    "sequence",
    [
        (0, 0, 1, 1),
        (0, 1, 0, 1),
        (0, 1, 1, 0),
        (1, 0, 0, 1),
        (1, 0, 1, 0),
        (1, 1, 0, 0),
    ],
)
def test_implicit_sequencing(result, runner, api, sequence):
    event = trio.Event()
    event.set()
    sequences = [[], []]
    pass_result = result.Result.PASSED
    fail_result = result.Result.FAILED
    abort_result = result.Result.ABORTED
    final_action = null_action((pass_result, EMPTY_MAP))

    for index in sequence:
        new_event = trio.Event()
        sequences[index].append(
            SynchAction((pass_result, EMPTY_MAP), event, new_event)
        )
        event = new_event

    args = []

    for index, sub_sequence in enumerate(sequences):
        action_0 = f"{index}0"
        res_0 = action_0 + "_res"
        action_1 = f"{index}1"
        res_1 = action_1 + "_res"
        args.extend(api.action(sub_sequence[0]))
        args.extend(api.target(res_0, sub_sequence[0]))
        args.extend(api.action(sub_sequence[1], res_0))
        args.extend(api.target(res_1, sub_sequence[1]))

    args.extend(api.action(final_action, "01_res", "11_res"))
    args.extend(api.target("final_res", final_action))
    reg = api.build(args)
    results = {pass_result: [], fail_result: [], abort_result: []}
    target = runner.Target(reg, null_report, results)
    trio.run(target, "final_res")

    assert results[pass_result]
    assert not results[fail_result]
    assert not results[abort_result]
