from airflow.plugins_manager import AirflowPlugin
from operators.custom_file_load_operator import CustomFileProcessingOperator
from hooks.sample_custom_hook import CustomHook


# Defining the plugin class
class CustomPlugin(AirflowPlugin):
    name = "custom_plugin"
    operators = [CustomFileProcessingOperator]
    hooks = [CustomHook]