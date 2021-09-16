import glob
import os
from tqdm.contrib.concurrent import process_map
import fire
from .util import get_current_date, new_dir

def _map(inputs):
    filename, replace_from, replace_to, command, dry_run = inputs
    new_filename = filename.replace(replace_from, replace_to)
    command = command.replace("{i}", "'" + filename + "'").replace("{o}", "'" + new_filename + "'")
    if new_filename == filename:
        return -1
    if dry_run:
        print(command)
    else:
        new_dir(os.path.dirname(new_filename))
        os.system(command)
    return 0

def batch_map(glob_pattern, command, replace_from, replace_to, j=4, dry_run=False):
    files = glob.glob(glob_pattern, recursive=True)
    if len(files) == 0:
        print("No files", glob_pattern, f"glob.glob({glob_pattern}, recursive=True)")
        return -1
    print(f"yata date:{get_current_date()}, total_files:{len(files)}, dry_run={dry_run}")
    files = [(filename, replace_from, replace_to, command, dry_run) for filename in files]
    process_map(_map, files, max_workers=j, chunksize=100)
    print(f"yata done:{get_current_date()}, total_files:{len(files)}, dry_run={dry_run}")
    return 0


def _glo(glob_pattern):
    glob_pattern = str(glob_pattern)
    files = glob.glob(glob_pattern, recursive=True)
    print(len(files))


def rename():
    print("yata './**/*' --command 'mv {i} {o}' --replace_from .aac --replace_to .wav --j 4 --dry_run True")  

def resample():
    print("yata './**/*' --command 'ffmpeg -hide_banner -loglevel quiet  -i {i} -f wav -ar 16000 -acodec pcm_s16le -ac 1 {o} -y' --replace_from .aac --replace_to .wav --j 10 --dry_run True")


def main():
    fire.Fire(batch_map)
    return 0

def glo():
    fire.Fire(_glo)
    return 0

def guide():
    fire.Fire()
    return 0

# def convert(filepath, save_file_path):
#     # dirname = new_dir(os.path.dirname(save_file_path))
#     command = "ffmpeg -hide_banner -loglevel quiet  -i {} -f wav -ar 16000 -acodec pcm_s16le -ac 1 {} -y".format(filepath, save_file_path)
#     os.system(command)
#     return os.path.exists(save_file_path)


if __name__ == "__main__":
    batch_map("testdir/**/*.wav", "mv {i} {o}", replace_from=".wav", replace_to=".aac", j=4)
