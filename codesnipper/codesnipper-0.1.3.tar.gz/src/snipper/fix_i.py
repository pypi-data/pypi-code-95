import functools
import textwrap
from snipper.legacy import block_process
from snipper.block_parsing import full_strip
import os
if os.name == 'nt':
    import wexpect as we
else:
    import pexpect as we


def run_i(lines, file, output):
    extra = dict(python=None, output=output, evaluated_lines=0)
    def block_fun(lines, start_extra, end_extra, art, head="", tail="", output=None, extra=None):
        outf = output + ("_" + art if art is not None and len(art) > 0 else "") + ".shell"
        lines = full_strip(lines)
        s = "\n".join(lines)
        s.replace("...", "..") # passive-aggressively truncate ... because of #issues.
        lines = textwrap.dedent(s).strip().splitlines()

        if extra['python'] is None:
            an = we.spawn("python", encoding="utf-8", timeout=20)
            an.expect([">>>"])
            extra['python'] = an

        analyzer = extra['python']
        def rsession(analyzer, lines):
            l2 = []
            for i, l in enumerate(lines):
                l2.append(l)
                if l.startswith(" ") and i < len(lines)-1 and not lines[i+1].startswith(" "):
                    if not lines[i+1].strip().startswith("else:") and not lines[i+1].strip().startswith("elif") :
                        l2.append("\n")

            lines = l2
            alines = []
            in_dot_mode = False
            if len(lines[-1]) > 0 and (lines[-1].startswith(" ") or lines[-1].startswith("\t")):
                lines += [""]

            for i, word in enumerate(lines):
                analyzer.sendline(word)
                before = ""
                while True:
                    analyzer.expect_exact([">>>", "..."])
                    before += analyzer.before
                    if analyzer.before.endswith("\n"):
                        break
                    else:
                        before += analyzer.after

                dotmode = analyzer.after == "..."
                if 'dir(s)' in word:
                    pass
                if 'help(s.find)' in word:
                    pass
                if dotmode:
                    alines.append(">>>" + analyzer.before.rstrip() if not in_dot_mode else "..." + analyzer.before.rstrip())
                    in_dot_mode = True
                else:
                    alines.append( ("..." if in_dot_mode else ">>>") + analyzer.before.rstrip())
                    in_dot_mode = False
            return alines

        for l in (head[extra['evaluated_lines']:] + ["\n"]):
            analyzer.sendline(l)
            analyzer.expect_exact([">>>", "..."])


        alines = rsession(analyzer, lines)
        extra['evaluated_lines'] += len(head) + len(lines)
        lines = alines
        return lines, [outf, lines]
    try:
        a,b,c,_ = block_process(lines, tag="#!i", block_fun=functools.partial(block_fun, output=output, extra=extra))
        if extra['python'] is not None:
            extra['python'].close()

        if len(c)>0:
            kvs= { v[0] for v in c}
            for outf in kvs:
                out = "\n".join( ["\n".join(v[1]) for v in c if v[0] == outf] )
                out = out.replace("\r", "")

                with open(outf, 'w') as f:
                    f.write(out)

    except Exception as e:
        print("lines are")
        print("\n".join(lines))
        print("Bad thing in #!i command in file", file)
        raise e
    return lines