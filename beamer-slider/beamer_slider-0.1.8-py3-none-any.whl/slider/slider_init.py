#!python
# No, do this instead: https://setuptools.readthedocs.io/en/latest/userguide/entry_point.html
# The above makes the script executable.

import clize
import os
import sys
import shutil

base_slide = """ 
\\documentclass[aspectratio=43]{beamer}
\\usepackage{etoolbox}
\\newtoggle{overlabel_includesvgs}
\\newtoggle{overlabel_includelabels}
\\toggletrue{overlabel_includesvgs}
\\toggletrue{overlabel_includelabels}
\\input{beamer_slider_preamble.tex}

\\title{Example slide show}
\\author{Tue Herlau}
\\begin{document}
\\begin{frame}
\\maketitle
\\end{frame}

\\begin{frame}\\osvg{myoverlay} % Use the \\osvg{labelname} - tag to create new overlays. Run slider and check the ./osvgs directory for the svg files!
\\title{Slide with an overlay}
This is some example text!
\\end{frame}

\\end{document}
"""

def slider_init(latexfile=None):
    # return
    # print("Initializing da slides.")
    wdir = os.getcwd()
    print(wdir)
    if latexfile == None:
        latexfile = "index.tex"
    if not latexfile.endswith(".tex"):
        latexfile += ".tex"
    latexfile = os.path.join(wdir, latexfile)
    if os.path.exists(latexfile):
        print("File already exists", latexfile)
        # sys.exit()
    # Done with the introductory bullshit.

    if not os.path.isdir(os.path.dirname(latexfile)):
        os.makedirs(os.path.dirname(latexfile))

    import jinja2
    with open(latexfile, 'w') as f:
        f.write(base_slide)

    print("Initializing with", latexfile)

    # jinja2.Environment().from_string(base_slide)
    from slider.slide import set_svg_background_images
    set_svg_background_images(latexfile, clean_temporary_files=True)

if __name__ == "__main__":
    # slider_init("../../test/index.tex")
    # from slider.latexutils import latexmk
    # import slider
    clize.run(slider_init)
