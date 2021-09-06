# import iictl
from iictl.commands.main import cli

def entrypoint():
    cli(obj={})
    
if __name__ == '__main__':
    entrypoint()