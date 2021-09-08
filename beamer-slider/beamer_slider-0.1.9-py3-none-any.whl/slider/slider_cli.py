import  clize
import os
import sys
import shutil
from slider.slide import set_svg_background_images
import click

def confirm_start_new_project(latexfile, force=False):
    try:
        if force or click.confirm(f"Do you want to create a new Slider LaTeX file named {latexfile}?", abort=True):
            # print("Starting new project")
            from slider.slider_init import slider_init
            slider_init(latexfile)

    except click.exceptions.Abort as e:
        sys.exit()


def slider_cli(latexfile=None, force=False, verbose=False):
    """
    Slider software for manipulating overlay-svg images.
    To get started, first start a slider project by creating a new folder and running

    > python -m slider index.tex

    This will create a bunch of files including a folder named osvgs. This is where you keep the slides!

    When you edit/change overlays, remember to run

    > python -m slider index.tex
    > python -m slider

    to keep everything synchronized.
    You can add new overlays by simply using the LaTeX \osvg{labelname}-tag on new slides (and running slider)
    Edit the overlays by looking in the \osvg-folder, in this case osvg/labelname.svg.

    Remember the overlays by default import the content of the slides (useful if you want to move existing equations around)
    so remember to remove non-wanted contents.
    When done, run slider again to keep everything in sync.

    :param latexfile:
    :param force:
    :param verbose:
    """

    # print("Initializing da slides.")
    wdir = os.getcwd()
    print(wdir)
    if latexfile == None:
        print("Trying to manually detect main latex file.")
        import glob
        files = glob.glob("*.tex")
        mfiles = []
        for name in files:
            with open(name, 'r') as f:
                lines = [l.strip() for l in f.read().splitlines()]
            s = "\n".join([l for l in lines if not l.startswith("%")] )
            if "\\begin{document}" in s and "{beamer}" in s and "_NO_SVGS" not in name:
                print("Main file found!")
                mfiles.append(name)
        if len(mfiles) != 1:
            print("Many candidate files found")
            print(mfiles)
            sys.exit()
        else:
            latexfile = mfiles[0]
        # latexfile = "index.tex"
    if not latexfile.endswith(".tex"):
        latexfile += ".tex"
    latexfile = os.path.join(wdir, latexfile)
    if os.path.exists(latexfile):
        # print("File already exists:", latexfile)
        # print("Doing the slide-stuff.")
        set_svg_background_images(lecture_tex=latexfile)
    else:
        confirm_start_new_project(latexfile=latexfile, force=force)


def clize_main_entry_point():
    """
    I collect this in one function to make a single entry point regardless of where
    > slider
    or
    > python -m slider

    is used.

    :return:
    """
    clize.run(slider_cli)


if __name__ == '__main__':
    clize_main_entry_point()
