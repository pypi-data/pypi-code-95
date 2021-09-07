import unittest

from algobra.engine import Profile


class TestAlgobra(unittest.TestCase):
    def test_engine_initialization(self):
        profile_op = Profile()
        assert (
            profile_op.database_credentials["1"]
            == "Please provide database credentials through set methdos"
        )
