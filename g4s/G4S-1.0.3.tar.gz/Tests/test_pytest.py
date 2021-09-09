import os
import g4s

USERNAME: str = os.environ["g4s_username"]
PASSWORD: str = os.environ["g4s_password"]


def test_creation():
    alarm = g4s.Alarm(USERNAME, PASSWORD)
    assert alarm is not None
