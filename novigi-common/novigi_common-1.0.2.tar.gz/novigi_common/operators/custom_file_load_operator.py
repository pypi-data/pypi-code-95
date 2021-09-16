from airflow.models.baseoperator import BaseOperator

from airflow.utils.decorators import apply_defaults

from novigi_common.hooks.sample_custom_hook import CustomHook


class CustomFileProcessingOperator(BaseOperator):
    """
        Currently this operator is not doing anything practically.
        We are just taking count of the source file and putting it on XCOM or demo purpose.
        But anyone can add logic to based on hteir reqirement. The configurations are structure will be similar.
    """

    @apply_defaults
    def __init__(
            self,
            name: str,
            *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.name = name

    def execute(self, context):
        message = "Hello {}".format(self.name)
        print(message)
        source_hook = CustomHook()
        return message