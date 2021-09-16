from unitgrade import unitgrade_helpers
import jinja2
import pickle
import inspect
import time
import os
from unitgrade_private import hidden_gather_upload
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
    assert False
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
    # cache_write(payloads, report.computed_answers_file, verbose=False)


def strip_main(report1_source):
    dx = report1_source.find("__main__")
    report1_source = report1_source[:dx]
    report1_source = report1_source[:report1_source.rfind("\n")]
    return report1_source


def setup_grade_file_report(ReportClass, execute=False, obfuscate=False, minify=False, bzip=True, nonlatin=False, source_process_fun=None, with_coverage=True):
    print("Setting up answers...")
    report = ReportClass()
    payload = report._setup_answers(with_coverage=with_coverage)
    payload['config'] = {}
    from unitgrade_private.hidden_gather_upload import gather_report_source_include
    sources = gather_report_source_include(report)
    known_hashes = [v for s in sources.values() for v in s['blake2b_file_hashes'].values() ]
    # assert len(known_hashes) == len(set(known_hashes)) # Check for collisions.
    payload['config']['blake2b_file_hashes'] = known_hashes
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
    picklestring = pickle.dumps(payload)

    import unitgrade
    excl = ["unitgrade.unitgrade_helpers",
            "from . import",
            "from unitgrade.",
            "from unitgrade ",
            "import unitgrade"]

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

    pyhead = lload([unitgrade_helpers.__file__, hidden_gather_upload.__file__], excl)
    from unitgrade import version
    report1_source = lload([unitgrade.__file__, unitgrade.unitgrade.__file__, unitgrade_helpers.__file__, hidden_gather_upload.__file__, version.__file__], excl) + "\n" + report1_source

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

    if minify or bzip:  # obfuscate:
        obs = '-O ' if obfuscate else ""
        # output_obfuscated = output[:-3]+"_obfuscated.py"
        extra = [  # "--nonlatin",
            # '--bzip2',
        ]
        if bzip: extra.append("--bzip2")
        if minify:
            obs += " --replacement-length=20"

        cmd = f'pyminifier {obs} {" ".join(extra)} -o {output} {output}'
        print(cmd)
        os.system(cmd)
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
