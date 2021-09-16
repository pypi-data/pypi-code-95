from dataclasses import dataclass, field

from hamcrest import assert_that
from hamcrest.core.base_matcher import BaseMatcher

from microcosm_sagemaker.bundle import Bundle


@dataclass
class BundlePredictionCheck:
    return_value_matcher: BaseMatcher
    args: list = field(default_factory=list)
    kwargs: dict = field(default_factory=dict)

    def check_bundle(self, bundle: Bundle) -> None:
        assert_that(
            bundle.predict(*self.args, **self.kwargs),
            self.return_value_matcher,
        )
