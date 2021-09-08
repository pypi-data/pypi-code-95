import motr._api.requirements.requirements
import motr.core.registry
import motr.core.runner
import motr.core.target


def action(
    runtime_action: motr.core.runner.RuntimeAction,
    *args: motr.core.target.CoerceToTarget,
) -> motr._api.requirements.requirements.Requirements:
    yield motr.core.registry.Action(runtime_action)
    for arg in args:
        target = motr.core.target.coerce(arg)
        yield motr.core.registry.ActionInput(runtime_action, target)
