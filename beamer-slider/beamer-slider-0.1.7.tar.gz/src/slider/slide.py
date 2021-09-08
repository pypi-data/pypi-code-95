#!python
# The above makes the script executable.

import slider.legacy_importer
import PyPDF2
import os
from jinjafy import execute_command
# from slider import slide
from slider import legacy_importer
from slider.legacy_importer import SVG_EDIT_RELPATH, SVG_TMP_RELPATH, move_template_files, DTU_beamer_base, svg_edit_to_importable
from jinjafy.cache import cache_update_str, cache_contains_str, cache_contains_file, cache_update_file
import shutil
from slider.slide_fixer import check_svg_file_and_fix_if_broken
from slider.latexutils import latexmk
import clize
import glob

dc = "\\documentclass"

def fix_handout(s):
    i = s.find(dc) + len(dc)
    j1 = s.find('[', i)
    j2 = s.find("{", i)
    if 0 < j1 < j2:
        s = s[:j1 + 1] + "handout," + s[j1 + 1:]
    else:
        s = s[:j2 + 1] + "[handout]" + s[j2 + 1:]
    return s

def set_svg_background_images(lecture_tex, verbose=False,
                              fix_broken_osvg_files=False,
                              recompile_on_change=True,
                              clean_temporary_files=False,
                              copy_template_resource_files=True,
                              force_recompile=False,
                              force_fix_broken_osvg_files = None,
                              ):
    '''
    Main file for fixing/setting osvg background images in the given lecture .pdf.
    Usage:

    > slider <text-file-to-convert>

    :param lecture_tex: File to set background image in.
    :return:
    '''
    MAIN_TEX_DIR = os.path.dirname(lecture_tex)
    SVG_TMP_DIR = MAIN_TEX_DIR + "/" + SVG_EDIT_RELPATH + "/" + SVG_TMP_RELPATH
    SVG_OSVG_DIR = MAIN_TEX_DIR + "/" + SVG_EDIT_RELPATH
    force_fix_broken_osvg_files = [] if force_fix_broken_osvg_files is None else force_fix_broken_osvg_files

    print("Slider is setting the background images for the .tex. file\n>  %s" % os.path.abspath(lecture_tex))
    if copy_template_resource_files:
        move_template_files(output_dir=MAIN_TEX_DIR, output_tex_file=None)
    if not os.path.exists(lecture_tex):
        # move a basic .tex file to this location and proceed
        shutil.copyfile(DTU_beamer_base +"/dtu_slideshow_base.tex", lecture_tex)

    ANY_CHANGES = True
    tex = recursive_tex_apply(lecture_tex)
    tex = "\n".join([tex[k] for k in tex])
    all_tex = tex
    tex = tex.splitlines()

    ol = "\\osvg"
    tex = [s.strip() for s in tex if ol in s and "@ifnextchar" not in s and "%" not in s[:s.find(ol)]] # exclude definition of osvg command
    sinfo = {}

    for s in tex:
        i = s.find(ol) + len(ol)
        if s[i] == "[": i = s.find("]", i)
        i = s.find("{", i)
        ie = s.find("}", i)
        if ie == -1: continue
        s = s[i+1:ie]
        ii = all_tex.find(s)
        frame_start = all_tex.rfind("\\begin{frame}", 0, ii)
        frame_end = all_tex.find("\\end{frame}", ii, len(all_tex))

        cs = all_tex[frame_start:frame_end]
        d = {"pdf_label": s, "svg_edit_file": MAIN_TEX_DIR + "/" + SVG_EDIT_RELPATH + "/" + s + ".svg", 'slide_tex': cs}
        sinfo[s] = d
        # print(d)

    if not os.path.exists(MAIN_TEX_DIR + "/" + SVG_EDIT_RELPATH):
        os.mkdir(MAIN_TEX_DIR + "/" + SVG_EDIT_RELPATH)
    # Prepare alternative .tex file; compile with handout and watermarks for later reference.
    lecture_tex_nosvg = lecture_tex[:-4] + "_NO_SVGS.tex"
    with open(lecture_tex, "r") as f:
        s = f.read()

    if s.find(dc) < 0:
        # find and fix the import
        dc2 = "\\input{"
        j1 = s.find(dc2)+len(dc2)
        j2 = s.find(dc2) + s.find("}", s.find(dc2))
        fhead = MAIN_TEX_DIR + "/" + s[j1:j2]+".tex"
        with open(fhead, 'r') as f:
            sh = f.read()
            sh = fix_handout(sh)
            with open(fhead, 'w') as f2:
                f2.write(sh)
    else:
        s = fix_handout(s)

    i = s.find("\\begin{document}")
    ii = s.rfind("\n", i - 10, i)
    s = s[:ii] + "\n \\togglefalse{overlabel_includesvgs}\n\\toggletrue{overlabel_includelabels}\n" + s[ii:]

    with open(lecture_tex_nosvg, "w") as f:
        f.write(s)

    lecture_tex_nosvg_pdf = lecture_tex_nosvg[:-4] + ".pdf"

    # lecture_tex_nosvg_tex = recursive_tex_apply(lecture_tex_nosvg)

    if cache_contains_str(MAIN_TEX_DIR, key='all_tex', value=all_tex) and os.path.exists(lecture_tex_nosvg_pdf):
        print("slider> Cache contains nosvg tex file")
    else:
        cdir = os.getcwd()
        os.chdir(os.path.dirname(lecture_tex_nosvg))
        execute_command(("latexmk -shell-escape -f -pdf -interaction=nonstopmode " + os.path.basename(lecture_tex_nosvg)).split(" "))
        os.chdir(cdir)
        cache_update_file(MAIN_TEX_DIR, lecture_tex_nosvg)
        ANY_CHANGES = True

    # Make .png background images.
    with open(lecture_tex_nosvg_pdf, 'rb') as f:
        pdfdoc = PyPDF2.PdfFileReader(f)
        for i in range(pdfdoc.getNumPages()):
            content = pdfdoc.getPage(i).extractText()
            for osvg_name, d in sinfo.items(): #enumerate(sinfo):

                if d['pdf_label'] in content:
                    d['pdf_page'] = i
                    d['png_bgimg'] = SVG_TMP_DIR + "/" + d['pdf_label'] + ".png"
                    if not os.path.exists(d['svg_edit_file']):
                        '''
                        Found \osvg{myslide}, but myslide.svg does not exist. Re-create it from the original slide.
                        '''
                        print("Failed to find editable file: %s. Re-creating from snapshot..."%d['svg_edit_file'])
                        tmp_svg_file = "%s/%s/%s"%(os.path.dirname(d['svg_edit_file']),
                                                   SVG_TMP_RELPATH,
                                                   os.path.basename(d['svg_edit_file']))
                        tmp_svg_file = legacy_importer.slide_to_image(lecture_tex_nosvg_pdf, tmp_svg_file, i + 1)
                        legacy_importer.raw_svg_to_osvg(tmp_svg_file, overwrite_existing=True)
                        ANY_CHANGES = True

                    if cache_contains_str(MAIN_TEX_DIR, key=d['pdf_label'], value=d['slide_tex']):
                        # print("slider> Cache contains slide tex; continuing: " + d['pdf_label'] )
                        continue
                    legacy_importer.slide_to_image(lecture_tex_nosvg_pdf, d['png_bgimg'], i + 1)
                    ANY_CHANGES = True
                    cache_update_str(MAIN_TEX_DIR, key=d['pdf_label'], value=d['slide_tex'])


    # This is the step that actually fixes the svg files. i.e. squeeze fonts, etc.
    for osvg_name, d in sinfo.items():
        if (osvg_name+".svg") not in force_fix_broken_osvg_files:
            if cache_contains_file(MAIN_TEX_DIR, d['svg_edit_file']) and not force_recompile:
                continue
        '''        
        Check if the svg image pass sanity checks: Does it exist and is it okay?                
        '''
        if fix_broken_osvg_files:
            check_svg_file_and_fix_if_broken(d['svg_edit_file'], verbose=verbose)

        legacy_importer.svg_edit_to_importable(d['svg_edit_file'], verbose=verbose)
        # legacy_importer.svg_check_background_layer(d['svg_edit_file'], verbose=verbose) # This was an old check for BG img.
        cache_update_file(MAIN_TEX_DIR, d['svg_edit_file'])
        ANY_CHANGES = True

    if ANY_CHANGES and recompile_on_change:

        latexmk(lecture_tex)

    if clean_temporary_files:
        if verbose:
            print("> SlideConverter: Removing temporary dirs...")
        # raise Exception()
        DNE = SVG_OSVG_DIR + "/do_not_edit"
        if os.path.exists(SVG_TMP_DIR):
            for v in glob.glob(SVG_TMP_DIR + "/*"):
                if not v.endswith("png"):
                    os.remove(v)

        if os.path.exists(DNE):
            for v in glob.glob(DNE + "/*"):
                if not v.endswith("png"):
                    os.remove(v)

def slide_no_by_text(pdf_file, text):
    assert False
    # Make .png background images.
    if os.path.exists(pdf_file):
        with open(pdf_file, 'rb') as f:
            print(pdf_file)
            pdfdoc = PyPDF2.PdfFileReader(f)
            for i in range(pdfdoc.getNumPages()):
                content = pdfdoc.getPage(i).extractText()
                # for j, d in enumerate(sinfo):
                if text in content:
                    return i+1
    else:
        print("Warning: slide.py() -> slide_no_by_text(): PDF file not found " + pdf_file)
    return -1
    # raise Exception()

def recursive_tex_apply(doc, fun=None, current_output=None):
    if not fun:
        def mfun(curdoc, txt, cur_out):
            if not cur_out: cur_out = dict()
            cur_out[curdoc] = txt
            return cur_out

        fun = mfun
    if os.path.exists(doc):
        def rfile(doc, encoding):
            with open(doc, 'r', encoding=encoding) as f:
                tex = f.read()
            return tex
        try:
            tex = rfile(doc, encoding="utf-8")
        except Exception as e:
            print("Problem reading file", doc)
            print(e)
            import glob
            from chardet.universaldetector import UniversalDetector
            detector = UniversalDetector()
            detector.reset()
            with open(doc, 'rb') as f:
                detector.feed(f.read())
            detector.close()
            res = detector.result['encoding']
            print("Detecting encoding with chardet...")
            print(res)
            tex = rfile(doc, encoding=detector.result['encoding'])

        current_output = fun(doc, tex, current_output)
        for s in tex.splitlines():
            fs = '\\input{'
            if fs in s and not s.strip().startswith("%"):
                j = s.find(fs)
                rec_file = s[j + len(fs):s.find("}", j)]
                if os.path.isabs(rec_file):
                    rec_file_tex = rec_file
                else:
                    rec_file_tex = os.path.dirname(doc) + "/" + rec_file
                    if not rec_file_tex.endswith(".tex"):
                        rec_file_tex += ".tex"

                current_output = recursive_tex_apply(rec_file_tex, fun, current_output)
    return current_output

def recursive_tex_collect(doc):
    assert False
    sdict = recursive_tex_apply(doc)
    def gathersub(file):
        lines = []
        if file not in sdict:
            print(sdict)
            raise Exception("Bad error occured in split lines " + file )
        for s in sdict[file].splitlines():
            fs = '\\input{'
            if fs in s and not s.strip().startswith("%"):
                j = s.find(fs)
                rec_file = s[j + len(fs):s.find("}", j)]
                if os.path.isabs(rec_file):
                    rec_file_tex = rec_file
                else:
                    rec_file_tex = os.path.dirname(file) + "/" + rec_file
                    if not rec_file_tex.endswith(".tex"):
                        rec_file_tex += ".tex"

                lines += gathersub(rec_file_tex)
            else:
                lines.append(s)
        return lines

    lines = gathersub(doc)
    return "\n".join(lines)

