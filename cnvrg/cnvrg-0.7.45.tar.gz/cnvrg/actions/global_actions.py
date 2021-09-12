import os
import click
import shutil
def check_if_path_exists(path):
    if os.path.exists(path):
        if not click.confirm('Cnvrg will override {project} Do you want to continue?'.format(project=path)):
            return
        else:
            shutil.rmtree(path, ignore_errors=True)