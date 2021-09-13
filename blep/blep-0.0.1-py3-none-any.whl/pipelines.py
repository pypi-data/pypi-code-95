# Pre-defined pipelines
from shutil import copy as copy_file

from .core import File, Website


def copy(web: Website, files: list[File]):
	for file in files:
		origin = web.input_path / file.path
		target = web.output_path / file.path
		if not target.parent.is_dir():
			target.parent.mkdir(parents=True)
		copy_file(origin, target)
