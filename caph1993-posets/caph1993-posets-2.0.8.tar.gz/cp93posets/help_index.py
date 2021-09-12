from __future__ import annotations
from cp93pytools.methodtools import cached_property
import inspect
import re


class HelpIndex:
    '''
    @section
        Help and examples
    '''

    @classmethod
    def help_index(cls, show_all=False, silent=False):
        # Inspect the source code
        src = inspect.getsource(cls)
        re_sect = r'(?:\n *(@section(?:.|[ \n])+?)(?:\'\'\'|\"\"\"))'
        re_meth = r'(?:def +(.*?\( *self.*?\)):)'
        re_cmeth = r'(?:def +(.*?\( *cls.*?\)):)'
        tokens = re.findall('|'.join((re_meth, re_cmeth, re_sect)), src)

        # Group sections and get docs when available
        sections = []
        methodsOf = {}
        section = '(no section)'
        for f, g, sec in tokens:
            f = f or g
            if f:
                methodsOf[section] = methodsOf.get(section, [])
                name = f[:f.index('(')]
                if not hasattr(cls, name):
                    continue
                func = getattr(cls, name)
                doc = func.__doc__ or ''
                doc = '\n'.join(l.strip() for l in doc.split('\n'))
                if isinstance(func, cached_property):
                    full_f = f'@cached_property\ndef {f}:'
                else:
                    full_f = f'def {f}:'
                methodsOf[section].append((full_f, doc))
            else:
                sections.append((section, methodsOf.get(section, [])))
                section = sec.replace('@section', '').strip()
        sections.append((section, methodsOf.get(section, [])))

        # Write a readable output
        out = []
        for i, (sec, methods) in enumerate(sections):
            out.append(f'\n@section {i}. {sec}\n\n')
            for f, docs in methods:
                underscore = f.startswith(
                    'def _') and not f.startswith('def __')
                if show_all or not underscore or (not underscore and docs):
                    f = '\n'.join(' ' * 4 + s for s in f.split('\n'))
                    docs = '\n'.join(' ' * 8 + s for s in docs.split('\n'))
                    out.append(f'{f}\n')
                    out.append(f'{docs}\n')
                    if docs.strip():
                        out.append('\n')
        out = ''.join(out)

        return (sections, out) if silent else print(out)