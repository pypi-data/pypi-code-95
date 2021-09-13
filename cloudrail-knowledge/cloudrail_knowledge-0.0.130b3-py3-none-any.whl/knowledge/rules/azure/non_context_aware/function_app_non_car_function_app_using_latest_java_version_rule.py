from typing import List, Dict
from cloudrail.knowledge.context.azure.azure_environment_context import AzureEnvironmentContext
from cloudrail.knowledge.rules.azure.azure_base_rule import AzureBaseRule
from cloudrail.knowledge.rules.base_rule import Issue
from cloudrail.knowledge.rules.rule_parameters.base_paramerter import ParameterType


class FunctionAppUsingLatestJavaVersionRule(AzureBaseRule):

    def get_id(self) -> str:
        return 'non_car_function_app_using_latest_java_version'

    def execute(self, env_context: AzureEnvironmentContext, parameters: Dict[ParameterType, any]) -> List[Issue]:
        issues: List[Issue] = []
        for func_app in env_context.function_apps:
            function_worker, version = _get_function_worker(func_app.app_service_config.linux_fx_version, func_app.app_service_config.java_version)
            if function_worker == 'java' and version != '11':
                issues.append(
                    Issue(
                        f'The {func_app.get_type()} `{func_app.get_friendly_name()}` does not use the latest Azure supported Java version (11).',
                        func_app,
                        func_app))
        return issues

    def should_run_rule(self, environment_context: AzureEnvironmentContext) -> bool:
        return bool(environment_context.function_apps)


def _get_function_worker(linux_fx_version, java_version):
    function_worker = None
    version = None
    if linux_fx_version:
        if linux_fx_version.split('|')[0] == 'JAVA':
            function_worker = 'java'
            version = linux_fx_version.split('|')[1]
    elif java_version:
        function_worker = 'java'
        version = java_version
    return function_worker, version
