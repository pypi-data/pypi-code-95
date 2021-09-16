import codecs
import lzma
import pathlib
import shutil
import subprocess
import urllib.request
from os import path, makedirs
from tempfile import _get_candidate_names
from urllib.parse import urlparse
from zipfile import ZipFile


def copy_file_with_dir_creation(src_filepath, dest_filepath):
	makedirs(get_dir_path(dest_filepath), exist_ok=True)
	shutil.copyfile(src_filepath, dest_filepath)


def read_file(file_path):
	with codecs.open(file_path, 'r', 'utf-8') as f:
		return f.read()


def run_cmd(cmd):
	subprocess.Popen(
		cmd,
		shell=True,
		encoding='utf8',
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE)


def delete_folder(folder_path):
	shutil.rmtree(folder_path)


def check_output(cmd):
	proc = subprocess.run(
		cmd,
		shell=True,
		check=False,
		encoding='utf8',
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE)

	if proc.returncode != 0:
		raise Exception(
			"Run command `{0}` failed, stderr=`{1}`, stdout=`{2}`, returncode=`{3}`"
				.format(cmd, proc.stderr, proc.stdout, proc.returncode))

	return proc.stdout.strip()


def get_filename_from_url(url):
	return path.basename(urlparse(url).path)


def invert_dict(d):
	return {v: k for k, v in d.items()}


def download_from_url(file_url, dest_file_path):
	with urllib.request.urlopen(file_url) as response, open(dest_file_path,
	                                                        'wb') as out_file:
		shutil.copyfileobj(response, out_file)
	return dest_file_path


def get_temp_name():
	return next(_get_candidate_names())


def get_dir_path(file_path):
	return pathlib.Path(file_path).parent.resolve()


def get_filename(file_path, with_extension=True):
	filename = path.basename(file_path)

	if not with_extension:
		filename = remove_extension(filename)

	return filename


def remove_extension(filepath):
	return path.splitext(filepath)[0]


def extract_xz_file(xzfile_path, dest_file_path=None):
	if not dest_file_path:
		dest_file_path = remove_extension(xzfile_path)

	with lzma.open(xzfile_path) as f, open(dest_file_path, 'wb') as fout:
		file_content = f.read()
		fout.write(file_content)

	return dest_file_path


def extract_zip_file(zipfile_path, dest_dir_path):
	with ZipFile(zipfile_path, 'r') as zipObj:
		# Extract all the contents of zip file in current directory
		zipObj.extractall(dest_dir_path)

	return dest_dir_path
