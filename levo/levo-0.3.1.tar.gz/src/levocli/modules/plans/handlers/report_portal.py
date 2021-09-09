import base64
import enum
import time
import traceback
from typing import Dict, List, Optional, Union

from levo_commons import events
from levo_commons.models import (
    AfterTestExecutionPayload,
    AfterTestSuiteExecutionPayload,
    BeforeTestExecutionPayload,
    BeforeTestSuiteExecutionPayload,
    FinishedPayload,
    Response,
    Status,
    TestResult,
)
from reportportal_client import ReportPortalService

from ....apitesting.runs.api_test_runs_pb2 import (  # type: ignore
    CATEGORY_FAILED,
    CATEGORY_SUCCESS,
    ApiEndpointTestsCategory,
)
from ....env_constants import TEST_RUNS_SERVICE_URL
from ....handlers import EventHandler
from ....logger import get_logger
from ....utils import format_exception
from ...utils import get_formatted_request_response
from ..context import ExecutionContext, TestSuiteExecutionContext

STATUS_DICT = {
    Status.success: "PASSED",
    Status.failure: "FAILED",
    Status.error: "FAILED",
}

log = get_logger(__name__)


def timestamp():
    return str(int(time.time() * 1000))


def handle_before_execution(
    context: ExecutionContext,
    event: events.BeforeTestCaseExecution[BeforeTestExecutionPayload],
    service: ReportPortalService,
) -> None:
    # Test case id here isn't ideal so we need to find what's better.
    message = f"{event.payload.method} {event.payload.relative_path}"
    suite_context = context.test_suite_id_to_context[event.payload.test_suite_id]
    if event.payload.recursion_level > 0:
        message = f"{'    ' * event.payload.recursion_level}-> {message}"
        # This value is not `None` - the value is set in runtime before this line
        suite_context.operations_processed += 1  # type: ignore
    case_attr = {"case_id": event.payload.test_case_id}
    item_id = service.start_test_item(
        name=message,
        description=message,
        start_time=timestamp(),
        item_type="TEST",
        test_case_id=event.payload.test_case_id,
        attributes=case_attr,
    )
    suite_context.test_case_id_to_item_id[event.payload.test_case_id] = item_id
    log.debug(
        "Starting to execute the test case.",
        item_id=item_id,
        test_case_id=event.payload.test_case_id,
        attributes=case_attr,
        endpoint=message,
    )


def handle_after_execution(
    context: ExecutionContext,
    event: events.AfterTestCaseExecution[AfterTestExecutionPayload],
    service: ReportPortalService,
) -> None:
    suite_context = context.test_suite_id_to_context[event.payload.test_suite_id]
    suite_context.operations_processed += 1
    suite_context.results.append(event.payload.result)

    check_summary: Dict[str, ApiEndpointTestsCategory] = {}

    test_item_id = suite_context.test_case_id_to_item_id[event.payload.test_case_id]
    for check in event.payload.result.checks:
        check_item_id = service.start_test_item(
            name=check.name,
            description=f"{check.message}",
            start_time=timestamp(),
            item_type="STEP",
            parent_item_id=test_item_id,
        )
        if check.name not in check_summary:
            check_summary[check.name] = ApiEndpointTestsCategory(
                name=check.name,
                successful_tests=0,
                failed_tests=0,
                duration_millis=0,
                status=CATEGORY_SUCCESS,
            )
        check_summary[check.name].duration_millis += check.duration
        if check.value == Status.success:
            check_summary[check.name].successful_tests += 1
        else:
            check_summary[check.name].failed_tests += 1
        if (
            check.value != Status.success
            and check_summary[check.name].status != CATEGORY_FAILED
        ):
            check_summary[check.name].status = CATEGORY_FAILED
        service.finish_test_item(
            item_id=check_item_id,
            end_time=timestamp(),
            status=STATUS_DICT[check.value],
        )

    test_item_attributes = {
        "elapsed_time": event.payload.elapsed_time,
        "thread-id": event.payload.thread_id,
    }

    for check_name in check_summary:
        test_item_attributes[f"check:{check_name}"] = base64.b64encode(
            check_summary[check_name].SerializeToString()
        ).decode("utf-8")

    service.finish_test_item(
        item_id=test_item_id,
        end_time=timestamp(),
        status=STATUS_DICT[event.payload.status],
        attributes=test_item_attributes,
    )
    log.debug(
        "Finished executing the test case.",
        item_id=test_item_id,
        test_case_id=event.payload.test_case_id,
        attributes=test_item_attributes,
        test_suite_id=suite_context.test_item_id,
    )

    if event.payload.result.has_errors:
        report_log(
            message=get_single_error(context, event.payload.result),
            service=service,
            level="ERROR",
            item_id=test_item_id,
        )
    if event.payload.result.has_failures:
        report_log(
            message=get_failures_for_single_test(context, event.payload.result),
            service=service,
            level="ERROR",
            item_id=test_item_id,
        )

    # Send all the requests and responses of all the steps from the actual test to SaaS.
    if event.payload.result.interactions:
        lines = []
        for interaction in event.payload.result.interactions:
            lines.append(
                get_formatted_request_response(
                    interaction.status,
                    interaction.recorded_at,
                    interaction.request,
                    interaction.response,
                )
            )
        attachment = {
            "name": "request-response-" + test_item_id,
            "data": "\n".join(lines),
            "mime": "text/plain",
        }
        service.log(timestamp(), attachment["name"], attachment=attachment)
        log.debug(
            "Sending the request-response log for test case.",
            item_id=test_item_id,
            attachment=attachment,
        )


def get_single_error(
    context: ExecutionContext,
    result: TestResult,
) -> str:
    lines = [get_subsection(result)]
    for error in result.errors:
        lines.append(_get_error(context, error))
    return "\n".join(lines)


def _get_error(
    context: ExecutionContext,
    exception: Exception,
) -> str:
    return format_exception(exception, context.show_errors_tracebacks)


def get_failures(
    context: ExecutionContext, event: events.Finished[FinishedPayload]
) -> Optional[str]:
    """Get all failures in the test run."""
    if not event.payload.has_failures:
        return None
    relevant_results = [
        result
        for context in context.test_suite_id_to_context.values()
        for result in context.results
        if not result.is_errored
    ]
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
    result: TestResult,
) -> str:
    """Gets a failure for a single method / path."""
    lines = [get_subsection(result)]
    for idx, check in enumerate(result.checks, 1):
        message: Optional[str]
        if check.message:
            message = f"{idx}. {check.message}"
        else:
            message = None
        lines.append(get_example(context, check.response, message))
    return "\n".join(lines)


def get_example(
    context: ExecutionContext,
    response: Optional[Response] = None,
    message: Optional[str] = None,
) -> str:
    lines = []
    if message is not None:
        if not context.verbosity:
            lines.append(message)

    if response is not None and response.body is not None:
        payload = base64.b64decode(response.body).decode(
            response.encoding or "utf8", errors="replace"
        )
        lines.append(f"----------\n\nResponse payload: `{payload}`\n")
    return "\n".join(lines)


def get_subsection(
    result: TestResult,
) -> str:
    return get_section_name(result.verbose_name, "_", result.data_generation_method)


def get_statistic(event: events.Finished[FinishedPayload]) -> str:
    """Format and print statistic collected by :obj:`models.TestResult`."""
    lines = [get_section_name("SUMMARY")]
    total = (
        event.payload.passed_count
        + event.payload.failed_count
        + event.payload.errored_count
    )

    if total:
        lines.append(get_checks_statistics(total))
    else:
        lines.append("No checks were performed.")

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
    return f"{check_name}: {success} / {total} passed"


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
    return message


def get_summary(event: events.Finished[FinishedPayload]) -> str:
    message = get_summary_output(event)
    return get_section_name(message)


def get_summary_message_parts(event: events.Finished[FinishedPayload]) -> List[str]:
    parts = []
    passed = event.payload.passed_count
    if passed:
        parts.append(f"{passed} passed")
    failed = event.payload.failed_count
    if failed:
        parts.append(f"{failed} failed")
    errored = event.payload.errored_count
    if errored:
        parts.append(f"{errored} errored")
    return parts


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
    event: events.Finished[FinishedPayload], service: ReportPortalService
) -> None:
    """Show the outcome of the whole testing session."""
    report_log(get_statistic(event), service)
    report_log(get_summary(event), service)


def report_log(
    message: str, service: ReportPortalService, level="INFO", item_id=None
) -> None:
    if message is None:
        return
    service.log(time=timestamp(), message=message, item_id=item_id, level=level)


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
    log.info(f"Terminated the launch with status: {status}")
    service.terminate()


class HandlerState(enum.Enum):
    """Different states for ReportPortal handler lifecycle."""

    # Instance is created. The default state
    NEW = enum.auto()
    # Launch started, ready to handle events
    ACTIVE = enum.auto()
    # Launch is interrupted, no events will be processed after it
    INTERRUPTED = enum.auto()


def handle_before_suite_execution(
    context: ExecutionContext,
    event: events.BeforeTestSuiteExecution[BeforeTestSuiteExecutionPayload],
    service: ReportPortalService,
) -> None:
    # Start a test suite run in ReportPortal.
    suite_attr = {"suite_id": event.payload.test_suite_id}
    item_id = service.start_test_item(
        name=event.payload.name,
        description=event.payload.name,
        start_time=timestamp(),
        item_type="SUITE",
        attributes=suite_attr,
    )
    # Add a context at the test suite level and record the item id.
    context.test_suite_id_to_context[
        event.payload.test_suite_id
    ] = TestSuiteExecutionContext(test_item_id=item_id)
    log.info(
        "Starting to execute the test suite.",
        suite_id=event.payload.test_suite_id,
        suite_name=event.payload.name,
    )


def handle_after_suite_execution(
    context: ExecutionContext,
    event: events.AfterTestSuiteExecution[AfterTestSuiteExecutionPayload],
    service: ReportPortalService,
) -> None:
    suite_context = context.test_suite_id_to_context[event.payload.test_suite_id]
    if event.payload.errored:
        status = Status.error
    else:
        status = Status.success
        for result in suite_context.results:
            if result.has_failures:
                status = Status.failure
                break

    success_count = 0
    failed_count = 0
    errored_count = 0
    for result in suite_context.results:
        if result.has_errors:
            errored_count += 1
        elif result.has_failures:
            failed_count += 1
        else:
            success_count += 1

    test_item_attributes = {
        "elapsed_time": event.running_time,
        "thread-id": event.payload.thread_id,
        "success_count": success_count,
        "failed_count": failed_count,
        "errored_count": errored_count,
    }
    service.finish_test_item(
        item_id=suite_context.test_item_id,
        end_time=timestamp(),
        status=STATUS_DICT[status],
        attributes=test_item_attributes,
    )
    log.debug(
        "Finished executing the test suite.",
        item_id=suite_context.test_item_id,
        status=status,
        attributes=test_item_attributes,
    )


class TestPlanReportPortalHandler(EventHandler):
    def __init__(self, plan, token):
        self.service = ReportPortalService(
            endpoint=TEST_RUNS_SERVICE_URL, project=plan.workspace_id, token=token
        )
        self.plan = plan
        self.state = HandlerState.NEW

    def _set_state(self, state: HandlerState) -> None:
        self.state = state

    def _terminate_launch(self, status: str) -> None:
        if self.state == HandlerState.ACTIVE:
            terminate_launch(self.service, status)

    def handle_event(self, context: ExecutionContext, event: events.Event) -> None:
        """Reports the test results to ReportPortal service."""
        if isinstance(event, events.Initialized):
            # Create a launch in report portal
            launch_name = self.plan.name
            launch_attr = {
                "plan_lrn": self.plan.lrn,
                "plan_id": event.payload.plan_id,
                "target_url": event.payload.target_url,
            }
            self.service.start_launch(
                name=launch_name,
                start_time=timestamp(),
                description=launch_name,
                attributes=launch_attr,
            )
            self._set_state(HandlerState.ACTIVE)
            log.info(
                "Started the test launch.", name=launch_name, attributes=launch_attr
            )
        if isinstance(event, events.BeforeTestSuiteExecution):
            handle_before_suite_execution(context, event, self.service)
        if isinstance(event, events.AfterTestSuiteExecution):
            handle_after_suite_execution(context, event, self.service)
        if isinstance(event, events.BeforeTestCaseExecution):
            handle_before_execution(context, event, self.service)
        if isinstance(event, events.AfterTestCaseExecution):
            handle_after_execution(context, event, self.service)
        if isinstance(event, events.Finished):
            handle_finished(event, self.service)
            status = {
                HandlerState.ACTIVE: "PASSED",
                HandlerState.INTERRUPTED: "INTERRUPTED",
            }[self.state]
            self._terminate_launch(status)
        if isinstance(event, events.Interrupted):
            self._set_state(HandlerState.INTERRUPTED)
        if isinstance(event, events.InternalError):
            if event.is_terminal:
                self._terminate_launch("FAILED")
            else:
                # Report the test case error to SaaS.
                pass
