from src.unitgrade2 import unitgrade_helpers2
import jinja2
import pickle
import inspect
import os
from unitgrade_private2 import hidden_gather_upload
import sys

data = """
{{head}}

report1_source = {{source}}
report1_payload = '{{payload}}'
name="{{Report1}}"

report = source_instantiate(name, report1_source, report1_payload)
output_dir = os.path.dirname(__file__)
gather_upload_to_campusnet(report, output_dir)
"""

def setup_answers(report):
    """
    Obtain student answers by executing the test in the report and then same them to the disk.
    """
    payloads = {}
    import tabulate
    from collections import defaultdict
    rs = defaultdict(lambda: [])
    for q, _ in report.questions:
        # for q, _ in report.questions:
        q()._save_cache()

        q.name = q.__class__
        payloads[q.name] = {}
        print("> Setting up question", q)
        # start = time.time()
        # q.init_all_item_questions() # Initialize all this questions items questions (i.e. make sure the items can run).
        # payloads[q.name]['time'] = time.time()-start
        # for item in q.items:
        #     print("    Setting up item", item)
        #     start = time.time()
        #     item._precomputed_payload = item.precompute_payload()
        #     answer = item.compute_answer(unmute=True)
        #
        #     rs['Name'].append(str(item))
        #     rs['Answer'].append( sys.getsizeof(pickle.dumps(answer)) )
        #     rs['Precomputed'].append( sys.getsizeof( pickle.dumps(item._precomputed_payload)))
        #     payloads[q.name][item.name] = {'payload': answer, 'precomputed': item._precomputed_payload, 'time': time.time() - start, 'title': item.title}

    print(tabulate.tabulate(rs, headers="keys"))
    # from src.unitgrade2 import cache_write, unitgrade_helpers2
    # cache_write(payloads, report.computed_answers_file, verbose=False)


def strip_main(report1_source):
    dx = report1_source.find("__main__")
    report1_source = report1_source[:dx]
    report1_source = report1_source[:report1_source.rfind("\n")]
    return report1_source

# def pack_report_for_students(Report1, obfuscate=False, minify=False, bzip=True, nonlatin=False):

def setup_grade_file_report(ReportClass, execute=False, obfuscate=False, minify=False, bzip=True, nonlatin=False, source_process_fun=None,
                            with_coverage=True):
    print("Setting up answers...")
    payload = ReportClass()._setup_answers(with_coverage=with_coverage)
    # setup_answers(ReportClass())
    import time
    time.sleep(0.1)
    print("Packing student files...")
    # pack report into a binary blob thingy the students can run on their own.
    # report = ReportClass()
    fn = inspect.getfile(ReportClass)
    with open(fn, 'r') as f:
        report1_source = f.read()
    report1_source = strip_main(report1_source)

    # Do fixing of source. Do it dirty/fragile:
    if source_process_fun == None:
        source_process_fun = lambda s: s

    report1_source = source_process_fun(report1_source)

    # payload = cache_read(report.computed_answers_file)
    picklestring = pickle.dumps(payload)

    import unitgrade2
    excl = ["unitgrade2.unitgrade_helpers2",
            "from . import",
            "from unitgrade2.",
            "from unitgrade2 ",
            "import unitgrade2"]

    def rmimports(s, excl):
        s = "\n".join([l for l in s.splitlines() if not any([l.strip().startswith(e) for e in excl])])
        return s

    def lload(flist, excl):
        s = ""
        for fname in flist:
            with open(fname, 'r', encoding="utf-8") as f:
                s += f.read() + "\n" + "\n"
        s = rmimports(s, excl)  # remove import statements from helper class.
        return s
    report1_source = rmimports(report1_source, excl)

    pyhead = lload([unitgrade_helpers2.__file__, hidden_gather_upload.__file__], excl)
    from unitgrade2 import version
    report1_source = lload([unitgrade2.__file__, unitgrade2.unitgrade2.__file__, unitgrade_helpers2.__file__, hidden_gather_upload.__file__, version.__file__], excl) + "\n" + report1_source

    print(sys.getsizeof(picklestring))
    print(len(picklestring))
    s = jinja2.Environment().from_string(data).render({'Report1': ReportClass.__name__,
                                                       'source': repr(report1_source),
                                                       'payload': picklestring.hex(), #repr(picklestring),
                                                       'token_out': repr(fn[:-3] + "_handin"),
                                                       'head': pyhead})
    output = fn[:-3] + "_grade.py"
    print("> Writing student script to", output, "(this script may be shared)")
    with open(output, 'w', encoding="utf-8") as f:
        f.write(s)

    if minify:  # obfuscate:
        obs = '-O ' if obfuscate else ""
        # output_obfuscated = output[:-3]+"_obfuscated.py"
        extra = [  # "--nonlatin",
            # '--bzip2',
        ]
        if bzip: extra.append("--bzip2")
        cmd = f'pyminifier {obs} {" ".join(extra)} --replacement-length=20 -o {output} {output}'
        print(cmd)
        os.system(cmd)
        import time
        time.sleep(0.2)
        with open(output, 'r') as f:
            sauce = f.read().splitlines()
        wa = """WARNING: Modifying, decompiling or otherwise tampering with this script, it's data or the resulting .token file will be investigated as a cheating attempt."""
        sauce = ["'''" + wa + "'''"] + sauce[:-1]
        sauce = "\n".join(sauce)
        with open(output, 'w') as f:
            f.write(sauce)

    if execute:
        time.sleep(0.1)
        print("Testing packed files...")
        fn = inspect.getfile(ReportClass)
        s = os.path.basename(fn)[:-3] + "_grade"
        exec("import " + s)
    a = 234
