import unittest
import pytest
from algobra.engine import Profile


class TestAlgobra(unittest.TestCase):
    def test_engine_profiler_credentials(self):
        """
        Raises a KeyError for non indexed field
        """
        profile_op = Profile()
        with pytest.raises(KeyError) as e_info:
            profile_op.database_credentials["1"] == 1

    def test_engine_profiler_db_defaults(self):
        profile_op = Profile()
        assert (
            profile_op.database_credentials["hostname"]
            == "Please provide database information through Profile::set::methods"
        )

    def test_engine_profiler_db_initialization(self):
        profile_op = Profile()
        profile_op.set_db_hostname("localhost")
        profile_op.set_db_username("sec_user")
        profile_op.set_db_password("password")
        profile_op.set_db_database("securities_master")
        assert profile_op.database_credentials["hostname"] == "localhost"
        assert profile_op.database_credentials["username"] == "sec_user"
        assert profile_op.database_credentials["password"] == "password"
        assert profile_op.database_credentials["database"] == "securities_master"
