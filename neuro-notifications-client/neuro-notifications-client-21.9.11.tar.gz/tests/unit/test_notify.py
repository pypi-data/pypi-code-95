from datetime import datetime

import pytest

from notifications_client import (
    Client,
    JobCannotStartLackResources,
    JobCannotStartQuotaReached,
    JobTransition,
    QuotaWillBeReachedSoon,
)
from notifications_client.notifications import JobNotification, QuotaResourceType


# TODO: make this tests more meaningful:
# at the moment they just test that no exception was raised


@pytest.mark.parametrize(
    "notification",
    [
        JobTransition(
            "job-new-transition",
            status="PENDING",
            transition_time=datetime(year=2019, month=6, day=7),
        ),
        JobTransition(
            "job-started",
            status="RUNNING",
            transition_time=datetime(year=2019, month=6, day=8),
            prev_status="PENDING",
            prev_transition_time=datetime(year=2019, month=6, day=7),
        ),
        JobTransition(
            "job-failed-exit",
            status="FAILED",
            transition_time=datetime(year=2019, month=6, day=9),
            prev_status="RUNNING",
            prev_transition_time=datetime(year=2019, month=6, day=8),
            reason="Exited with code -10",
            exit_code=-10,
        ),
        JobTransition(
            "job-failed-image",
            status="FAILED",
            transition_time=datetime(year=2019, month=6, day=10),
            prev_status="PENDING",
            prev_transition_time=datetime(year=2019, month=6, day=9),
            reason="ImagePullBackOff",
            description="Cannot pull image some:tag",
        ),
        JobTransition(
            "job-finished",
            status="SUCCEEDED",
            transition_time=datetime(year=2019, month=6, day=11),
            prev_status="RUNNING",
            prev_transition_time=datetime(year=2019, month=6, day=10),
            exit_code=0,
        ),
    ],
)
async def test_job_transition_notifications(
    client: Client,
    notification: JobNotification,
) -> None:
    # Should not raise anything
    await client.notify(notification)
    await client.close()


@pytest.mark.parametrize(
    "notification", [JobCannotStartLackResources("job-lack-resources")]
)
async def test_job_notifications(
    client: Client,
    notification: JobNotification,
) -> None:
    # Should not raise anything
    await client.notify(notification)
    await client.close()


@pytest.mark.parametrize(
    "notification",
    [
        JobCannotStartQuotaReached(
            user_id="job-quota-reached",
            resource=QuotaResourceType.NON_GPU,
            quota=2.1,
            cluster_name="test",
        )
    ],
)
async def test_user_notifications(
    client: Client,
    notification: JobNotification,
) -> None:
    # Should not raise anything
    await client.notify(notification)
    await client.close()


@pytest.mark.parametrize(
    "notification",
    [
        QuotaWillBeReachedSoon(
            "job-quota-reached",
            resource=QuotaResourceType.NON_GPU,
            used=1,
            quota=2,
            cluster_name="default",
        ),
        QuotaWillBeReachedSoon(
            "job-quota-reached",
            resource=QuotaResourceType.GPU,
            used=2,
            quota=3,
            cluster_name="default",
        ),
    ],
)
async def test_quota_will_be_reached_soon_notifications(
    client: Client,
    notification: QuotaWillBeReachedSoon,
) -> None:
    # Should not raise anything
    await client.notify(notification)
    await client.close()


async def test_unknown_notifications(
    client: Client,
    unknown_notification: JobNotification,
) -> None:
    with pytest.raises(ValueError):
        await client.notify(unknown_notification)
        await client.close()
