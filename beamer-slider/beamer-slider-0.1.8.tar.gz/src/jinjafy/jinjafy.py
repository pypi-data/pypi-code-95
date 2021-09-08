import inspect
import jinja2
from math import floor, log10
import os
import numpy as np
from jinjafy import jinja_env


def jinjafy_template(data,file_in,file_out=None, filters={},template_searchpath=None):
    if template_searchpath:
        file_in = os.path.relpath(file_in, template_searchpath)

    return jinjafy_comment(data, file_in=file_in, file_out=file_out,jinja_tag=None, filters=filters,template_searchpath=template_searchpath)


def jinjafy_comment(data,file_in=None,file_out=None,jinja_tag="jinja",jinja_code=None,trim_whitespace=True,trim_comments=True,comment_char="#",
                    filters={},template_searchpath=None):
    # Extract all comments from the given file and jinjafy them.
    if file_in is None:
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        file_in = module.__file__
    elif not jinja_tag:
        trim_comments=False
        trim_whitespace=False

    if not template_searchpath:
        with open(file_in,'r') as f:
            s = f.read()
            if jinja_tag:
                stag = "<" + jinja_tag + ">"
                etag = "</" + jinja_tag + ">"

                i_start = s.find(stag)
                i_end = s.find(etag)
                s = s[i_start+len(stag):i_end]
            ss = [s]
            if trim_comments:
                ss = [ds.strip()[1:] for ds in s.splitlines() if len(ds.strip()) > 0 and ds.strip()[0] in ["#", "%"] ]
            if trim_whitespace:
                ss = [ds.strip() for ds in ss]

            jinja_code = '\n'.join(ss)

    from jinjafy.snipper import SnipperExtension
    extensions = [SnipperExtension]
    if template_searchpath:
        if not isinstance(template_searchpath, list):
            template_searchpath = [template_searchpath]
        template_searchpath = [ts.replace("\\", "/") for ts in template_searchpath]
        templateLoader = jinja2.FileSystemLoader(searchpath=template_searchpath)
        env = jinja2.Environment(lstrip_blocks=True, trim_blocks=True,loader=templateLoader, extensions=extensions)
    else:
        env = jinja2.Environment(lstrip_blocks=True, trim_blocks=True, extensions=extensions)

    import math
    env.globals['exp'] = math.exp
    env.globals['sqrt'] = math.sqrt
    env.globals['cos'] = math.cos
    env.globals['sin'] = math.sin

    env.globals['mround'] = mround
    env.globals['bold'] = bold
    env.globals['fmat'] = fmat
    env.globals['enumerate'] = enumerate
    env.globals['zip'] = zip
    env.globals['ensure_numpy'] = ensure_numpy
    env.globals['transpose'] = transpose
    import math
    env.globals['ceil'] = math.ceil
    env.globals['floor'] = math.floor


    from pylatexenc import latexencode
    env.globals['utf8tolatex'] = latexencode.utf8tolatex
    env.globals['as_set'] = jinja_env.as_set
    env.globals['as_set_list'] = jinja_env.as_set_list
    env.globals['len'] = jinja_env.mylen
    env.globals['get'] = jinja_env.jget
    env.globals['tolist'] = jinja_env.tolist

    filters['as_set'] =  jinja_env.as_set
    filters['format_list'] =jinja_env.format_list
    filters['format_join'] = jinja_env.format_join
    filters['format_join_enum'] = jinja_env.format_join_enum
    filters['pm'] = lambda x: f" {x}" if x < 0 else f"+{x}"
    filters['bold'] = bold
    filters['capfirst'] = lambda x: (x[0].upper() + x[1:] if len(x) > 1 else x.upper()) if x != None and isinstance(x, str) else x
    filters['lowerfirst'] = lambda x: (x[0].lower() + x[1:] if len(x) > 1 else x.lower()) if x != None and isinstance(x, str) else x
    filters['infty'] = jinja_env.infty
    filters['n2w'] = jinja_env.n2w
    def latex_url(url):
        if not isinstance(url, str):
            return url
        url = url.replace("%", r"\%")
        return url
    filters['latex_url'] = latex_url
    filters['format_list_symbols'] = jinja_env.format_list_symbols
    filters['mround'] = mround
    def eround(val,l):
        x = str(mround(val, l))
        if l == 0:
            return x
        if '.' not in x:
            x = x + "."
        n = l - (len(x) - x.find(".") - 1)
        if n > 0:
            x = x + "0"*n
        return x

    filters['eround'] = eround
    filters['get'] = jinja_env.jget
    filters['flatten'] = jinja_env.flatten
    filters['aan'] = jinja_env.aan
    filters['bracket'] = bracket
    filters['tolist'] = jinja_env.tolist
    filters['rational'] = jinja_env.as_rational
    filters['permute_exam_answers'] = jinja_env.permute_exam_answers
    env.filters.update(filters)

    data['block_start_string'] = '{%'
    if not template_searchpath:
        jinja_out = env.from_string(jinja_code).render(data)
    else:
        file_in = file_in.replace("\\", "/")
        template = env.get_template(file_in)
        jinja_out = template.render(data)

    if file_out is not None:
        with open(file_out,'w',encoding='utf-8') as f:
            # jinja_out = jinja_out.encode('utf-8')

            f.write(jinja_out)
            print("Writing to: " + file_out)

    return jinja_out


def bold(bob,d=True) :
    if not isinstance(bob, str) :
        bob = str(bob)
    if d :
        bob = '\\textbf{' + bob +"}"
    return bob


def fmat(bob,l=2,dobold=False) :
    bob = mround(bob,l)
    bob = bold(bob, dobold)
    return bob

def bracket(s):
    return "{"+str(s)+"}"

def un2str(x, xe, precision=2):
    """pretty print nominal value and uncertainty

        x  - nominal value
        xe - uncertainty
        precision - number of significant digits in uncertainty

        returns shortest string representation of `x +- xe` either as
        x.xx(ee)e+xx
        or as
        xxx.xx(ee)"""
    # base 10 exponents
    x_exp = int(floor(log10(x)))
    xe_exp = int(floor(log10(xe)))

    # uncertainty
    un_exp = xe_exp - precision + 1
    un_int = round(xe * 10 ** (-un_exp))

    # nominal value
    no_exp = un_exp
    no_int = round(x * 10 ** (-no_exp))

    # format - nom(unc)exp
    fieldw = x_exp - no_exp
    fmt = '%%.%df' % fieldw
    result1 = (fmt + '(%.0f)e%d') % (no_int * 10 ** (-fieldw), un_int, x_exp)

    # format - nom(unc)
    fieldw = max(0, -no_exp)
    fmt = '%%.%df' % fieldw
    result2 = (fmt + '(%.0f)') % (no_int * 10 ** no_exp, un_int * 10 ** max(0, un_exp))

    # return shortest representation
    if len(result2) <= len(result1):
        return result2
    else:
        return result1


def mround(val, l=2):
    if not isinstance(l, int):
        return un2str(val, l, 1)
    else:
        if isinstance(val, np.ndarray):
            return np.round(val * 10 ** l) / (10 ** l)
        else:
            return round(val * 10 ** l) / (10 ** l)


def transpose(X):
    return np.transpose( ensure_numpy( X) )


def ensure_numpy(X):
    if type(X) != np.ndarray:
        X = np.asarray(X)
    if X.ndim == 1:
        X = np.transpose( np.expand_dims(X,1) )
    return X