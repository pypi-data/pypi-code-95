import logging
import subprocess
import sys
from collections import defaultdict
from typing import Dict, List

import treefiles as tf

from OarLauncher.dumpers import dump_exe, dump_data
from OarLauncher.templates import RUNME_SCRIPT, START_OAR


class ArrayJob:
    # Data = defaultdict(list)  # directly use `defaultdict(list)`

    def __init__(
        self, gen_dir: tf.Tree, data: Dict[str, List[str]], job_path: str = None
    ):
        self.g = gen_dir
        self.data = data
        self.job_path = job_path

        self.setup_files()
        self.nb_jobs = len(next(iter(data.values())))

        self.oar_cmd = None

    def dump(self, python_path: str = ""):
        if python_path != "":
            python_path = f"\nexport PYTHONPATH=$PYTHONPATH:{python_path}\n"

        self.dump_data()
        self.dump_runme(python_path)

        # log.info(f"Files are dumped to file://{self.g.abs()}")

    def run(self) -> str:
        shell_out = subprocess.check_output(self.g.start_oar)
        shell_out = shell_out.decode("utf-8").strip()
        return shell_out  # empty except if `stdout` argument of tf.start_oar is set to None

    def setup_files(self):
        self.g.file(
            start_oar="start_oar.sh",
            array="array_args.txt",
            runme="runme.sh",
            oar="oarsub_res.txt",
        )

    def dump_runme(self, python_path: str):
        runme_script = RUNME_SCRIPT.format(
            activate=tf.Tree(sys.executable).p.path("activate"),
            python_job=self.job_path,
            python_path=python_path,
        )
        dump_exe(self.g.runme, runme_script)

    def build_oar_command(
        self,
        minutes=1,
        hours=0,
        core=1,
        queue=tf.Queue.BESTEFFORT,
        to_file: bool = True,
        job_name: str = None,
    ):
        stdout = self.g.oar if to_file else None
        self.oar_cmd = tf.start_oar(
            self.g.runme,
            prgm=tf.Program.OARCTL,
            logs_dir=self.g.dir("logs").dump(),
            array_fname=self.g.array,
            do_run=False,
            wall_time=tf.walltime(minutes=minutes, hours=hours),
            core=core,
            queue=queue,
            stdout=stdout,  # if None, output of oarsub in returned in <ArrayJob.run>
            job_name=job_name,
        )

        oar_command = START_OAR.format(oar_command=" ".join(self.oar_cmd))
        dump_exe(self.g.start_oar, oar_command)

    def dump_data(self):
        dump_data(self.g.array, self.data)


log = logging.getLogger(__name__)
