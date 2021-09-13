import sys
from functools import reduce
from pathlib import Path, PurePath
from queue import Queue, Empty
from shutil import rmtree
from typing import Union

# Applying typing definition from aiohttp
if sys.version_info >= (3, 6):
	PathLike = Union[str, "os.PathLike[str]"]
else:
	PathLike = Union[str, PurePath]
# Other custom typings
Patterns = dict[str, str]
Pipelines = dict[str, list]


class File:
	path: Path  # This is the path relative to the website root. It can be an input file, an output file, etc.
	kind: str
	metadata: dict
	raw: str

	def __init__(self, path: Path, kind: str, metadata=None, raw: str = ''):
		if metadata is None:
			metadata = {}
		self.path = path
		self.kind = kind
		self.metadata = metadata
		self.raw = raw


class Job:
	files: list[File]
	pipeline: list

	def __init__(self, files: list[File], pipeline: list):
		self.files = files
		self.pipeline = pipeline


class JobQueue(Queue):
	def __iter__(self):
		while True:
			try:
				yield self.get(block=False)
			except Empty:
				break


class Website:
	job_queue: JobQueue = JobQueue()
	build_prepared: bool = False

	input_path: Path
	output_path: Path

	patterns: Patterns
	pipelines: Pipelines

	title: str
	author: str
	base_url: str

	def __init__(
		self,
		blog_path: PathLike, input_dir: PathLike, output_dir: PathLike,
		patterns: Patterns, pipelines: Pipelines,
		title: str, author: str, base_url: str):
		blog_path = Path(blog_path).expanduser()
		self.input_path = blog_path / input_dir
		self.output_path = blog_path / output_dir

		self.patterns = patterns
		self.pipelines = pipelines

		self.title = title
		self.author = author
		self.base_url = base_url

	def reset(self):
		if self.output_path.exists():
			rmtree(self.output_path)

	def enqueue(self, jobs: list[Job]):
		for job in jobs:
			self.job_queue.put(job)

	def execute_pipeline(self, pipeline: list, files: list[File]):
		reduce(lambda f, action: action(self, files), pipeline, files)

	def prepare(self):
		if self.build_prepared:
			return
		self.reset()
		for file in self.input_path.rglob('*'):
			if file.suffix in self.patterns:
				kind = self.patterns[file.suffix]
				pipeline = self.pipelines[kind]

				self.enqueue([Job([File(file.relative_to(self.input_path), kind)], pipeline)])
		self.build_prepared = True

	def build(self):
		self.prepare()
		for job in self.job_queue:
			self.execute_pipeline(job.pipeline, job.files)
			self.job_queue.task_done()
