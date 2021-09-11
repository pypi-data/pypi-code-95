import logging
from mailman2discourse.cmd import Cmd
import pytest


@pytest.mark.parametrize("args,level", [([], logging.WARNING),
                                        (['--verbose'], logging.INFO),
                                        (['--debug'], logging.DEBUG)])
def test_logging(args, level):
    args += [
        '--api-key=KEY', '--url=URL',
        '--list=LIST', '--domain=example.com',
        '--mailman-config=PATH',
    ]
    cmd = Cmd(*args)
    assert cmd.configure_logging() == level
