"""
git add . && git commit -m "Options" && git push &&  pip install git+ssh://git@gitlab.compute.dtu.dk/tuhe/unitgrade.git --upgrade

"""
from . import cache_read
import unittest
import numpy as np
import os
import sys
from io import StringIO
import collections
import inspect
import re
import threading
import tqdm
import time

myround = lambda x: np.round(x)  # required.
msum = lambda x: sum(x)
mfloor = lambda x: np.floor(x)

def setup_dir_by_class(C,base_dir):
    name = C.__class__.__name__
    # base_dir = os.path.join(base_dir, name)
    # if not os.path.isdir(base_dir):
    #     os.makedirs(base_dir)
    return base_dir, name

class Hidden:
    def hide(self):
        return True

class Logger(object):
    def __init__(self, buffer):
        self.terminal = sys.stdout
        self.log = buffer

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        # this flush method is needed for python 3 compatibility.
        pass

class Capturing(list):
    def __init__(self, *args, unmute=False, **kwargs):
        self.unmute = unmute
        super().__init__(*args, **kwargs)

    def __enter__(self, capture_errors=True): # don't put arguments here.
        self._stdout = sys.stdout
        self._stringio = StringIO()
        if self.unmute:
            sys.stdout = Logger(self._stringio)
        else:
            sys.stdout = self._stringio

        if capture_errors:
            self._sterr = sys.stderr
            sys.sterr = StringIO() # memory hole it
        self.capture_errors = capture_errors
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout
        if self.capture_errors:
            sys.sterr = self._sterr


class QItem(unittest.TestCase):
    title = None
    testfun = None
    tol = 0
    estimated_time = 0.42
    _precomputed_payload = None
    _computed_answer = None # Internal helper to later get results.
    weight = 1 # the weight of the question.

    def __init__(self, question=None, *args, **kwargs):
        if self.tol > 0 and self.testfun is None:
            self.testfun = self.assertL2Relative
        elif self.testfun is None:
            self.testfun = self.assertEqual

        self.name = self.__class__.__name__
        # self._correct_answer_payload = correct_answer_payload
        self.question = question

        super().__init__(*args, **kwargs)
        if self.title is None:
            self.title = self.name

    def _safe_get_title(self):
        if self._precomputed_title is not None:
            return self._precomputed_title
        return self.title

    def assertNorm(self, computed, expected, tol=None):
        if tol == None:
            tol = self.tol
        diff = np.abs( (np.asarray(computed).flat- np.asarray(expected)).flat )
        nrm = np.sqrt(np.sum( diff ** 2))

        self.error_computed = nrm

        if nrm > tol:
            print(f"Not equal within tolerance {tol}; norm of difference was {nrm}")
            print(f"Element-wise differences {diff.tolist()}")
            self.assertEqual(computed, expected, msg=f"Not equal within tolerance {tol}")

    def assertL2(self, computed, expected, tol=None):
        if tol == None:
            tol = self.tol
        diff = np.abs( (np.asarray(computed) - np.asarray(expected)) )
        self.error_computed = np.max(diff)

        if np.max(diff) > tol:
            print(f"Not equal within tolerance {tol=}; deviation was {np.max(diff)=}")
            print(f"Element-wise differences {diff.tolist()}")
            self.assertEqual(computed, expected, msg=f"Not equal within tolerance {tol=}, {np.max(diff)=}")

    def assertL2Relative(self, computed, expected, tol=None):
        if tol == None:
            tol = self.tol
        diff = np.abs( (np.asarray(computed) - np.asarray(expected)) )
        diff = diff / (1e-8 + np.abs( (np.asarray(computed) + np.asarray(expected)) ) )
        self.error_computed = np.max(np.abs(diff))
        if np.sum(diff > tol) > 0:
            print(f"Not equal within tolerance {tol}")
            print(f"Element-wise differences {diff.tolist()}")
            self.assertEqual(computed, expected, msg=f"Not equal within tolerance {tol}")

    def precomputed_payload(self):
        return self._precomputed_payload

    def precompute_payload(self):
        # Pre-compute resources to include in tests (useful for getting around rng).
        pass

    def compute_answer(self, unmute=False):
        raise NotImplementedError("test code here")

    def test(self, computed, expected):
        self.testfun(computed, expected)

    def get_points(self, verbose=False, show_expected=False, show_computed=False,unmute=False, passall=False, silent=False, **kwargs):
        possible = 1
        computed = None
        def show_computed_(computed):
            print(">>> Your output:")
            print(computed)

        def show_expected_(expected):
            print(">>> Expected output (note: may have been processed; read text script):")
            print(expected)

        correct = self._correct_answer_payload
        try:
            if unmute: # Required to not mix together print stuff.
                print("")
            computed = self.compute_answer(unmute=unmute)
        except Exception as e:
            if not passall:
                if not silent:
                    print("\n=================================================================================")
                    print(f"When trying to run test class '{self.name}' your code threw an error:", e)
                    show_expected_(correct)
                    import traceback
                    print(traceback.format_exc())
                    print("=================================================================================")
                return (0, possible)

        if self._computed_answer is None:
            self._computed_answer = computed

        if show_expected or show_computed:
            print("\n")
        if show_expected:
            show_expected_(correct)
        if show_computed:
            show_computed_(computed)
        try:
            if not passall:
                self.test(computed=computed, expected=correct)
        except Exception as e:
            if not silent:
                print("\n=================================================================================")
                print(f"Test output from test class '{self.name}' does not match expected result. Test error:")
                print(e)
                show_computed_(computed)
                show_expected_(correct)
            return (0, possible)
        return (1, possible)

    def score(self):
        try:
            self.test()
        except Exception as e:
            return 0
        return 1

class QPrintItem(QItem):
    def compute_answer_print(self):
        """
        Generate output which is to be tested. By default, both text written to the terminal using print(...) as well as return values
        are send to process_output (see compute_answer below). In other words, the text generated is:

        res = compute_Answer_print()
        txt = (any terminal output generated above)
        numbers = (any numbers found in terminal-output txt)

        self.test(process_output(res, txt, numbers), <expected result>)

        :return: Optional values for comparison
        """
        raise Exception("Generate output here. The output is passed to self.process_output")

    def process_output(self, res, txt, numbers):
        return res

    def compute_answer(self, unmute=False):
        with Capturing(unmute=unmute) as output:
            res = self.compute_answer_print()
        s = "\n".join(output)
        s = rm_progress_bar(s) # Remove progress bar.
        numbers = extract_numbers(s)
        self._computed_answer = (res, s, numbers)
        return self.process_output(res, s, numbers)

class OrderedClassMembers(type):
    @classmethod
    def __prepare__(self, name, bases):
        return collections.OrderedDict()
    def __new__(self, name, bases, classdict):
        ks = list(classdict.keys())
        for b in bases:
            ks += b.__ordered__
        classdict['__ordered__'] = [key for key in ks if key not in ('__module__', '__qualname__')]
        return type.__new__(self, name, bases, classdict)

class QuestionGroup(metaclass=OrderedClassMembers):
    title = "Untitled question"
    partially_scored = False
    t_init = 0  # Time spend on initialization (placeholder; set this externally).
    estimated_time = 0.42
    has_called_init_ = False
    _name = None
    _items = None

    @property
    def items(self):
        if self._items == None:
            self._items = []
            members = [gt for gt in [getattr(self, gt) for gt in self.__ordered__ if gt not in ["__classcell__", "__init__"]] if inspect.isclass(gt) and issubclass(gt, QItem)]
            for I in members:
                self._items.append( I(question=self))
        return self._items

    @items.setter
    def items(self, value):
        self._items = value

    @property
    def name(self):
        if self._name == None:
            self._name = self.__class__.__name__
        return self._name #

    @name.setter
    def name(self, val):
        self._name = val

    def init(self):
        # Can be used to set resources relevant for this question instance.
        pass

    def init_all_item_questions(self):
        for item in self.items:
            if not item.question.has_called_init_:
                item.question.init()
                item.question.has_called_init_ = True


class Report():
    title = "report title"
    version = None
    questions = []
    pack_imports = []
    individual_imports = []

    def __init__(self, strict=False, payload=None):
        working_directory = os.path.abspath(os.path.dirname(inspect.getfile(type(self))))
        self.wdir, self.name = setup_dir_by_class(self, working_directory)
        self.computed_answers_file = os.path.join(self.wdir, self.name + "_resources_do_not_hand_in.dat")
        import time
        qs = [] # Has to accumulate to new array otherwise the setup/evaluation steps cannot be run in sequence.
        for k, (Q, w) in enumerate(self.questions):
            start = time.time()
            q = Q()
            q.t_init = time.time() - start
            for k, i in enumerate(q.items):
                i.name = i.name + "_" + str(k)
            qs.append((q, w))

        self.questions = qs
        if payload is not None:
            self.set_payload(payload, strict=strict)
        else:
            if os.path.isfile(self.computed_answers_file):
                self.set_payload(cache_read(self.computed_answers_file), strict=strict)
            else:
                s = f"> Warning: The pre-computed answer file, {os.path.abspath(self.computed_answers_file)} is missing. The framework will NOT work as intended. Reasons may be a broken local installation."
                if strict:
                    raise Exception(s)
                else:
                    print(s)


    def set_payload(self, payloads, strict=False):
        for q, _ in self.questions:
            for item in q.items:
                if q.name not in payloads or item.name not in payloads[q.name]:
                    s = f"> Broken resource dictionary submitted to unitgrade for question {q.name} and subquestion {item.name}. Framework will not work."
                    if strict:
                        raise Exception(s)
                    else:
                        print(s)
                else:
                    item._correct_answer_payload = payloads[q.name][item.name]['payload']
                    item.estimated_time = payloads[q.name][item.name].get("time", 1)
                    q.estimated_time = payloads[q.name].get("time", 1)
                    if "precomputed" in payloads[q.name][item.name]: # Consider removing later.
                        item._precomputed_payload = payloads[q.name][item.name]['precomputed']
                    try:
                        if "title" in payloads[q.name][item.name]: # can perhaps be removed later.
                            item.title = payloads[q.name][item.name]['title']
                    except Exception as e: # Cannot set attribute error. The title is a function (and probably should not be).
                        pass
                        # print("bad", e)
        self.payloads = payloads


def rm_progress_bar(txt):
    # More robust version. Apparently length of bar can depend on various factors, so check for order of symbols.
    nlines = []
    for l in txt.splitlines():
        pct = l.find("%")
        ql = False
        if pct > 0:
            i = l.find("|", pct+1)
            if i > 0 and l.find("|", i+1) > 0:
                ql = True
        if not ql:
            nlines.append(l)
    return "\n".join(nlines)

def extract_numbers(txt):
    # txt = rm_progress_bar(txt)
    numeric_const_pattern = '[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'
    rx = re.compile(numeric_const_pattern, re.VERBOSE)
    all = rx.findall(txt)
    all = [float(a) if ('.' in a or "e" in a) else int(a) for a in all]
    if len(all) > 500:
        print(txt)
        raise Exception("unitgrade.unitgrade.py: Warning, many numbers!", len(all))
    return all


class ActiveProgress():
    def __init__(self, t, start=True, title="my progress bar"):
        self.t = t
        self._running = False
        self.title = title
        self.dt = 0.1

        self.n = int(np.round(self.t / self.dt))
        # self.pbar = tqdm.tqdm(total=self.n)


        if start:
            self.start()

    def start(self):
        self._running = True
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def terminate(self):


        self._running = False
        self.thread.join()
        if hasattr(self, 'pbar') and self.pbar is not None:
            self.pbar.update(1)
            self.pbar.close()
            self.pbar=None

        sys.stdout.flush()

    def run(self):
        self.pbar = tqdm.tqdm(total=self.n, file=sys.stdout, position=0, leave=False, desc=self.title, ncols=100,
                              bar_format='{l_bar}{bar}| [{elapsed}<{remaining}]')  # , unit_scale=dt, unit='seconds'):

        for _ in range(self.n-1): # Don't terminate completely; leave bar at 99% done until terminate.
            if not self._running:
                self.pbar.close()
                self.pbar = None
                break

            time.sleep(self.dt)
            self.pbar.update(1)
