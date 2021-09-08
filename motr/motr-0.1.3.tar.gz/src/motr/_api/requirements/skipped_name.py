import motr._api.requirements.requirements
import motr.core.registry
import motr.core.target_name


def skipped_name(
    name: str,
) -> motr._api.requirements.requirements.Requirements:
    target_name = motr.core.target_name.coerce(name)
    yield motr.core.registry.SkippedName(target_name)
