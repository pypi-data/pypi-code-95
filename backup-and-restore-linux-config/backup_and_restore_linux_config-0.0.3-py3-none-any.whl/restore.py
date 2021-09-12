import os
import click
import shutil

from datetime import datetime
from pathlib import Path

from .common import (
    EXCLUDE_FOLDER,
    EXCLUDE_FILE,
    print_diff,
    change_user_path,
    skip_this_user,
)


@click.command(
    help="Copies contents from BACKUP to the root using the actual user. BACKUP should be like a root directory, in other words, it should contain a home folder. SELECTED_USERS should be a list of users present in BACKUP/home and specify which users to copy. When the same file appear in different users, the first has priority."
)
@click.argument("backup", type=click.Path(exists=True))
@click.argument("selected-users", nargs=-1, type=str)
@click.option(
    "--overwritten-output",
    type=click.Path(exists=True),
    #default="./",
    help="folder where backup will be saved. It will create a folder with a timestamp: 'backup_%Y-%m-%d_%H:%M:%S'. Only files that were overwritten will be saved. It default location is the home folder (or the current directory?). This is useful when a disaster occurs after apply the backup",
)
# TODO: in backup this make more sense to be mandatory
@click.option("--dry-run", is_flag=True)
@click.option(
    "--ask-before",
    is_flag=True,
    help="if the file already exists, show the diff and ask whether overwrite.",
)
def main(backup, overwritten_output, selected_users, dry_run, ask_before):
    # def main(**kwargs):
    #    print(kwargs)
    #    quit()

    # Force dryrun when debugging
    #dry_run = True

    # TODO: Check if backup contains "home" folder

    if overwritten_output:
        overwritten_output = Path(overwritten_output) / datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

    assert len(selected_users) > 0

    for directory in Path(backup).glob("**"):
        assert not directory.is_file()

        if any([e in directory.parts for e in EXCLUDE_FOLDER]):
            continue
        for file_src in directory.iterdir():
            if file_src.is_dir():
                continue

            if any([e in file_src.parts for e in EXCLUDE_FILE]):
                continue

            assert file_src.is_file()
            ####################### Handle users #######################

            if skip_this_user(file_src, backup, selected_users):
                continue

            file_dst = Path("/") / file_src.relative_to(backup)
            file_dst = change_user_path(file_dst, os.environ["USER"])

            #############################################################


            if file_dst.is_file():
                if not print_diff(file_dst, file_src):
                    #print("Skipping copy, both files are equal")
                    continue
                if overwritten_output:
                    overwritten_path = overwritten_output / file_dst.relative_to('/')
                    os.makedirs(overwritten_path.parent, exist_ok=True)
                    shutil.copy(file_dst, overwritten_path)
            else:
                print("Copying new file")

            print(f"file_src: {file_src}")
            print(f"file_dst: {file_dst}")

            if not dry_run:
                if ask_before and input("do you want this file (y/n): ") == "n":
                    print("")
                    continue
                if not file_dst.parent.is_dir():
                    print("calling makedirs")
                    # os.makedirs(os.path.dirname(file_dst), exist_ok=True)
                shutil.copy(file_src, file_dst)

            print("")


if __name__ == "__main__":
    main()
