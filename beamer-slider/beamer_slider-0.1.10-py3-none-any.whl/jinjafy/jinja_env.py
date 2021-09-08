import numpy as np
from fractions import Fraction
import jinja2


def format_list_symbols(list, pattern, symbol="x", seperator=",\ "):
    return format_join(list, pattern=symbol+"_{%i}", seperator=seperator)


def n2w(i):
    w = {0: 'zero', 1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight',
         9: 'nine', 10: 'ten'}
    return i if i < 0 or i > 10 else w[i]


def format_list(list_, pattern):
    list_ = tolist(list_)
    return [pattern % s for s in list_]


def format_join(list, pattern, seperator=",\ ",withand=False,withor=False,lastsep=None):
    ls = format_list(list, pattern)
    if withand:
        return seperator.join(ls[:-1]) + "$, and $" + ls[-1]
    if withor:
        return seperator.join(ls[:-1]) + "$, or $" + ls[-1]
    return seperator.join(ls)


def format_join_enum(list, pattern="x_{%i}=%g", seperator=",\ "):
    list = tolist(list)
    return seperator.join(format_list( zip( range(1,len(list)+1 ), list), pattern))


def as_set(l, symbol='f_{%i}'):
    if type(l) != list and type(l) != np.ndarray:
        l = [l]
    l = tolist(l)
    s = [symbol%(i,) for i in l]
    s = '\{' + ", ".join(s) + "\}"
    return s


def as_set_list(ll, symbol='%g'):
    s = []
    for l in ll.flat:
        l = tolist(l)
        s.append(as_set(l, symbol))
    s = ["$"+ds+"$" for ds in s]
    s = ", ".join(s)
    return s


def infty(n,tol=10^8):
    if n > tol:
        s = '\infty'
    else:
        s = str(n)
    return s


def flatten(ar):
    v = []
    if type(ar) is np.ndarray or type(ar) is np.array:
        for x in ar.flat:
            m = flatten(x)
            if type(m) == list:
                v = v + m
            else:
                v.append(m)
    else:
        v = ar
    return v


def tolist(l):
    if type(l) == np.ndarray:
        l2 = []
        for x in l.flat:
            l2.append(  x.tolist() if isinstance(x,np.ndarray) else x  )
        l = l2

    elif type(l) == list or hasattr(l, '__iter__'):
        pass
    else:
        l = [l]
    return l


def jget(A,n=0):
    A = flatten(A)
    return A[n]


def as_rational(x, output='tex', always_frac=False):
    if type(x) == jinja2.runtime.Undefined:
        return "UNDEFINED(jinja2)"
    b = Fraction.from_float(x).limit_denominator(10000)
    s = "output_error_in_as_rational_filter"
    if output == 'tex':
        if (b.denominator == 1 or b.numerator == 0) and not always_frac:
            s = '%i'%b.numerator
        else:
            s = "\\frac{%i}{%i}"%(b.numerator, b.denominator)
    return s


def mylen(l):
    if isinstance(l, np.ndarray):
        sz = l.size
    else:
        sz = len(l)
    return sz


def permute_exam_answers(section,permutation):
    v = section.split("\\item")
    v = v[:5] + v[-1:]
    assert(len(v) == 6)
    permutation = [0] + permutation + [5]
    v[0] = "\\begin{answer}[%i]\n"%permutation.index(1)
    v2 = "\\item".join( [v[i] for i in permutation] )
    return v2


def startswithvowel(value):
    if value.lower().startswith(("a", "e", "i", "o","u")):
        return True
    else:
        return False


def aan(s):
    if s.startswith("no "):
        return ""
    return "an" if startswithvowel(s) else "a"
