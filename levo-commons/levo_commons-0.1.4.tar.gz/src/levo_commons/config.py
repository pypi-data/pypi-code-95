from typing import Optional, Tuple

import attr

CONFIG_VERSION = (1, 0)


@attr.s(slots=True)
class PlanConfig:
    """Test plan configuration."""

    spec_path: Optional[str] = attr.ib(kw_only=True, default=None)
    test_plan_path: Optional[str] = attr.ib(kw_only=True, default=None)
    target_url: str = attr.ib(kw_only=True)
    auth: Optional[Tuple[str, str]] = attr.ib(kw_only=True)
    auth_type: Optional[str] = attr.ib(kw_only=True, default=None)
    report_to_saas: bool = attr.ib(kw_only=True, default=True)
    # Current config version
    version = CONFIG_VERSION
