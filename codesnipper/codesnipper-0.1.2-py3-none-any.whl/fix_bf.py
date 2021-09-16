import functools
from snipper.legacy import gcoms
from snipper.block_parsing import indent
from snipper.block_parsing import block_split, block_join


def fix_f(lines, debug):
    lines2 = []
    i = 0
    while i < len(lines):
        l = lines[i]
        dx = l.find("#!f")
        if dx >= 0:
            l_head = l[dx+3:].strip()
            l = l[:dx]
            lines2.append(l)
            id = indent(lines[i+1])
            for j in range(i+1, 10000):
                jid = len( indent(lines[j]) )
                if  j+1 == len(lines) or ( jid < len(id) and len(lines[j].strip() ) > 0):
                    break

            if len(lines[j-1].strip()) == 0:
                j = j - 1
            funbody = "\n".join( lines[i+1:j] )
            if i == j:
                raise Exception("Empty function body")
            i = j
            comments, funrem = gcoms(funbody)
            comments = [id + c for c in comments]
            if len(comments) > 0:
                lines2 += comments[0].split("\n")
            f = [id + l.strip() for l in funrem.splitlines()]
            f[0] = f[0] + "#!b"
            errm = l_head if len(l_head) > 0 else "Implement function body"
            f[-1] = f[-1] + f' #!b {errm}'
            lines2 += f
        else:
            lines2.append(l)
            i += 1
    return lines2

# stats = {'n': 0}
def _block_fun(lines, start_extra, end_extra, keep=False, silent=False):
    id = indent(lines[0])
    lines = lines[1:] if len(lines[0].strip()) == 0 else lines
    lines = lines[:-1] if len(lines[-1].strip()) == 0 else lines
    cc = len(lines)
    ee = end_extra.strip()
    if len(ee) >= 2 and ee[0] == '"':
        ee = ee[1:-1]
    start_extra = start_extra.strip()
    if keep:
        l2 = ['GARBAGE'] * cc
    else:
        if silent:
            l2 = []
            cc = 0
        else:
            l2 = ([id + start_extra] if len(start_extra) > 0 else []) + [id + f"# TODO: {cc} lines missing.",
                                                                         id + f'raise NotImplementedError("{ee}")']
    return l2, cc

def fix_b(lines, keep=False):
    cutout = []
    n = 0
    while True:
        b = block_split(lines, tag="#!b")
        if b == None:
            break
        args = {k:v for k, v in b['start_tag_args'].items() if len(k) > 0}
        cutout += b['block']
        b['block'], dn = _block_fun(b['block'], start_extra=b['arg1'], end_extra=b['arg2'], **args, keep=keep)
        lines = block_join(b)
        n += dn

    # lines2, _, _, cutout = block_process(lines, tag="#!b", block_fun=functools.partial(block_fun, stats=stats))
    return lines, n, cutout