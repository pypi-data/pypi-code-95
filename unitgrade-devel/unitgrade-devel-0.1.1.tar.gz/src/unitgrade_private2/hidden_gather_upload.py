from unitgrade2.unitgrade_helpers2 import evaluate_report
import bz2
import pickle
import os


def bzwrite(json_str, token): # to get around obfuscation issues
    with getattr(bz2, 'open')(token, "wt") as f:
        f.write(json_str)

def gather_imports(imp):
    resources = {}
    m = imp
    # for m in pack_imports:
    # print(f"*** {m.__name__}")
    f = m.__file__
    # dn = os.path.dirname(f)
    # top_package = os.path.dirname(__import__(m.__name__.split('.')[0]).__file__)
    # top_package = str(__import__(m.__name__.split('.')[0]).__path__)

    if hasattr(m, '__file__') and not hasattr(m, '__path__'):  # Importing a simple file: m.__class__.__name__ == 'module' and False:
        top_package = os.path.dirname(m.__file__)
        module_import = True
    else:
        top_package = __import__(m.__name__.split('.')[0]).__path__._path[0]
        module_import = False

    # top_package = os.path.dirname(__import__(m.__name__.split('.')[0]).__file__)
    # top_package = os.path.dirname(top_package)
    import zipfile
    # import strea
    # zipfile.ZipFile
    import io
    # file_like_object = io.BytesIO(my_zip_data)
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip:
        # zip.write()
        for root, dirs, files in os.walk(top_package):
            for file in files:
                if file.endswith(".py"):
                    fpath = os.path.join(root, file)
                    v = os.path.relpath(os.path.join(root, file), os.path.dirname(top_package) if not module_import else top_package)
                    zip.write(fpath, v)

    resources['zipfile'] = zip_buffer.getvalue()
    resources['top_package'] = top_package
    resources['module_import'] = module_import
    return resources, top_package

    if f.endswith("__init__.py"):
        for root, dirs, files in os.walk(os.path.dirname(f)):
            for file in files:
                if file.endswith(".py"):
                    # print(file)
                    # print()
                    v = os.path.relpath(os.path.join(root, file), top_package)
                    with open(os.path.join(root, file), 'r') as ff:
                        resources[v] = ff.read()
    else:
        v = os.path.relpath(f, top_package)
        with open(f, 'r') as ff:
            resources[v] = ff.read()
    return resources

import argparse
parser = argparse.ArgumentParser(description='Evaluate your report.', epilog="""Use this script to get the score of your report. Example:

> python report1_grade.py

Finally, note that if your report is part of a module (package), and the report script requires part of that package, the -m option for python may be useful.
For instance, if the report file is in Documents/course_package/report3_complete.py, and `course_package` is a python package, then change directory to 'Documents/` and run:

> python -m course_package.report1

see https://docs.python.org/3.9/using/cmdline.html
""", formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('--noprogress',  action="store_true",  help='Disable progress bars')
parser.add_argument('--autolab',  action="store_true",  help='Show Autolab results')

def gather_upload_to_campusnet(report, output_dir=None):
    n = report.nL
    args = parser.parse_args()
    results, table_data = evaluate_report(report, show_help_flag=False, show_expected=False, show_computed=False, silent=True,
                                          show_progress_bar=not args.noprogress,
                                          big_header=not args.autolab)
    # print(" ")
    # print("="*n)
    # print("Final evaluation")
    # print(tabulate(table_data))
    # also load the source code of missing files...

    sources = {}
    print("")
    if not args.autolab:
        if len(report.individual_imports) > 0:
            print("By uploading the .token file, you verify the files:")
            for m in report.individual_imports:
                print(">", m.__file__)
            print("Are created/modified individually by you in agreement with DTUs exam rules")
            report.pack_imports += report.individual_imports

        if len(report.pack_imports) > 0:
            print("Including files in upload...")
            for k, m in enumerate(report.pack_imports):
                nimp, top_package = gather_imports(m)
                _, report_relative_location, module_import = report._import_base_relative()

                # report_relative_location = os.path.relpath(inspect.getfile(report.__class__), top_package)
                nimp['report_relative_location'] = report_relative_location
                nimp['report_module_specification'] = module_import
                nimp['name'] = m.__name__
                sources[k] = nimp
                # if len([k for k in nimp if k not in sources]) > 0:
                print(f" * {m.__name__}")
                # sources = {**sources, **nimp}
    results['sources'] = sources

    if output_dir is None:
        output_dir = os.getcwd()

    payload_out_base = report.__class__.__name__ + "_handin"

    obtain, possible = results['total']
    vstring = "_v"+report.version if report.version is not None else ""

    token = "%s_%i_of_%i%s.token"%(payload_out_base, obtain, possible,vstring)
    token = os.path.normpath(os.path.join(output_dir, token))


    with open(token, 'wb') as f:
        pickle.dump(results, f)

    if not args.autolab:
        print(" ")
        print("To get credit for your results, please upload the single unmodified file: ")
        print(">", token)
        # print("To campusnet without any modifications.")

        # print("Now time for some autolab fun")

def source_instantiate(name, report1_source, payload):
    eval("exec")(report1_source, globals())
    pl = pickle.loads(bytes.fromhex(payload))
    report = eval(name)(payload=pl, strict=True)
    # report.set_payload(pl)
    return report
