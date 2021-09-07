class Error(Exception):
    pass


class TargetPairError(Error):
    def __init__(self, target_pair):
        self.target_pair = target_pair

    def __str__(self):
        return f"ERROR: '{self.target_pair}' not a valid target pair or format"


class ParameterRequiredError(Error):
    def __init__(self, params):
        self.params = params

    def __str__(self):
        return "{} is mandatory, but received empty.".format(", ".join(self.params))
