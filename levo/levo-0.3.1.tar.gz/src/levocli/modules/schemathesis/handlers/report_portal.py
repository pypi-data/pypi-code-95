import base64
import enum
import os
import time
import traceback
from typing import Dict, List, Optional, Set, Tuple, Union, cast

import levo_commons.status
from levo_commons import events
from reportportal_client import ReportPortalService
from schemathesis.constants import CodeSampleStyle

from ....apitesting.runs.api_test_runs_pb2 import (  # type: ignore
    CATEGORY_FAILED,
    CATEGORY_SUCCESS,
    ApiEndpointTestsCategory,
)
from ....env_constants import BASE_URL
from ....handlers import EventHandler
from ....logger import get_logger
from ....utils import fetch_schema_as_lines
from ...utils import get_formatted_request_response
from ..context import EndpointExecutionContext, ExecutionContext
from ..models import (
    AfterExecutionPayload,
    BeforeExecutionPayload,
    FinishedPayload,
    Response,
    SerializedCase,
    SerializedCheck,
    SerializedError,
    SerializedTestResult,
    Status,
)
from .default import get_summary_message_parts

log = get_logger(__name__)

DISABLE_SCHEMA_VALIDATION_MESSAGE = (
    "\nYou can disable input schema validation with --validate-schema=false "
    "command-line option\nIn this case, Schemathesis cannot guarantee proper"
    " behavior during the test run"
)

TEST_RUNS_SERVICE_URL = os.getenv("TEST_RUNS_SERVICE_URL", BASE_URL + "/test-runs")
STATUS_DICT = {
    Status.success: "PASSED",
    Status.failure: "FAILED",
    Status.error: "FAILED",
}


class HandlerState(enum.Enum):
    """Different states for ReportPortal handler lifecycle."""

    # Instance is created. The default state
    NEW = enum.auto()
    # Launch started, ready to handle events
    ACTIVE = enum.auto()
    # Launch is interrupted, no events will be processed after it
    INTERRUPTED = enum.auto()


def timestamp():
    return str(int(time.time() * 1000))


def _get_endpoint_name(method, relative_path):
    return f"{method} {relative_path}"


def _get_endpoint_context(
    context: ExecutionContext,
    endpoint_name: str,
    service: ReportPortalService,
):
    if endpoint_name not in context.endpoint_to_context:
        item_id = service.start_test_item(
            name=endpoint_name,
            description=endpoint_name,
            start_time=timestamp(),
            item_type="SUITE",
        )

        # If this is the first test case that was executed for this endpoint, add a context at the endpoint level
        # and record the item id.
        endpoint_context = EndpointExecutionContext(
            test_item_id=item_id, name=endpoint_name
        )
        log.info(
            f"Started the test suite for endpoint: {endpoint_name}",
            context=endpoint_context,
        )
        context.endpoint_to_context[endpoint_name] = endpoint_context
    return context.endpoint_to_context[endpoint_name]


def handle_before_execution(
    context: ExecutionContext,
    event: events.BeforeTestCaseExecution[BeforeExecutionPayload],
    service: ReportPortalService,
) -> None:
    endpoint_name = _get_endpoint_name(
        event.payload.method, event.payload.relative_path
    )
    _get_endpoint_context(context, endpoint_name, service)

    if event.payload.recursion_level > 0:
        # This value is not `None` - the value is set in runtime before this line
        context.operations_count += 1  # type: ignore


def handle_after_execution(
    context: ExecutionContext,
    event: events.AfterTestCaseExecution[AfterExecutionPayload],
    service: ReportPortalService,
) -> None:
    context.hypothesis_output.extend(event.payload.hypothesis_output)

    endpoint_name = _get_endpoint_name(
        event.payload.method, event.payload.relative_path
    )
    endpoint_context = _get_endpoint_context(context, endpoint_name, service)
    endpoint_context.operations_processed += 1
    endpoint_context.results.append(event.payload.result)

    # if event.payload.hypothesis_output is not None:
    #     report_log(
    #         message=str(event.payload.hypothesis_output),
    #         service=service,
    #         item_id=test_item_id,
    #     )
    # if event.payload.result.has_errors:
    #     report_log(
    #         message=get_single_error(context, event.payload.result),
    #         service=service,
    #         level="ERROR",
    #         item_id=test_item_id,
    #     )
    # if event.payload.result.has_failures:
    #     report_log(
    #         message=get_failures_for_single_test(context, event.payload.result),
    #         service=service,
    #         level="ERROR",
    #         item_id=test_item_id,
    #     )


def _report_check_as_test_case(endpoint_name, check_name, checks, context, service):
    endpoint_context = context.endpoint_to_context[endpoint_name]
    test_case_item_id = service.start_test_item(
        name=check_name,
        description=check_name,
        start_time=timestamp(),
        item_type="TEST",
        # Mark the test suite item id as parent_item_id
        parent_item_id=endpoint_context.test_item_id,
    )

    duration = 0
    successful_tests = 0
    failed_tests = 0
    errored_tests = 0
    status = Status.success
    for check in checks:
        duration += check.duration

        if check.value == Status.error:
            errored_tests += 1
        elif check.value == Status.failure:
            failed_tests += 1
            status = Status.failure
        else:
            successful_tests += 1

    test_item_attributes = {
        "elapsed_time": duration,
        "success_count": successful_tests,
        "failed_count": failed_tests,
        "errored_count": errored_tests,
    }
    service.finish_test_item(
        item_id=test_case_item_id,
        end_time=timestamp(),
        status=STATUS_DICT[status],
        attributes=test_item_attributes,
    )
    log.debug(
        f"Finished the test case for check: {check_name} and endpoint: {endpoint_name}",
        attributes=test_item_attributes,
        item_id=test_case_item_id,
        status=status,
    )

    _send_endpoint_test_request_response_bodies(
        test_case_item_id, endpoint_context, service
    )
    return status


def _send_endpoint_test_request_response_bodies(
    test_item_id, endpoint_context, service
):
    # Send all the requests and responses of all the steps from the actual test to SaaS
    # when the test fails.
    lines = []
    for result in endpoint_context.results:
        for interaction in result.interactions:
            if interaction.status != levo_commons.status.Status.success:
                lines.append(
                    get_formatted_request_response(
                        interaction.status,
                        interaction.recorded_at,
                        interaction.request,
                        interaction.response,
                    )
                )
    if len(lines) > 0:
        attachment = {
            "name": "request-response-" + test_item_id,
            "data": "\n".join(lines),
            "mime": "text/plain",
        }
        service.log(timestamp(), attachment["name"], attachment=attachment)
        log.debug(
            "Sending the request-response body for test.",
            item_id=test_item_id,
            attachment=attachment,
        )


def get_hypothesis_output(hypothesis_output: List[str]) -> Optional[str]:
    """Show falsifying examples from Hypothesis output if there are any."""
    if hypothesis_output:
        return get_section_name("HYPOTHESIS OUTPUT") + "\n".join(hypothesis_output)
    return None


def get_errors(
    context: ExecutionContext, event: events.Finished[FinishedPayload]
) -> Optional[str]:
    """Get all errors in the test run."""
    if not event.payload.has_errors:
        return None

    lines = [get_section_name("ERRORS")]
    for endpoint_context in context.endpoint_to_context.values():
        for result in endpoint_context.results:
            if not result.has_errors:
                continue
            lines.append(get_single_error(context, result))
    if event.payload.generic_errors:
        lines.append(get_generic_errors(context, event.payload.generic_errors))
    return "\n".join(lines)


def get_single_error(
    context: ExecutionContext,
    result: SerializedTestResult,
) -> str:
    lines = [get_subsection(result)]
    for error in result.errors:
        lines.append(_get_error(context, error, result.seed))
    return "\n".join(lines)


def get_generic_errors(
    context: ExecutionContext,
    errors: List[SerializedError],
) -> str:
    lines = []
    for error in errors:
        lines.append(get_section_name(error.title or "Generic error", "_"))
        lines.append(_get_error(context, error))
    return "\n".join(lines)


def _get_error(
    context: ExecutionContext,
    error: SerializedError,
    seed: Optional[int] = None,
) -> str:
    if context.show_errors_tracebacks:
        message = error.exception_with_traceback
    else:
        message = error.exception
    if error.exception.startswith("InvalidSchema") and context.validate_schema:
        message += DISABLE_SCHEMA_VALIDATION_MESSAGE + "\n"
    if error.example is not None:
        get_example(context, error.example, seed=seed)
    return message


def get_failures(
    context: ExecutionContext, event: events.Finished[FinishedPayload]
) -> Optional[str]:
    """Get all failures in the test run."""
    if not event.payload.has_failures:
        return None
    relevant_results = []
    for endpoint_context in context.endpoint_to_context.values():
        relevant_results.extend(
            [result for result in endpoint_context.results if not result.is_errored]
        )
    if not relevant_results:
        return None
    lines = [get_section_name("FAILURES")]
    for result in relevant_results:
        if not result.has_failures:
            continue
        lines.append(get_failures_for_single_test(context, result))
    return "\n".join(lines)


def get_failures_for_single_test(
    context: ExecutionContext,
    result: SerializedTestResult,
) -> str:
    """Gets a failure for a single method / path."""
    lines = [get_subsection(result)]
    checks = get_unique_failures(result.checks)
    for idx, check in enumerate(checks, 1):
        message: Optional[str]
        if check.message:
            message = f"{idx}. {check.message}"
        else:
            message = None
        lines.append(
            get_example(context, check.example, check.response, message, result.seed)
        )
    return "\n".join(lines)


def get_unique_failures(checks: List[SerializedCheck]) -> List[SerializedCheck]:
    """Return only unique checks that should be displayed in the output."""
    seen: Set[Tuple[str, Optional[str]]] = set()
    unique_checks = []
    for check in reversed(checks):
        # There are also could be checks that didn't fail
        if check.value == Status.failure:
            key = get_failure_key(check)
            if (check.name, key) not in seen:
                unique_checks.append(check)
                seen.add((check.name, key))
    return unique_checks


def get_failure_key(check: SerializedCheck) -> Optional[str]:
    return check.message


def reduce_schema_error(message: str) -> str:
    """Reduce the error schema output."""
    end_of_message_index = message.find(":", message.find("Failed validating"))
    if end_of_message_index != -1:
        return message[:end_of_message_index]
    return message


def get_example(
    context: ExecutionContext,
    case: SerializedCase,
    response: Optional[Response] = None,
    message: Optional[str] = None,
    seed: Optional[int] = None,
) -> str:
    lines = []
    if message is not None:
        if not context.verbosity:
            lines.append(reduce_schema_error(message))
    for line in case.text_lines:
        lines.append(line)

    if response is not None and response.body is not None:
        payload = base64.b64decode(response.body).decode(
            response.encoding or "utf8", errors="replace"
        )
        lines.append(f"----------\n\nResponse payload: `{payload}`\n")
    if context.code_sample_style == CodeSampleStyle.python:
        lines.append(
            f"Run this Python code to reproduce this failure: \n\n    {case.requests_code}\n"
        )
    if context.code_sample_style == CodeSampleStyle.curl:
        lines.append(
            f"Run this cURL command to reproduce this failure: \n\n    {case.curl_code}\n"
        )
    if seed is not None:
        lines.append(
            f"Or add this option to your command line parameters: --hypothesis-seed={seed}"
        )
    return "\n".join(lines)


def get_subsection(
    result: SerializedTestResult,
) -> str:
    return get_section_name(result.verbose_name, "_", result.data_generation_method)


def get_statistic(event: events.Finished[FinishedPayload]) -> str:
    """Format and print statistic collected by :obj:`models.TestResult`."""
    lines = [get_section_name("SUMMARY")]
    total = event.payload.total
    if event.payload.is_empty or not total:
        lines.append("No checks were performed.")

    if total:
        lines.append(get_checks_statistics(total))

    return "\n".join(lines)


def get_checks_statistics(total: Dict[str, Dict[Union[str, Status], int]]) -> str:
    lines = []
    for check_name, results in total.items():
        lines.append(get_check_result(check_name, results))
    return "Performed checks:" + "\n".join(lines)


def get_check_result(
    check_name: str,
    results: Dict[Union[str, Status], int],
) -> str:
    """Show results of single check execution."""
    success = results.get(Status.success, 0)
    total = results.get("total", 0)
    return check_name + ": " + f"{success} / {total} passed"


def get_internal_error(
    context: ExecutionContext, event: events.InternalError
) -> Optional[str]:
    message = None
    if event.exception:
        if context.show_errors_tracebacks:
            message = event.exception_with_traceback
        else:
            message = event.exception
        message = (
            f"Error: {message}\n"
            f"Add this option to your command line parameters to see full tracebacks: --show-errors-tracebacks"
        )
        if event.exception_type == "jsonschema.exceptions.ValidationError":
            message += "\n" + DISABLE_SCHEMA_VALIDATION_MESSAGE
    return message


def get_summary(event: events.Finished[FinishedPayload]) -> str:
    message = get_summary_output(event)
    return get_section_name(message)


def get_summary_output(event: events.Finished[FinishedPayload]) -> str:
    parts = get_summary_message_parts(event)
    if not parts:
        message = "Empty test suite"
    else:
        message = f'{", ".join(parts)} in {event.running_time:.2f}s'
    return message


def get_section_name(title: str, separator: str = "=", extra: str = "") -> str:
    """Print section name with separators in terminal with the given title nicely centered."""
    extra = extra if not extra else f" [{extra}]"
    return f" {title}{extra} ".center(80, separator)


def handle_finished(
    context: ExecutionContext,
    event: events.Finished[FinishedPayload],
    service: ReportPortalService,
    state: HandlerState,
) -> str:
    """Report the outcome of the whole testing session to Levo SaaS."""
    # Report each check for each endpoint as a test case.
    status = Status.success
    for endpoint_name, endpoint_context in context.endpoint_to_context.items():
        endpoint_status = _report_finish_endpoint(
            context, endpoint_context, endpoint_name, service
        )
        if endpoint_status == Status.error:
            status = endpoint_status
        elif endpoint_status == Status.failure and status != Status.error:
            status = Status.failure

    report_log(get_statistic(event), service)
    report_log(get_summary(event), service)

    if state == HandlerState.INTERRUPTED:
        return "INTERRUPTED"
    else:
        # If all the checks have passed, return a PASSED status, otherwise return FAILED.
        return STATUS_DICT[status]


def _report_finish_endpoint(context, endpoint_context, endpoint_name, service):
    check_name_to_list: Dict[str, List[SerializedCheck]] = {}
    duration = 0
    for result in endpoint_context.results:
        for check in result.checks:
            if check.name not in check_name_to_list:
                check_name_to_list[check.name] = []
            check_name_to_list[check.name].append(check)
            duration += check.duration

    success_count = 0
    failed_count = 0
    errored_count = 0
    for check_name, checks in check_name_to_list.items():
        status = _report_check_as_test_case(
            endpoint_name, check_name, checks, context, service
        )
        if status == Status.error:
            errored_count += 1
        elif status == Status.failure:
            failed_count += 1
        else:
            success_count += 1

    # Finish the test suite for this endpoint.
    test_item_attributes = {
        "elapsed_time": duration,
        "success_count": success_count,
        "failed_count": failed_count,
        "errored_count": errored_count,
    }
    endpoint_status = Status.success
    if errored_count > 0:
        endpoint_status = Status.error
    elif failed_count > 0:
        endpoint_status = Status.failure
    service.finish_test_item(
        item_id=endpoint_context.test_item_id,
        end_time=timestamp(),
        status=STATUS_DICT[endpoint_status],
        attributes=test_item_attributes,
    )
    log.info(
        f"Test Suite for endpoint: {endpoint_name} finished with status: {endpoint_status}"
    )
    return endpoint_status


def report_log(
    message: str, service: ReportPortalService, level="INFO", item_id=None
) -> None:
    if message is None:
        return
    service.log(time=timestamp(), message=message, item_id=item_id, level=level)
    log.debug("Reporting the log.", message=message, item_id=item_id)


def my_error_handler(exc_info):
    """
    This callback function will be called by async service client when error occurs.
    Return True if error is not critical and you want to continue work.
    :param exc_info: result of sys.exc_info() -> (type, value, traceback)
    :return:
    """
    traceback.print_exception(*exc_info)


def terminate_launch(service: ReportPortalService, status="PASSED") -> None:
    service.finish_launch(end_time=timestamp(), status=status)
    log.info(f"Finished the launch with status: {status}")
    service.terminate()


class SchemathesisReportPortalHandler(EventHandler):
    def __init__(self, project, token, spec_path):
        self.service = ReportPortalService(
            endpoint=TEST_RUNS_SERVICE_URL, project=project, token=token
        )
        self.state = HandlerState.NEW
        self.spec = fetch_schema_as_lines(spec_path)

    def _set_state(self, state: HandlerState) -> None:
        self.state = state

    def _terminate_launch(self, status: str) -> None:
        if self.state == HandlerState.ACTIVE:
            terminate_launch(self.service, status)

    def handle_event(self, context: ExecutionContext, event: events.Event) -> None:
        """Reports the test results to ReportPortal service."""
        if isinstance(event, events.Initialized):
            # Create a launch in report portal
            launch_name = "Schema conformance test"
            launch_attr = {
                "target_url": event.payload.base_url,
            }
            self.service.start_launch(
                name=launch_name,
                start_time=timestamp(),
                description=launch_name,
                attributes=launch_attr,
            )
            self._set_state(HandlerState.ACTIVE)
            context.operations_count = cast(
                int, event.payload.operations_count
            )  # INVARIANT: should not be `None`
            log.info(
                f"Test is ready to be run with {context.operations_count} endpoints."
            )
        if isinstance(event, events.BeforeTestCaseExecution):
            handle_before_execution(context, event, self.service)
        if isinstance(event, events.AfterTestCaseExecution):
            handle_after_execution(context, event, self.service)
        if isinstance(event, events.Finished):
            # Send the schema as an attachment.
            attachment = {
                "name": "schema",
                "data": "".join(self.spec),
                "mime": "text/plain",
            }
            self.service.log(timestamp(), "schema", attachment=attachment)
            status = handle_finished(context, event, self.service, self.state)
            self._terminate_launch(status)
        if isinstance(event, events.Interrupted):
            log.info("Test run is interrupted.")
            self._set_state(HandlerState.INTERRUPTED)
        if isinstance(event, events.InternalError):
            self._terminate_launch("FAILED")
