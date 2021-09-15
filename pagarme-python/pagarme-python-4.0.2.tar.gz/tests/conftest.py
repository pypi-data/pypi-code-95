import pytest
import tenacity


@pytest.fixture
def retry():
    def is_false(value):
        return not value

    def _retry(func, retry_if_result=is_false, **kwargs):
        kwargs.setdefault('retry', tenacity.retry_if_result(retry_if_result))
        kwargs.setdefault('wait', tenacity.wait_fixed(1))
        kwargs.setdefault('stop', tenacity.stop_after_delay(10))
        decorator = tenacity.retry(**kwargs)
        decorated_func = decorator(func)
        return decorated_func()

    return _retry
