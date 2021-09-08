import os
import pkg_resources  # part of setuptools
from jinjafy import execute_command
import subprocess
from datetime import datetime

bibliography = """
@online{%s,
	title={%s},
	url={%s},
	urldate = {%s}, 
	month={9},
	publisher={Technical University of Denmark (DTU)},
	author={Tue Herlau},
	year={%s},
}
"""
# 	comments={See url{asdfsdaf} for examples},

def make_bibliography(setup_py, outfile=None):
    if not os.path.isfile(setup_py) or os.path.basename(setup_py) != "setup.py":
        raise Exception("No setup.py")

    v = subprocess.check_output(f"cd {os.path.dirname(setup_py)} && python setup.py --name --version --url --description", shell=True).decode("utf-8").splitlines()
    v = [s.strip() for s in v]
    name, version, url, description = v

    ex = "\\texttt{pip install " + name + "}"
    title = f"{name.capitalize()} ({version}): {ex}"
    date = datetime.today().strftime('%Y-%m-%d')
    year = datetime.today().strftime('%Y')

    key = name.replace("-", "_")
    s = (bibliography%(key, title, url, date, year) ).strip()
    if outfile is not None:
        if os.path.isdir(outfile):
            outfile = os.path.join(outfile, name.replace("-",'_') + ".bib")
        with open(outfile, 'w') as f:
            f.write(s)
        print(f"[Writing bibliography with entry '{key}' to]", outfile)

    return s
