import os
import g4s

USERNAME = os.environ.get("g4s_username")
PASSWORD = os.environ.get("g4s_password")


def test_creation():
    alarm = g4s.Alarm(USERNAME, PASSWORD)
    assert alarm is not None
