import subprocess
import sys
import time
import click

# https://stackoverflow.com/a/3431838
# https://creativecommons.org/licenses/by-sa/4.0/
####
import hashlib
def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
####

def printerr(msg):
    print(msg, file=sys.stderr)

def can_read_file(file_name):
    try:
        with open(file_name, "r") as f:
            pass
    except OSError:
        return False
    return True


@click.command()
@click.argument("filename", type=click.Path(exists=True))
@click.argument("poll_interval_seconds", type=click.INT, default=60)
def cli(poll_interval_seconds, filename):
    try:
        subprocess.run(["git", "init"])
    except CalledProcessError:
        printerr("git init failed!")
        sys.exit(1)
    
    last_md5 = ""
    while True:
        if not can_read_file(filename):
            print(f"File is mising or cant be read at {filename}")
        else:
            value = md5(filename)
            if last_md5 == value:
                print("md5 match, nothing to do")
            else:
                try:
                    subprocess.run(["git", "add", "--", filename])
                    subprocess.run(["git", "commit", "-m", f'"Auto Backup md5 {value}"',
                            "-o", "--", filename])
                    last_md5 = value
                except CalledProcessError:
                    printerr("git commit failed!")
        time.sleep(poll_interval_seconds)



if __name__ == "__main__":
    cli()
