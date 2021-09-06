#!python

import os
import subprocess
from argparse import ArgumentParser, RawTextHelpFormatter
from emutils.utils import py_to_ipy, run_ipynb, ipynb_to_html

# Custom Templates
# In order to add more custom templates, it must be added here


def main():
    parser = ArgumentParser(
        prog='emnbconvert',
        description='''Extension of \'jupyter nbconvert\'
This script allow for the export of .py files in VSCODE format to .ipynb and .html''',
        formatter_class=RawTextHelpFormatter,
    )
    parser.add_argument(
        'filenames', metavar='FILENAME', nargs='+', help='Python Regex(s) for the .py filename to export', default=None
    )
    # parser.add_argument('--to', type=str, choices=['notebook', 'html'], default='notebook')
    parser.add_argument(
        '--override',
        action='store_true',
        default=False,
        help="Override the .ipynb file if it exists (by default it skips it)"
    )
    parser.add_argument('--execute', action='store_true', default=False, help="Execute the .ipynb Notebook")
    parser.add_argument('--html', action='store_true', default=False, help="Export the .ipynb Notebook to HTML")
    parser.add_argument(
        '--all', action='store_true', default=False, help="Does all (.ipynb export, override, execute and HTML export)"
    )
    args = parser.parse_args()

    if args.all:
        args.override, args.execute, args.html = True, True, True

    filenames = args.filenames
    print("FILENAMES: ", filenames)

    for filename in filenames:
        py_path = os.path.join('.', filename)
        nb_path = os.path.join('.', os.path.splitext(filename)[0] + '.ipynb')
        print(py_path, nb_path)
        if not args.override and os.path.exists(nb_path):
            print(f'{nb_path} already exists. SKIPPING. (Use --override to override it)')
        else:
            print(f'Converting {filename} to Jupyter Notebook ({nb_path})...')
            py_to_ipy(
                py_path=py_path,
                nb_path=nb_path,
            )
            print('Convertion done.')

        if args.execute:
            which_python = subprocess.run(
                ['which', 'python'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False
            ).stdout.decode("utf-8").strip()
            print(f'Executing {nb_path} using {which_python}...')

            run_ipynb(nb_path)
            print('Execution done.')

        if args.html:
            print(f'Exporting HTML {nb_path} ...')
            ipynb_to_html(nb_path)
            print('Export done.')

        # logging.info('\n\nAll convertions to Jupyter Notebooks done. :)')

    # if args.run_notebook:
    #     # Run notebooks
    #     folder_run_ipynb('.', match=match, conda_env='a')
    #     time.sleep(2)

    #     # Export HTML
    #     folder_ipynb_to_html('.', match=match, conda_env='a')


if __name__ == "__main__":
    main()