import pathlib
import tempfile
import zipfile
from typing import Tuple

import click
from levo_commons.utils import get_grpc_channel

from ...apitesting import levo_testplans_service_pb2 as test_plans_service
from ...apitesting import levo_testplans_service_pb2_grpc as test_plans_service_grpc
from ...env_constants import TEST_PLANS_GRPC_URL
from ...logger import get_logger
from .models import Plan

log = get_logger(__name__)


def get_plan(*, plan_lrn: str, workspace_id: str, authz_header: str) -> Plan:
    directory = pathlib.Path(tempfile.mkdtemp())
    path, plan = download(
        plan_lrn=plan_lrn,
        workspace_id=workspace_id,
        authz_header=authz_header,
        directory=directory,
    )
    extract(path, directory)
    return plan


def download(
    *,
    plan_lrn: str,
    workspace_id: str,
    authz_header: str,
    directory: pathlib.Path,
) -> Tuple[pathlib.Path, Plan]:
    """Downloads the test plan from Levo service by using Levo's GRPC API endpoint."""
    create_plans_directory(directory)

    metadata = [("authorization", authz_header)]
    with get_grpc_channel(TEST_PLANS_GRPC_URL) as channel:
        stub = test_plans_service_grpc.LevoTestPlansServiceStub(channel)
        request = test_plans_service.ExportTestPlanByLrnRequest(test_plan_lrn=plan_lrn)  # type: ignore
        plan = stub.ExportTestPlan(request=request, metadata=metadata)
        plan_path = directory / f"{plan.name}.zip"
        save_plan(plan_path, plan.contents.bytes)
        saved_plan = Plan(
            name=plan.name, lrn=plan_lrn, catalog=directory, workspace_id=workspace_id
        )
        log.debug(
            f"Saved the test plan to directory: {plan_path}",
            request=request,
            metadata=metadata,
            plan=saved_plan,
        )
        return plan_path, saved_plan


def create_plans_directory(directory: pathlib.Path) -> None:
    try:
        directory.mkdir(exist_ok=True)
    except OSError as e:
        click.secho(
            f"Cannot create the directory: {directory} for saving the test plans.",
            fg="red",
        )
        log.error("Could not create plans directory.", error=e)
        raise click.exceptions.Exit(1)


def save_plan(path: pathlib.Path, data: bytes) -> None:
    try:
        with path.open("wb") as fd:
            fd.write(data)
    except OSError as e:
        click.secho(
            "Could not write the downloaded test plans to a file. Please check the permissions.",
            fg="red",
        )
        log.error("Could not save the test plan.", error=e)
        raise click.exceptions.Exit(1)


def extract(path: pathlib.Path, directory: pathlib.Path) -> None:
    """Extract all test plans into `directory`."""
    with zipfile.ZipFile(path) as archive:
        archive.extractall(directory)
