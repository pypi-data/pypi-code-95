from snipper.load_citations import find_tex_cite
from snipper.legacy import COMMENT


def fix_citations(lines, references, strict=True):
    lines = fix_aux(lines, aux=references.get('aux', {}) )
    for cm in references.get('commands', []):
        lines = fix_aux_special(lines, aux=cm['aux'], command=cm['command'], output=cm['output'])

    lines = fix_bibtex(lines, bibtex=references.get('bibtex', {}))
    return lines


def fix_aux_special(lines, aux, command='\\nref', output='\cite[%s]{my_bibtex_entry}'):
    # out = output %
    daux = {name: {'nicelabel': output % v['nicelabel'] } for name, v in aux.items()}
    l2 = fix_single_reference(lines, aux=daux, cmd=command, strict=True)
    return l2

def fix_aux(lines, aux, strict=True):
    l2 = fix_single_reference(lines, aux=aux, cmd="\\ref", strict=True)
    # print("\n".join(l2))
    return l2

def fix_bibtex(lines, bibtex):
    s = "\n".join(lines)
    i = 0
    all_refs = []
    while True:
        (i, j), reference, txt = find_tex_cite(s, start=i, key="\\cite")
        if i < 0:
            break
        if reference not in bibtex:
            raise IndexError("no such reference: " + reference)
        ref = bibtex[reference]
        label = ref['label']
        rtxt = f"({label}" + (", "+txt if txt is not None else "") + ")"
        r = ref['plain']
        if r not in all_refs:
            all_refs.append(r)
        s = s[:i] + rtxt + s[j+1:]
        i = i + len(rtxt)

    if len(all_refs) > 0:
        if not s.startswith(COMMENT):
            s = f"{COMMENT}\n{COMMENT}\n" + s
        i = s.find(COMMENT, s.find(COMMENT)+1)
        all_refs = ["  " + r.strip() for r in all_refs]
        s = s[:i] + "References:\n" + "\n".join(all_refs) +"\n"+ s[i:]

    # s = s.replace(cpr, info['code_copyright'])
    return s.splitlines()

# def fix_references(lines, info, strict=True):
#     assert False
#     for cmd in info['new_references']:
#         lines = fix_single_reference(lines, cmd, info['new_references'][cmd], strict=strict)
#     return lines

def fix_single_reference(lines, cmd, aux, strict=True):
    references = aux
    s = "\n".join(lines)
    i = 0
    while True:
        (i, j), reference, txt = find_tex_cite(s, start=i, key=cmd)
        if i < 0:
            break
        if reference not in references:
            er = "cref label not found for label: " + reference
            if strict:
                raise IndexError(er)
            else:
                print(er)
                continue
        r = references[reference]
        rtxt = r['nicelabel']
        s = s[:i] + rtxt + s[j + 1:]
        i = i + len(rtxt)
        print(cmd, rtxt)

    lines = s.splitlines(keepends=False)
    return lines