from .descriptor import Descriptor


# Typed
class Typed(Descriptor):
    expected_type = type(None)

    def __set__(self, instance, value):
        if not isinstance(value, self.expected_type):
            raise TypeError("expected {!r}".format(self.expected_type))

        super().__set__(instance, value)


# GenericTyped
class GenericTyped(Descriptor):
    def __init__(self, name=None, **opts):
        super().__init__(name, **opts)

        if "type" not in opts:
            raise ValueError("keyword-only argument 'type' must be passed")
        self.expected_type = opts["type"]

    def __set__(self, instance, value):
        if not isinstance(value, self.expected_type):
            raise TypeError("expected {!r}".format(self.expected_type))

        super().__set__(instance, value)
