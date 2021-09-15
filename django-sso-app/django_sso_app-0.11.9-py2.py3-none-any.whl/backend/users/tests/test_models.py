import pytest

from django_sso_app.backend.users.models import User

pytestmark = pytest.mark.django_db


def test_user_get_relative_url(user: User):
    assert user.get_relative_url() == f"/users/{user.username}/"
