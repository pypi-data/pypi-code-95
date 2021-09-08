from datetime import datetime
from unswamp.objects.base.SerializableObject import SerializableObject
from unswamp.objects.base.MetaDataObject import MetaDataObject
from unswamp.objects.core import CheckResult
from unswamp.objects.checks.CheckFunctions import CheckFunctions


class BaseCheck(SerializableObject, MetaDataObject):
    __levels = ["column", "table", "custom"]
    __run_method = "_run"
    id = None
    meta_data = {}
    level = "column"
    active = True
    name = None

    def __init__(self, id, active, level, meta_data):
        MetaDataObject.__init__(self, meta_data)
        self.id = id
        self.active = active
        self.level = level
        self.name = self.__class__.__name__

    def run(self, dataset):
        start = datetime.now()
        passed, message, result = self._run(dataset)
        #TODO: Here we should make a nicer message for the checks with:
        method = getattr(self, "build_expectation_description", None)
        if callable(method):
            exp_desc = self.build_expectation_description(result)
            desc = f"{self.function_description} {exp_desc} {message}"
            message = desc

        #CheckFunctions.get_result_message(self, passed)
        end = datetime.now()
        check_result = CheckResult(self, start, end, passed, message)
        return check_result

    @staticmethod
    def _check(obj):
        if isinstance(obj, BaseCheck):
            if obj.level not in obj.__levels:
                raise ValueError(
                    f"level has value '{obj.level}' but should be one of these values {obj.__levels}!")
            if type(obj.meta_data) is not dict:
                raise ValueError(
                    f"meta_data is of type '{type(obj.meta_data)}' but should be of type dict!")
            if type(obj.active) is not bool:
                raise ValueError(
                    f"active is of type '{type(obj.active)}' but should be of type bool!")
            if not callable(getattr(obj, obj.__run_method, None)):
                raise ValueError(
                    f"object should implement a '{obj.__run_method}' method but it does not!")
        else:
            raise TypeError(
                f"object of type '{type(obj)}' is not of type '{type(BaseCheck)}'!"
            )
