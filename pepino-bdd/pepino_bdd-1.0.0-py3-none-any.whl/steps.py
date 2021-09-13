import threading
from .registry import registry
from .enums import Step


class AbstractStep:

    def __init__(self, pattrn, registry=registry):
        self._pattern = pattrn
        self._registry = registry

    def __call__(self, func, *args, **kwargs):
        def wrapped(*args, **kwargs):
            func(*args, **kwargs)

        thread = threading.Thread(
            target=self._registry.add_step,
            args=(self._pattern, func),
            daemon=True,
        )
        thread.start()
        return func


class given(AbstractStep):  # noqa

    __name__ = Step.GIVEN


class when(AbstractStep):  # noqa

    __name__ = Step.WHEN


class then(AbstractStep):  # noqa

    __name__ = Step.THEN


class but(AbstractStep):  # noqa

    __name__ = Step.BUT
