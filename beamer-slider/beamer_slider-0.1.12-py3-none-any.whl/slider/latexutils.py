from jinjafy import execute_command
import os
import shutil
import subprocess
import glob

def latexmk(texfile,pdf_out=None,shell=True,cleanup=False, Linux=False):
    cdir = os.getcwd()
    texfile = os.path.abspath(texfile)
    dname = os.path.dirname(texfile)
    os.chdir(dname)
    texfile = os.path.basename(texfile)
    CMD = "latexmk -f -g -pdf -shell-escape -interaction=nonstopmode " + texfile
    print("Running LaTeX command>> " + CMD)

    s = subprocess.check_output(CMD, shell=True)

    # if Linux:
    #     CMD = "latexmk -f -g -pdf -interaction=nonstopmode " + texfile
    #     print("Running LaTeX command>> " + CMD)
    #     s = execute_command(CMD.split(" "), shell=shell)
    # else:
    #     CMD = "latexmk -f -g -pdf -shell-escape -interaction=nonstopmode " + texfile
    #     s = execute_command(CMD.split(" "),shell=shell)
    #
    if pdf_out:
        shutil.copyfile(texfile[:-4]+".pdf", pdf_out)
    else:
        pdf_out = os.path.join(os.path.dirname(texfile), texfile[:-4]+".pdf")

    if cleanup and os.path.exists(pdf_out):
        bft = ['bbl', 'blg', 'fdb_latexmk', 'fls', 'aux', 'synctex.gz', 'log']
        for ex in bft:
            fl = glob.glob(dname + "/*."+ex)
            for f in fl:
                os.remove(f)

    os.chdir(cdir)
    return pdf_out



