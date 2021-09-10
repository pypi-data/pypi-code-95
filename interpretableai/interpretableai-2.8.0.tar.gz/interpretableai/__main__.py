from . import install
import sys

args = [x for x in sys.argv[1:] if '=' not in x]
kwargs = {x.split('=')[0]: x.split('=')[1] for x in sys.argv[1:] if '=' in x}

install(*args, **kwargs)
