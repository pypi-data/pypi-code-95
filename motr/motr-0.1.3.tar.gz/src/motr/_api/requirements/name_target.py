import motr._api.requirements.requirements
import motr.core.registry
import motr.core.target
import motr.core.target_name


def name_target(
    coerce_to_target: motr.core.target.CoerceToTarget, name: str
) -> motr._api.requirements.requirements.Requirements:
    target = motr.core.target.coerce(coerce_to_target)
    target_name = motr.core.target_name.coerce(name)
    yield motr.core.registry.TargetName(target, target_name)
