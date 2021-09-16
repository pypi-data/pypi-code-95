import os
import re

from snipper.block_parsing import full_strip
from snipper.fix_i import run_i
from snipper.fix_r import fix_r
from snipper.fix_s import save_s
from snipper.fix_cite import fix_citations
from snipper.fix_bf import fix_f, fix_b
from snipper.fix_o import run_o


def rem_nonprintable_ctrl_chars(txt):
    """Remove non_printable ascii control characters """
    try:
        txt = re.sub(r'[^\x20-\x7E|\x09-\x0A]','', txt)
        # remove non-ascii characters
        txt = repr(txt).decode('unicode_escape').encode('ascii','ignore')[1:-1]
    except Exception as exception:
        print(exception)
    return txt


def censor_code(lines, keep=True):
    dbug = True
    lines = fix_f(lines, dbug)
    lines, nB, cut = fix_b(lines, keep=True)
    return lines



def censor_file(file, run_files=True, run_out_dirs=None, cut_files=True, solution_list=None,
                censor_files=True,
                base_path=None,
                strict=True,
                references=None,
                license_head=None):

    if references == None:
        references = {}

    dbug = False
    with open(file, 'r', encoding='utf8') as f:
        s = f.read()
        s = s.lstrip()
        lines = s.split("\n")
        for k, l in enumerate(lines):
            if l.find(" # !") > 0:
                print(f"{file}:{k}> bad snipper tag, fixing")
            lines[k] = l.replace("# !", "#!")

        try:
            lines = fix_citations(lines, references, strict=strict)
        except IndexError as e:
            print(e)
            print("Error in file, cite/reference tag not found!>", file)
            raise e

        if (run_files or cut_files) and run_out_dirs is not None:
            ofiles = []
            for rod in [run_out_dirs]:
                ofiles.append(os.path.join(rod, os.path.basename(file).split(".")[0]) )
            ofiles[0] = ofiles[0].replace("\\", "/")

            if run_files:
                run_o(lines, file=file, output=ofiles[0])
                run_i(lines, file=file, output=ofiles[0])
            if cut_files:
                save_s(lines, file_path=os.path.relpath(file, base_path), output_dir=run_out_dirs)  # save file snips to disk
        lines = full_strip(lines, ["#!s", "#!o", '#!i'])

        if censor_files:
            lines = fix_f(lines, dbug)
            lines, nB, cut = fix_b(lines)
        else:
            nB = 0
        lines = fix_r(lines)

        if censor_files and len(cut) > 0 and solution_list is not None:
            fname = file.__str__()
            i = fname.find("irlc")
            # wk = fname[i+5:fname.find("\\", i+6)]
            # sp = paths['02450students'] +"/solutions/"
            # if not os.path.exists(sp):
            #     os.mkdir(sp)
            # sp = sp + wk
            # if not os.path.exists(sp):
            #     os.mkdir(sp)
            sols = []
            stext = ["\n".join(lines) for lines in cut]
            for i,sol in enumerate(stext):
                sols.append( (sol,) )
                # sout = sp + f"/{os.path.basename(fname)[:-3]}_TODO_{i+1}.py"
                # wsol = any([True for s in solution_list if os.path.basename(sout).startswith(s)])
                # print(sout, "(published)" if wsol else "")
                # if wsol:
                #     with open(sout, "w") as f:
                #         f.write(sol)

        if len(lines) > 0 and len(lines[-1])>0:
            lines.append("")
        s2 = "\n".join(lines)

    if license_head is not None:
        s2 = fix_copyright(s2, license_head)


    with open(file, 'w', encoding='utf-8') as f:
        f.write(s2)
    return nB


def fix_copyright(s, license_head):
    return "\n".join( ["# " + l.strip() for l in license_head.splitlines()] ) +"\n" + s

# lines: 294, 399, 420, 116