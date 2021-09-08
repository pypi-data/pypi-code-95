START_OAR = """
#!/bin/bash

{oar_command}
""".strip()

RUNME_SCRIPT = """
#!/bin/bash

source /etc/profile.d/modules.sh
module load conda/2020.11-python3.8
module load gcc/9.2.0
module load cmake/3.19.6
module load boost/1.58.0

export MPLBACKEND=Agg

source {activate}
{python_path}
python {python_job} $1
""".strip()
