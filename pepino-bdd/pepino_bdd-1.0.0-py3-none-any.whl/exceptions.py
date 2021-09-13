class CucumberException(Exception):

    pass


class UnknownStepException(CucumberException):

    def __init__(self, step):
        self.message = f"No '{step.keyword.title()} step defined for '{step.text}' at {step.position}"
        super(UnknownStepException, self).__init__(self.message)
        self._step = step

    def __str__(self):
        return self.message


class CucumberStepException(CucumberException):

    def __init__(self, step: str, location: str):
        self.message = f"Step {step} failed at {location}"

    def __str__(self):
        return self.message


class CucumberTableException(CucumberException):

    def __init__(self, table, message):
        self.message = f"{message} failed at {table.position}"

    def __str__(self):
        return self.message
