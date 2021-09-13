# Copyright © 2020 Toolchain Labs, Inc. All rights reserved.
#
# Toolchain Labs, Inc. CONFIDENTIAL
#
# This file includes unpublished proprietary source code of Toolchain Labs, Inc.
# The copyright notice above does not evidence any actual or intended publication of such source code.
# Disclosure of this source code or any related proprietary information is strictly prohibited without
# the express written permission of Toolchain Labs, Inc.

from __future__ import annotations

import base64
import logging
import os
import re
import socket
import time
from dataclasses import asdict
from pathlib import Path
from threading import Thread
from typing import Mapping

from pants.base.build_environment import get_git
from pants.engine.environment import CompleteEnvironment
from pants.engine.internals import native_engine
from pants.engine.rules import collect_rules, rule
from pants.engine.streaming_workunit_handler import (
    StreamingWorkunitContext,
    TargetInfo,
    WorkunitsCallback,
    WorkunitsCallbackFactory,
    WorkunitsCallbackFactoryRequest,
)
from pants.engine.unions import UnionRule
from pants.option.option_value_container import OptionValueContainer
from pants.option.subsystem import Subsystem

from toolchain.pants.auth.store import AuthStore
from toolchain.pants.buildsense.client import BuildSenseClient
from toolchain.pants.buildsense.common import RunTrackerBuildInfo, WorkUnits, WorkUnitsMap
from toolchain.pants.buildsense.state import BuildState
from toolchain.pants.common.toolchain_setup import ToolchainSetup

logger = logging.getLogger(__name__)


def optional_dir_option(dn: str) -> str:
    # Similar to Pant's dir_option, but doesn't require the directory to exist.
    return os.path.normpath(dn)


class Reporter(Subsystem):
    options_scope = "buildsense"
    help = """Configuration for Toolchain's BuildSense reporting."""

    @classmethod
    def register_options(cls, register):

        register(
            "--timeout",
            advanced=True,
            type=int,
            default=5,
            help="Wait at most this many seconds for network calls to complete.",
        )
        register("--dry-run", type=bool, help="Go thru the motions w/o making network calls", default=False)
        register(
            "--local-build-store",
            advanced=True,
            type=bool,
            default=True,
            help="Store failed uploads and try to upload later.",
        )
        register(
            "--local-store-base",
            advanced=True,
            type=optional_dir_option,
            default=".pants.d/toolchain/buildsense/",
            help="Base direcory for storing buildsense data locally",
        )
        register(
            "--max-batch-size-mb",
            advanced=True,
            type=int,
            default=20,
            help="Maximum batch size to try and upload (uncompressed).",
        )
        register(
            "--ci-env-var-pattern",
            advanced=True,
            type=str,
            default=None,
            help="CI Environment variables regex pattern.",
        )
        register(
            "--enable",
            type=bool,
            default=True,
            help="Enables the BuildSense reporter plugin",
        )
        register(
            "--log-upload",
            type=bool,
            default=True,
            advanced=True,
            help="Upload pants logs to buildsense",
        )
        register(
            "--ci-env-scrub-terms",
            type=list,
            default=list(CaptureCIEnv.DEFAULT_EXCLUDE_TERMS),
            advanced=True,
            help="patterns for environment variables to exclude from uploaded CI env variables",
        )
        register(
            "--show-link",
            type=bool,
            default=True,
            advanced=True,
            help="Show link to the pants run in BuildSense Web UI.s",
        )


class ReporterCallback(WorkunitsCallback):
    """Configuration for Toolchain's BuildSense reporting."""

    def __init__(
        self,
        options: OptionValueContainer,
        auth_store: AuthStore,
        env: Mapping[str, str],
        repo_name: str | None,
        base_url: str,
    ):
        super().__init__()
        self._env = env
        self._enabled = False
        if not options.enable:
            logger.debug("BuildSense plugin is disabled.")
            return
        if not repo_name:
            logger.warning("Couldn't determine repo name. BuildSense plugin will be disabled.")
            return
        client = BuildSenseClient.from_options(
            client_options=options, auth=auth_store, repo=repo_name, base_url=base_url
        )
        # set self._build_state *before* changing the state.
        self._build_state = BuildState(
            client,
            local_store_base_path=Path(options.local_store_base),
            max_batch_size_mb=options.max_batch_size_mb,
            local_store_enabled=options.local_build_store,
        )

        self._enabled = True
        self._log_upload = options.log_upload
        self._call_count = 0
        self._reporter_thread = ReportThread(self._build_state)
        self._ci_capture = CaptureCIEnv(pattern=options.ci_env_var_pattern, exclude_terms=options.ci_env_scrub_terms)
        self._build_link_logged = not options.show_link
        logger.debug("BuildSense Plugin enabled")

    @property
    def can_finish_async(self) -> bool:
        return True

    def __call__(
        self,
        *,
        completed_workunits: WorkUnits,
        started_workunits: WorkUnits,
        context: StreamingWorkunitContext,
        finished: bool = False,
        **kwargs,
    ) -> None:
        if not self._enabled:
            return
        self.handle_workunits(
            completed_workunits=completed_workunits,
            started_workunits=started_workunits,
            context=context,
            finished=finished,
        )

    def handle_workunits(
        self,
        *,
        completed_workunits: WorkUnits,
        started_workunits: WorkUnits,
        context: StreamingWorkunitContext,
        finished: bool,
    ) -> None:
        work_units_map = {wu["span_id"]: wu for wu in (started_workunits or [])}
        work_units_map.update({wu["span_id"]: wu for wu in (completed_workunits or [])})
        logger.debug(
            f"handle_workunits total={len(work_units_map)} completed={len(completed_workunits)} started={len(started_workunits)} finished={finished} calls={self._call_count}"
        )
        self._maybe_show_buildsense_link()
        self._build_state.set_context(context)
        if self._call_count == 0 and not finished:
            # If the first invocation of ReporterCallback by pants is also the last one
            # (i.e. if finished=True), then we don't send the initial report to buildsense.

            self._enqueue_initial_report(context)
        if finished:
            self._on_finish(context, self._call_count, work_units_map)
        else:
            self._build_state.queue_workunits(self._call_count, work_units_map)
        self._call_count += 1

    def _maybe_show_buildsense_link(self) -> None:
        if not self._build_link_logged and self._build_state.build_link:
            logger.info(f"View on BuildSense: {self._build_state.build_link}")
            self._build_link_logged = True

    def _enqueue_initial_report(self, context: StreamingWorkunitContext) -> None:
        run_tracker_info = self._get_run_tracker_info(context)
        logger.debug(f"enqueue_initial_report {run_tracker_info.run_id}")
        self._build_state.queue_initial_report(run_tracker_info)

    def _on_finish(self, context: StreamingWorkunitContext, call_count: int, work_units_map: WorkUnitsMap) -> None:
        run_tracker_info = self._get_run_tracker_info(context)
        self._build_state.build_ended(run_tracker_info, call_count=call_count, work_units_map=work_units_map)
        self._reporter_thread.stop_thread()

    def _get_run_tracker_info(self, context: StreamingWorkunitContext) -> RunTrackerBuildInfo:
        ci_env = self._ci_capture.capture(self._env)
        run_tracker = context.run_tracker
        has_ended = run_tracker.has_ended()

        # Copy the RunTracker info before mutating it in _adjust_run_info_fields.
        run_info = dict(run_tracker.run_information())
        _adjust_run_info_fields(run_info, run_tracker.goals, has_ended)

        build_stats = {
            "run_info": run_info,
            "recorded_options": run_tracker.get_options_to_record(),
        }

        if ci_env:
            build_stats["ci_env"] = ci_env

        if has_ended:
            build_stats.update(
                {
                    "pantsd_stats": run_tracker.pantsd_scheduler_metrics,
                    "cumulative_timings": run_tracker.get_cumulative_timings(),
                    "counter_names": list(run_tracker.counter_names),
                }
            )
            targets_specs = _get_expanded_specs(context)
            if targets_specs:
                build_stats["targets"] = targets_specs
            observation_histograms = _get_historgrams(context)
            if observation_histograms:
                build_stats["observation_histograms"] = observation_histograms
        upload_log = all((has_ended, self._log_upload, run_tracker.run_logs_file))
        log_file = Path(run_tracker.run_logs_file) if upload_log else None
        return RunTrackerBuildInfo(has_ended=has_ended, build_stats=build_stats, log_file=log_file)


def _get_expanded_specs(context: StreamingWorkunitContext) -> dict[str, list[dict[str, str]]] | None:
    def to_targets_dicts(targets: list[TargetInfo]) -> list[dict[str, str]]:
        return [asdict(target) for target in targets]

    targets = context.get_expanded_specs().targets
    return {spec: to_targets_dicts(targets) for spec, targets in targets.items()}


def _get_historgrams(context: StreamingWorkunitContext) -> dict | None:
    histograms_info = context.get_observation_histograms()
    version = histograms_info["version"]

    if version != 0:
        logger.warning(f"Cannot encode internal metrics histograms: unexpected version {version}")
        return None
    histograms = histograms_info["histograms"]
    if not histograms:
        return None
    return {
        "version": version,
        "histograms": {key: base64.b64encode(value).decode() for key, value in histograms.items()},
    }


def _adjust_run_info_fields(run_info: dict, goals: list[str], has_ended: bool) -> None:
    host = socket.gethostname()
    run_info["machine"] = f"{host} [docker]" if _is_docker() else host
    scm = get_git()
    if scm:
        revision = scm.commit_id
        run_info.update(revision=revision, branch=scm.branch_name or revision)
    else:
        logger.warning("Can't get git scm info")

    if "parent_build_id" in run_info:
        del run_info["parent_build_id"]

    run_info["computed_goals"] = goals
    if not has_ended:
        run_info["outcome"] = "NOT_AVAILABLE"


def _is_docker() -> bool:
    # Based on https://github.com/jaraco/jaraco.docker/blob/master/jaraco/docker.py
    # https://stackoverflow.com/a/49944991/38265
    cgroup = Path("/proc/self/cgroup")
    return Path("/.dockerenv").exists() or (cgroup.exists() and "docker" in cgroup.read_text("utf-8"))


class ReportThread:
    def __init__(self, build_state: BuildState) -> None:
        self._logging_destination = native_engine.stdio_thread_get_destination()
        self._build_state = build_state
        self._terminate = False
        self._reporter_thread = Thread(target=self._report_loop, name="buildsense-reporter", daemon=True)
        self._reporter_thread.start()

    def stop_thread(self):
        self._terminate = True
        self._reporter_thread.join()

    def _report_loop(self):
        native_engine.stdio_thread_set_destination(self._logging_destination)
        while not self._terminate:
            operation = self._build_state.send_report()
            if operation.is_sent():
                # If we send something in this call, then we don't need to sleep.
                continue
            time.sleep(2 if operation.is_error() else 0.05)
        self._build_state.send_final_report()


class CaptureCIEnv:
    _CI_MAP = {
        "CIRCLECI": re.compile(r"^CIRCLE.*"),
        "TRAVIS": re.compile(r"^TRAVIS.*"),
        "GITHUB_ACTIONS": re.compile(r"^GITHUB.*"),
        # Unlike other CI systems, BITBUCKET doesn't have a default env variable that
        # indicates the it is a bitbucket environment.
        # See: https://support.atlassian.com/bitbucket-cloud/docs/variables-and-secrets/
        "BITBUCKET_BUILD_NUMBER": re.compile(r"^BITBUCKET.*"),
        "BUILDKITE": re.compile(r"^BUILDKITE.*"),
    }
    DEFAULT_EXCLUDE_TERMS = ("ACCESS", "TOKEN", "SECRET")

    def __init__(self, *, pattern: str | None, exclude_terms: list[str]) -> None:
        self._pattern = re.compile(pattern) if pattern else None
        self._exclude_expression = re.compile("|".join(f".*{re.escape(v)}.*" for v in exclude_terms))

    def _get_pattern(self, env: Mapping[str, str]) -> re.Pattern | None:
        for ci_name, capture_expression in self._CI_MAP.items():
            if ci_name in env:
                return capture_expression
        return None

    def capture(self, env: Mapping[str, str]) -> dict[str, str] | None:
        captured = self._capture_ci_env(env)
        return self._scrub(captured) if captured else None

    def _capture_ci_env(self, env: Mapping[str, str]) -> dict[str, str] | None:
        pattern = self._pattern or self._get_pattern(env)
        if not pattern:
            return None
        return {key: value for key, value in env.items() if pattern.match(key)}

    def _scrub(self, captured: dict[str, str]) -> dict[str, str]:
        scrubbed_keys = set()
        final_data = {}
        for key, value in captured.items():
            if self._exclude_expression.match(key):
                scrubbed_keys.add(key)
            else:
                final_data[key] = value
        captured_str = ",".join(sorted(captured.keys()))
        if scrubbed_keys:
            final_captured_str = ",".join(sorted(final_data.keys()))
            logger.debug(f"captured CI env: {captured_str} scrubbed: {scrubbed_keys} final: {final_captured_str}")
        else:
            logger.debug(f"captured CI env: {captured_str}")
        return final_data


class BuildsenseCallbackFactoryRequest:
    """A unique request type that is installed to trigger construction of our WorkunitsCallback."""


@rule
def construct_buildsense_callback(
    _: BuildsenseCallbackFactoryRequest,
    reporter: Reporter,
    toolchain_setup: ToolchainSetup,
    auth_store: AuthStore,
    environment: CompleteEnvironment,
) -> WorkunitsCallbackFactory:
    repo_name = toolchain_setup.safe_get_repo_name()
    return WorkunitsCallbackFactory(
        lambda: ReporterCallback(
            reporter.options,
            auth_store=auth_store,
            env=dict(environment),
            repo_name=repo_name,
            base_url=toolchain_setup.base_url,
        )
    )


def rules():
    return [
        UnionRule(WorkunitsCallbackFactoryRequest, BuildsenseCallbackFactoryRequest),
        *collect_rules(),
    ]
