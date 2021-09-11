import json

from pistar_echo_agent.utilities.constants import TEST_SUITE
from pistar_echo_agent.resources.loggers import server_logger
from .base import EchoTestTask

cloud_test_agent = EchoTestTask()


def get_services():
    """
    description: this function is used to import function list
    """

    return [
        heartbeat, send_testcases, clean, stop, get_task_report, get_task_status
    ]


def heartbeat(request_id="Default"):
    """
    description: 用于 cloud test 的心跳检测
    summary: 心跳检测
    arguments:
        request_id:
            type: str
            description: 请求ID
            from: header
    response:
        200:
            content:
                type: dict
                description: 正常响应
            headers:
                request_id:
                    type: str
                    description: 请求 ID
                    example: 6705c301-69fc-4260-acc9-2c4066df0783
    methods:
        - get
    api_path: /v1/health
    status: enable
    """
    return cloud_test_agent.heartbeat(request_id)


def send_testcases(block_id, task_id, sub_task_id, task_name, execute_mode, testcases,
                   testcase_root_path, testcase_type, env_param_config=None, extend_content=""):
    """
    description: |
        该接口cloud test插件调用
        执行器完成解析环境, 解析用例信息, 下载脚本, 脚本执行, 采集结果等事务.
    summary: 下发用例
    arguments:
        block_id:
            type: str
            description: 当前执行用例块id
            from: body
        task_id:
            type: str
            from: body
            description: 任务id
        sub_task_id:
            type: str
            description: 子任务id
            from: body
        task_name:
            type: str
            description: 任务名称
            from: body
        execute_mode:
            type: str
            description: 执行模式
            from: body
        testcases:
            type: list
            description: 用例信息
            from: body
        testcase_root_path:
            type: str
            description: 参数字段
            from: body
        testcase_type:
            type: str
            description: 参数字段
            from: body
        env_param_config:
            type: dict
            description: 参数字段
            from: body
        extend_content:
            type: str
            description: 参数字段
            from: body
    response:
        200:
            content:
                type: dict
                description: 正常响应
        500:
            content:
                type: dict
                description: 错误响应
    api_path: /v1/task/start
    methods:
        - post
    status: enable
    """
    server_logger.info("Receive task start info. {}".format(
        json.dumps({
            TEST_SUITE.BLOCK_ID: block_id,
            TEST_SUITE.TASK_ID: task_id,
            TEST_SUITE.SUB_TASK_ID: sub_task_id,
            TEST_SUITE.TASK_NAME: task_name,
            TEST_SUITE.EXECUTE_MODE: execute_mode,
            TEST_SUITE.TESTCASES: testcases,
            TEST_SUITE.TESTCASE_ROOT_PATH: testcase_root_path,
            TEST_SUITE.EXTEND_CONTENT: extend_content,
            TEST_SUITE.TYPE: testcase_type,
            TEST_SUITE.ENVIRONMENT_PARAMS: env_param_config
        })))
    cur_task_info = {
        TEST_SUITE.BLOCK_ID: block_id,
        TEST_SUITE.TASK_ID: task_id,
        TEST_SUITE.SUB_TASK_ID: sub_task_id,
        TEST_SUITE.TASK_NAME: task_name,
        TEST_SUITE.EXECUTE_MODE: execute_mode,
        TEST_SUITE.EXTEND_CONTENT: extend_content,
        TEST_SUITE.TESTCASE_ROOT_PATH: testcase_root_path,
        TEST_SUITE.TYPE: testcase_type,
        TEST_SUITE.ENVIRONMENT_PARAMS: env_param_config
    }
    return cloud_test_agent.send_testcases(cur_task_info, testcases)


def clean(block_id):
    """
    description: 该接口由cloud test插件调用，初始化执行机.
    summary: 初始化执行机，清理环境
    arguments:
        block_id:
            type: str
            from: query
            description: body 字段
    response:
        200:
            content:
                type: dict
                description: 正常响应
            headers:
                request_id:
                    type: str
                    description: 请求 ID
                    example: 6705c301-69fc-4260-acc9-2c4066df0783
        500:
            content:
                type: dict
                description: 正常响应
            headers:
                request_id:
                    type: str
                    example: 6705c301-69fc-4260-acc9-2c4066df0783
    api_path: /v1/task/clean
    methods:
        - get
    status: enable
    """
    server_logger.info("Receive clean environment info.")
    return cloud_test_agent.clean(block_id)


def stop(block_id, task_id, sub_task_id, task_name):
    """
    description: 该接口由 cloud test 调用, cloud test 暂停执行机.
    summary: 结束用例块
    arguments:
        block_id:
            type: str
            description: body 字段
            from: body
        task_id:
            type: str
            from: body
            description: body 字段
        sub_task_id:
            type: str
            description: body 字段
            from: body
        task_name:
            type: dict
            from: body
            description: body 字段
    response:
        200:
            content:
                type: dict
                description: 正常响应
        500:
            content:
                type: dict
                description: 正常响应
    api_path: /v1/task/stop
    methods:
        - post
    status: enable
    """
    server_logger.info("Receive block:{} task_name:{} stop task info.".format(block_id, task_name))
    return cloud_test_agent.stop(block_id)


def get_task_status(block_id, task_id, sub_task_id):
    """
    description: 该接口由 cloud test 调用, 获取用例集的执行状态.
    summary: 结束用例块
    arguments:
        block_id:
            type: str
            description: body 字段
            from: body
        task_id:
            type: str
            from: body
            description: body 字段
        sub_task_id:
            type: str
            description: body 字段
            from: body
    response:
        200:
            content:
                type: dict
                description: 正常响应
        500:
            content:
                type: dict
                description: 正常响应
    api_path: /v1/task/status
    methods:
        - post
    status: enable
    """
    server_logger.info("Receive block:{} get task status info.".format(block_id))
    return cloud_test_agent.get_task_status(block_id)


def get_task_report(block_id, task_id, sub_task_id, testcase_ids):
    """
    description: 该接口由 cloud test 调用, cloud test 获取指定用例的报告.
    summary: 结束用例块
    arguments:
        block_id:
            type: str
            description: body 字段
            from: body
        task_id:
            type: str
            from: body
            description: body 字段
        sub_task_id:
            type: str
            description: body 字段
            from: body
        testcase_ids:
            type: list
            from: body
            description: body 字段
    response:
        200:
            content:
                type: dict
                description: 正常响应
        500:
            content:
                type: dict
                description: 正常响应
    api_path: /v1/task/report
    methods:
        - post
    status: enable
    """
    server_logger.info("Receive block:{} get test cases {} report info.".format(block_id, testcase_ids))
    return cloud_test_agent.get_task_report(block_id, testcase_ids)
