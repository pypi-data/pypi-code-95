import motr._api.requirements.requirements
import motr.core.registry


def build(
    requirements: motr._api.requirements.requirements.Requirements,
) -> motr.core.registry.Registry:
    registry = motr.core.registry.Registry()
    for requirement in requirements:
        registry = registry.require(requirement)
    return registry
