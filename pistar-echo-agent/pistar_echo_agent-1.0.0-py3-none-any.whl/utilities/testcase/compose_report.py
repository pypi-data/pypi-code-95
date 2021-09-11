import os
import json
import time

from pistar_echo_agent.utilities.constants import FILE_MODE
from pistar_echo_agent.utilities.constants import ENCODE
from pistar_echo_agent.utilities.constants import REPORT
from pistar_echo_agent.utilities.constants import TEST_SUITE
from pistar_echo_agent.utilities.constants import Result
from pistar_echo_agent.resources.loggers import server_logger


def compose_report_json(task_info, testcase_id, script_path, report_path):
    report = {
        TEST_SUITE.BLOCK_ID: task_info[TEST_SUITE.BLOCK_ID],
        TEST_SUITE.TASK_ID: task_info[TEST_SUITE.TASK_ID],
        TEST_SUITE.SUB_TASK_ID: task_info[TEST_SUITE.SUB_TASK_ID]
    }
    # 读取finished.json,读入各个属性
    finished_json = os.path.join(report_path, REPORT.FINISHED_JSON)
    try:
        with open(
                finished_json, mode=FILE_MODE.READ, encoding=ENCODE.UTF8
        ) as json_file:
            content = json.load(json_file)
            report[REPORT.RESULT] = content[REPORT.RESULT]
            report[REPORT.START_TIME] = content[REPORT.START_TIME]
            report[REPORT.END_TIME] = content[REPORT.END_TIME]
            report[REPORT.DURATION] = content[REPORT.DURATION]
    except Exception as ex:
        current_time = int(time.time() * 1000)
        report[REPORT.RESULT] = 1
        report[REPORT.START_TIME] = current_time
        report[REPORT.END_TIME] = current_time
        report[REPORT.DURATION] = 0
        server_logger.error(ex)
        server_logger.error("{} json file have some error, please check.".format(finished_json))

    report[REPORT.TESTCASE_ID] = testcase_id
    report[REPORT.SCRIPT_PATH] = script_path
    report[REPORT.DETAILS] = compose_report_details(report_path)

    return report


def compose_exception_report(task_info, testcase_id, script_path, reason):
    current_time = int(time.time() * 1000)
    report = {
        TEST_SUITE.BLOCK_ID: task_info[TEST_SUITE.BLOCK_ID],
        TEST_SUITE.TASK_ID: task_info[TEST_SUITE.TASK_ID],
        TEST_SUITE.SUB_TASK_ID: task_info[TEST_SUITE.SUB_TASK_ID],
        REPORT.RESULT: Result.ERROR.value,
        REPORT.ERROR_REASON: reason,
        REPORT.START_TIME: current_time,
        REPORT.END_TIME: current_time,
        REPORT.DURATION: 0,
        REPORT.TESTCASE_ID: testcase_id,
        REPORT.SCRIPT_PATH: script_path,
        REPORT.DETAILS: []
    }

    return report


def compose_report_details(report_path):
    details = []
    if not os.path.exists(report_path):
        return details
    files = os.listdir(report_path)
    for file in files:
        if file.endswith("result.json") and not file == REPORT.FINISHED_JSON:
            json_path = os.path.join(report_path, file)
            try:
                with open(
                        json_path, mode=FILE_MODE.READ, encoding=ENCODE.UTF8
                ) as json_file:
                    content = json.load(json_file)
                    for attribute in REPORT.USELESS_ATTRIBUTE:
                        if attribute in content:
                            content.pop(attribute)
                    # 将处理后的内容放入content
                    details.append(content)
            except Exception as ex:
                server_logger.error(ex)
                server_logger.error("{} json file have some error, please check.".format(json_path))

    # 将details进行排序
    details = sorted(details, key=lambda k: k["start_time"])
    return details
