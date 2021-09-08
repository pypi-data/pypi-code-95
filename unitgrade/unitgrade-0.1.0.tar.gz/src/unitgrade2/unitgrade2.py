"""
git add . && git commit -m "Options" && git push &&  pip install git+ssh://git@gitlab.compute.dtu.dk/tuhe/unitgrade.git --upgrade
"""
import numpy as np
import sys
import re
import threading
import tqdm
import pickle
import os
from io import StringIO
import io
from unittest.runner import _WritelnDecorator
from typing import Any
import inspect
import textwrap
import colorama
from colorama import Fore
from functools import _make_key, RLock
from collections import namedtuple
import unittest
import time
import textwrap

_CacheInfo = namedtuple("CacheInfo", ["hits", "misses", "maxsize", "currsize"])

colorama.init(autoreset=True)  # auto resets your settings after every output

def gprint(s):
    print(f"{Fore.GREEN}{s}")

myround = lambda x: np.round(x)  # required.
msum = lambda x: sum(x)
mfloor = lambda x: np.floor(x)


def setup_dir_by_class(C, base_dir):
    name = C.__class__.__name__
    return base_dir, name


class Logger(object):
    def __init__(self, buffer):
        assert False
        self.terminal = sys.stdout
        self.log = buffer

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        # this flush method is needed for python 3 compatibility.
        pass


class Capturing(list):
    def __init__(self, *args, stdout=None, unmute=False, **kwargs):
        self._stdout = stdout
        self.unmute = unmute
        super().__init__(*args, **kwargs)

    def __enter__(self, capture_errors=True):  # don't put arguments here.
        self._stdout = sys.stdout if self._stdout == None else self._stdout
        self._stringio = StringIO()
        if self.unmute:
            sys.stdout = Logger(self._stringio)
        else:
            sys.stdout = self._stringio

        if capture_errors:
            self._sterr = sys.stderr
            sys.sterr = StringIO()  # memory hole it
        self.capture_errors = capture_errors
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio  # free up some memory
        sys.stdout = self._stdout
        if self.capture_errors:
            sys.sterr = self._sterr


class Capturing2(Capturing):
    def __exit__(self, *args):
        lines = self._stringio.getvalue().splitlines()
        txt = "\n".join(lines)
        numbers = extract_numbers(txt)
        self.extend(lines)
        del self._stringio  # free up some memory
        sys.stdout = self._stdout
        if self.capture_errors:
            sys.sterr = self._sterr

        self.output = txt
        self.numbers = numbers


# @classmethod
# class OrderedClassMembers(type):
#     def __prepare__(self, name, bases):
#         assert False
#         return collections.OrderedDict()
#
#     def __new__(self, name, bases, classdict):
#         ks = list(classdict.keys())
#         for b in bases:
#             ks += b.__ordered__
#         classdict['__ordered__'] = [key for key in ks if key not in ('__module__', '__qualname__')]
#         return type.__new__(self, name, bases, classdict)


class Report:
    title = "report title"
    version = None
    questions = []
    pack_imports = []
    individual_imports = []
    nL = 120  # Maximum line width

    @classmethod
    def reset(cls):
        for (q, _) in cls.questions:
            if hasattr(q, 'reset'):
                q.reset()

    @classmethod
    def mfile(clc):
        return inspect.getfile(clc)

    def _file(self):
        return inspect.getfile(type(self))

    def _import_base_relative(self):
        if hasattr(self.pack_imports[0], '__path__'):
            root_dir = self.pack_imports[0].__path__._path[0]
        else:
            root_dir = self.pack_imports[0].__file__

        root_dir = os.path.dirname(root_dir)
        relative_path = os.path.relpath(self._file(), root_dir)
        modules = os.path.normpath(relative_path[:-3]).split(os.sep)
        return root_dir, relative_path, modules

    def __init__(self, strict=False, payload=None):
        working_directory = os.path.abspath(os.path.dirname(self._file()))
        self.wdir, self.name = setup_dir_by_class(self, working_directory)
        # self.computed_answers_file = os.path.join(self.wdir, self.name + "_resources_do_not_hand_in.dat")
        for (q, _) in self.questions:
            q.nL = self.nL  # Set maximum line length.

        if payload is not None:
            self.set_payload(payload, strict=strict)

    def main(self, verbosity=1):
        # Run all tests using standard unittest (nothing fancy).
        loader = unittest.TestLoader()
        for q, _ in self.questions:
            start = time.time()  # A good proxy for setup time is to
            suite = loader.loadTestsFromTestCase(q)
            unittest.TextTestRunner(verbosity=verbosity).run(suite)
            total = time.time() - start
            q.time = total

    def _setup_answers(self, with_coverage=False):
        if with_coverage:
            for q, _ in self.questions:
                q._with_coverage = True
                q._report = self

        self.main()  # Run all tests in class just to get that out of the way...
        report_cache = {}
        for q, _ in self.questions:
            # print(self.questions)
            if hasattr(q, '_save_cache'):
                q()._save_cache()
                print("q is", q())
                q()._cache_put('time', q.time) # = q.time
                report_cache[q.__qualname__] = q._cache2
            else:
                report_cache[q.__qualname__] = {'no cache see _setup_answers in unitgrade2.py': True}
        if with_coverage:
            for q, _ in self.questions:
                q._with_coverage = False
        return report_cache

    def set_payload(self, payloads, strict=False):
        for q, _ in self.questions:
            q._cache = payloads[q.__qualname__]


def rm_progress_bar(txt):
    # More robust version. Apparently length of bar can depend on various factors, so check for order of symbols.
    nlines = []
    for l in txt.splitlines():
        pct = l.find("%")
        ql = False
        if pct > 0:
            i = l.find("|", pct + 1)
            if i > 0 and l.find("|", i + 1) > 0:
                ql = True
        if not ql:
            nlines.append(l)
    return "\n".join(nlines)


def extract_numbers(txt):
    # txt = rm_progress_bar(txt)
    numeric_const_pattern = r'[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'
    rx = re.compile(numeric_const_pattern, re.VERBOSE)
    all = rx.findall(txt)
    all = [float(a) if ('.' in a or "e" in a) else int(a) for a in all]
    if len(all) > 500:
        print(txt)
        raise Exception("unitgrade.unitgrade.py: Warning, too many numbers!", len(all))
    return all


class ActiveProgress():
    def __init__(self, t, start=True, title="my progress bar", show_progress_bar=True, file=None):
        if file == None:
            file = sys.stdout
        self.file = file
        self.t = t
        self._running = False
        self.title = title
        self.dt = 0.01
        self.n = int(np.round(self.t / self.dt))
        self.show_progress_bar = show_progress_bar
        self.pbar = None

        if start:
            self.start()

    def start(self):
        self._running = True
        if self.show_progress_bar:
            self.thread = threading.Thread(target=self.run)
            self.thread.start()
        self.time_started = time.time()

    def terminate(self):
        if not self._running:
            raise Exception("Stopping a stopped progress bar. ")
        self._running = False
        if self.show_progress_bar:
            self.thread.join()
        if self.pbar is not None:
            self.pbar.update(1)
            self.pbar.close()
            self.pbar = None

        self.file.flush()
        return time.time() - self.time_started

    def run(self):
        self.pbar = tqdm.tqdm(total=self.n, file=self.file, position=0, leave=False, desc=self.title, ncols=100,
                              bar_format='{l_bar}{bar}| [{elapsed}<{remaining}]')

        for _ in range(self.n - 1):  # Don't terminate completely; leave bar at 99% done until terminate.
            if not self._running:
                self.pbar.close()
                self.pbar = None
                break

            time.sleep(self.dt)
            self.pbar.update(1)

def dprint(first, last, nL, extra = "", file=None, dotsym='.', color='white'):
    if file == None:
        file = sys.stdout

    # ss = self.item_title_print
    # state = "PASS" if success else "FAILED"
    dot_parts = (dotsym * max(0, nL - len(last) - len(first)))
    # if self.show_progress_bar or True:
    print(first + dot_parts, end="", file=file)
    # else:
    # print(dot_parts, end="", file=self.cc.file)
    last += extra
    # if tsecs >= 0.5:
    #     state += " (" + str(tsecs) + " seconds)"
    print(last, file=file)


class UTextResult(unittest.TextTestResult):
    nL = 80
    number = -1  # HAcky way to set question number.
    show_progress_bar = True
    cc = None

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.successes = []

    def printErrors(self) -> None:
        self.printErrorList('ERROR', self.errors)
        self.printErrorList('FAIL', self.failures)

    def addError(self, test, err):
        super(unittest.TextTestResult, self).addFailure(test, err)
        self.cc_terminate(success=False)

    def addFailure(self, test, err):
        super(unittest.TextTestResult, self).addFailure(test, err)
        self.cc_terminate(success=False)

    def addSuccess(self, test: unittest.case.TestCase) -> None:
        self.successes.append(test)
        self.cc_terminate()

    def cc_terminate(self, success=True):
        if self.show_progress_bar or True:
            tsecs = np.round(self.cc.terminate(), 2)
            self.cc.file.flush()
            ss = self.item_title_print

            state = "PASS" if success else "FAILED"

            dot_parts = ('.' * max(0, self.nL - len(state) - len(ss)))
            if self.show_progress_bar or True:
                print(self.item_title_print + dot_parts, end="", file=self.cc.file)
            else:
                print(dot_parts, end="", file=self.cc.file)

            if tsecs >= 0.5:
                state += " (" + str(tsecs) + " seconds)"
            print(state, file=self.cc.file)

    def startTest(self, test):
        # j =self.testsRun
        self.testsRun += 1
        # item_title = self.getDescription(test)
        item_title = test.shortDescription()  # Better for printing (get from cache).
        if item_title == None:
            # For unittest framework where getDescription may return None.
            item_title = self.getDescription(test)
        self.item_title_print = " * q%i.%i) %s" % (UTextResult.number + 1, self.testsRun, item_title)
        estimated_time = 10
        if self.show_progress_bar or True:
            self.cc = ActiveProgress(t=estimated_time, title=self.item_title_print, show_progress_bar=self.show_progress_bar, file=sys.stdout)
        else:
            print(self.item_title_print + ('.' * max(0, self.nL - 4 - len(self.item_title_print))), end="")

        self._test = test
        self._stdout = sys.stdout
        sys.stdout = io.StringIO()

    def stopTest(self, test):
        sys.stdout = self._stdout
        super().stopTest(test)

    def _setupStdout(self):
        if self._previousTestClass == None:
            total_estimated_time = 1
            if hasattr(self.__class__, 'q_title_print'):
                q_title_print = self.__class__.q_title_print
            else:
                q_title_print = "<unnamed test. See unitgrade.py>"

            cc = ActiveProgress(t=total_estimated_time, title=q_title_print, show_progress_bar=self.show_progress_bar)
            self.cc = cc

    def _restoreStdout(self):  # Used when setting up the test.
        if self._previousTestClass is None:
            q_time = self.cc.terminate()
            q_time = np.round(q_time, 2)
            sys.stdout.flush()
            if self.show_progress_bar:
                print(self.cc.title, end="")
            print(" " * max(0, self.nL - len(self.cc.title)) + (" (" + str(q_time) + " seconds)" if q_time >= 0.5 else ""))


class UTextTestRunner(unittest.TextTestRunner):
    def __init__(self, *args, **kwargs):
        stream = io.StringIO()
        super().__init__(*args, stream=stream, **kwargs)

    def _makeResult(self):
        # stream = self.stream # not you!
        stream = sys.stdout
        stream = _WritelnDecorator(stream)
        return self.resultclass(stream, self.descriptions, self.verbosity)


def cache(foo, typed=False):
    """ Magic cache wrapper
    https://github.com/python/cpython/blob/main/Lib/functools.py
    """
    maxsize = None
    def wrapper(self, *args, **kwargs):
        key = (self.cache_id(), ("@cache", foo.__name__, _make_key(args, kwargs, typed)))
        if not self._cache_contains(key):
            value = foo(self, *args, **kwargs)
            self._cache_put(key, value)
        else:
            value = self._cache_get(key)
        return value

    return wrapper


def get_hints(ss):
    if ss == None:
        return None
    try:
        ss = textwrap.dedent(ss)
        ss = ss.replace('''"""''', "").strip()
        hints = ["hints:", "hint:"]
        j = np.argmax([ss.lower().find(h) for h in hints])
        h = hints[j]
        ss = ss[ss.lower().find(h) + len(h) + 1:]
        ss = "\n".join([l for l in ss.split("\n") if not l.strip().startswith(":")])
        ss = textwrap.dedent(ss)
        ss = ss.strip()
        return ss
    except Exception as e:
        print("bad hints", ss, e)


class UTestCase(unittest.TestCase):
    _outcome = None  # A dictionary which stores the user-computed outcomes of all the tests. This differs from the cache.
    _cache = None  # Read-only cache. Ensures method always produce same result.
    _cache2 = None  # User-written cache.
    _with_coverage = False
    _report = None  # The report used. This is very, very hacky and should always be None. Don't rely on it!

    def capture(self):
        if hasattr(self, '_stdout') and self._stdout is not None:
            file = self._stdout
        else:
            # self._stdout = sys.stdout
            # sys._stdout = io.StringIO()
            file = sys.stdout
        return Capturing2(stdout=file)

    @classmethod
    def question_title(cls):
        """ Return the question title """
        return cls.__doc__.strip().splitlines()[0].strip() if cls.__doc__ is not None else cls.__qualname__

    @classmethod
    def reset(cls):
        print("Warning, I am not sure UTestCase.reset() is needed anymore and it seems very hacky.")
        cls._outcome = None
        cls._cache = None
        cls._cache2 = None

    def _callSetUp(self):
        if self._with_coverage:
            if not hasattr(self._report, 'covcache'):
                self._report.covcache = {}
            import coverage
            self.cov = coverage.Coverage()
            self.cov.start()
        self.setUp()

    def _callTearDown(self):
        self.tearDown()
        if self._with_coverage:
            from pathlib import Path
            from snipper import snipper_main
            self.cov.stop()
            data = self.cov.get_data()
            base, _, _ = self._report._import_base_relative()
            for file in data.measured_files():
                file = os.path.normpath(file)
                root = Path(base)
                child = Path(file)
                if root in child.parents:
                    with open(child, 'r') as f:
                        s = f.read()
                    lines = s.splitlines()
                    garb = 'GARBAGE'

                    lines2 = snipper_main.censor_code(lines, keep=True)
                    assert len(lines) == len(lines2)

                    for l in data.contexts_by_lineno(file):
                        if lines2[l].strip() == garb:
                            if self.cache_id() not in self._report.covcache:
                                self._report.covcache[self.cache_id()] = {}

                            rel = os.path.relpath(child, root)
                            cc = self._report.covcache[self.cache_id()]
                            j = 0
                            for j in range(l, -1, -1):
                                if "def" in lines2[j] or "class" in lines2[j]:
                                    break
                            from snipper.legacy import gcoms
                            fun = lines2[j]
                            comments, _ = gcoms("\n".join(lines2[j:l]))
                            if rel not in cc:
                                cc[rel] = {}
                            cc[rel][fun] = (l, "\n".join(comments))
                            self._cache_put((self.cache_id(), 'coverage'), self._report.covcache)

    def shortDescriptionStandard(self):
        sd = super().shortDescription()
        if sd is None:
            sd = self._testMethodName
        return sd

    def shortDescription(self):
        sd = self.shortDescriptionStandard()
        title = self._cache_get((self.cache_id(), 'title'), sd)
        return title if title is not None else sd

    @property
    def title(self):
        return self.shortDescription()

    @title.setter
    def title(self, value):
        self._cache_put((self.cache_id(), 'title'), value)

    def _get_outcome(self):
        if not (self.__class__, '_outcome') or self.__class__._outcome is None:
            self.__class__._outcome = {}
        return self.__class__._outcome

    def _callTestMethod(self, testMethod):
        t = time.time()
        self._ensure_cache_exists()  # Make sure cache is there.
        if self._testMethodDoc is not None:
            self._cache_put((self.cache_id(), 'title'), self.shortDescriptionStandard())

        self._cache2[(self.cache_id(), 'assert')] = {}
        res = testMethod()
        elapsed = time.time() - t
        self._get_outcome()[self.cache_id()] = res
        self._cache_put((self.cache_id(), "time"), elapsed)

    def cache_id(self):
        c = self.__class__.__qualname__
        m = self._testMethodName
        return c, m

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._load_cache()
        self._assert_cache_index = 0

    def _ensure_cache_exists(self):
        if not hasattr(self.__class__, '_cache') or self.__class__._cache == None:
            self.__class__._cache = dict()
        if not hasattr(self.__class__, '_cache2') or self.__class__._cache2 == None:
            self.__class__._cache2 = dict()

    def _cache_get(self, key, default=None):
        self._ensure_cache_exists()
        return self.__class__._cache.get(key, default)

    def _cache_put(self, key, value):
        self._ensure_cache_exists()
        self.__class__._cache2[key] = value

    def _cache_contains(self, key):
        self._ensure_cache_exists()
        return key in self.__class__._cache

    def wrap_assert(self, assert_fun, first, *args, **kwargs):
        # sys.stdout = self._stdout
        key = (self.cache_id(), 'assert')
        if not self._cache_contains(key):
            print("Warning, framework missing", key)
            self.__class__._cache[
                key] = {}  # A new dict. We manually insert it because we have to use that the dict is mutable.
        cache = self._cache_get(key)
        id = self._assert_cache_index
        if not id in cache:
            print("Warning, framework missing cache index", key, "id =", id)
        _expected = cache.get(id, f"Key {id} not found in cache; framework files missing. Please run deploy()")

        # The order of these calls is important. If the method assert fails, we should still store the correct result in cache.
        cache[id] = first
        self._cache_put(key, cache)
        self._assert_cache_index += 1
        assert_fun(first, _expected, *args, **kwargs)

    def assertEqualC(self, first: Any, msg: Any = ...) -> None:
        self.wrap_assert(self.assertEqual, first, msg)

    def _cache_file(self):
        # The filename-directory stuff is a bit tricky but this seems robust.
        return os.path.dirname(inspect.getabsfile(type(self))) + "/unitgrade/" + self.__class__.__name__ + ".pkl"

    def _save_cache(self):
        # get the class name (i.e. what to save to).
        cfile = self._cache_file()
        if not os.path.isdir(os.path.dirname(cfile)):
            os.makedirs(os.path.dirname(cfile))

        if hasattr(self.__class__, '_cache2'):
            with open(cfile, 'wb') as f:
                pickle.dump(self.__class__._cache2, f)

    # But you can also set cache explicitly.
    def _load_cache(self):
        if self._cache is not None:  # Cache already loaded. We will not load it twice.
            return
            # raise Exception("Loaded cache which was already set. What is going on?!")
        cfile = self._cache_file()
        if os.path.exists(cfile):
            try:
                # print("\ncache file", cfile)
                with open(cfile, 'rb') as f:
                    data = pickle.load(f)
                self.__class__._cache = data
            except Exception as e:
                print("Bad cache", cfile)
                print(e)
        else:
            print("Warning! data file not found", cfile)

    def _feedErrorsToResult(self, result, errors):
        """ Use this to show hints on test failure. """
        if not isinstance(result, UTextResult):
            er = [e for e, v in errors if v != None]

            if len(er) > 0:
                hints = []
                key = (self.cache_id(), 'coverage')
                if self._cache_contains(key):
                    CC = self._cache_get(key)
                    for id in CC:
                        if id == self.cache_id():
                            cl, m = id
                            gprint(f"> An error occured while solving: {cl}.{m}. The files/methods you need to edit are:")  # For the test {id} in {file} you should edit:")
                            for file in CC[id]:
                                rec = CC[id][file]
                                gprint(f">   * {file}")
                                for l in rec:
                                    _, comments = CC[id][file][l]
                                    hint = get_hints(comments)

                                    if hint != None:
                                        # hint = textwrap.dedent(hint)
                                        hints.append((hint, file, l) )
                                    gprint(f">      - {l}")

                er = er[0]
                doc = er._testMethodDoc
                if doc is not None:
                    hint = get_hints(er._testMethodDoc)
                    if hint is not None:
                        hints = [(hint, None, self.cache_id()[1] )] + hints
                if len(hints) > 0:
                    for hint, file, method in hints:
                        s = (f"'{method.strip()}'" if method is not None else "")
                        if method is not None and file is not None:
                            s += " in "
                        s += (file.strip() if file is not None else "")
                        gprint(">")
                        gprint("> Hints (from " + s  + ")")
                        gprint(textwrap.indent(hint, ">   "))

        super()._feedErrorsToResult(result, errors)

    def startTestRun(self):
        # print("asdfsdaf 11", file=sys.stderr)
        super().startTestRun()
        # print("asdfsdaf")

    def _callTestMethod(self, method):
        # print("asdfsdaf")
        super()._callTestMethod(method)


def hide(func):
    return func


def makeRegisteringDecorator(foreignDecorator):
    """
        Returns a copy of foreignDecorator, which is identical in every
        way(*), except also appends a .decorator property to the callable it
        spits out.
    """

    def newDecorator(func):
        # Call to newDecorator(method)
        # Exactly like old decorator, but output keeps track of what decorated it
        R = foreignDecorator(func)  # apply foreignDecorator, like call to foreignDecorator(method) would have done
        R.decorator = newDecorator  # keep track of decorator
        # R.original = func         # might as well keep track of everything!
        return R

    newDecorator.__name__ = foreignDecorator.__name__
    newDecorator.__doc__ = foreignDecorator.__doc__
    return newDecorator

hide = makeRegisteringDecorator(hide)

def methodsWithDecorator(cls, decorator):
    """
        Returns all methods in CLS with DECORATOR as the
        outermost decorator.

        DECORATOR must be a "registering decorator"; one
        can make any decorator "registering" via the
        makeRegisteringDecorator function.

        import inspect
        ls = list(methodsWithDecorator(GeneratorQuestion, deco))
        for f in ls:
            print(inspect.getsourcelines(f) ) # How to get all hidden questions.
    """
    for maybeDecorated in cls.__dict__.values():
        if hasattr(maybeDecorated, 'decorator'):
            if maybeDecorated.decorator == decorator:
                print(maybeDecorated)
                yield maybeDecorated
# 817
