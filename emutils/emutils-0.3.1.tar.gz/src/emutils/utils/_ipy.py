import logging
import subprocess
import warnings
import os
import re
from shutil import copyfile
from typing import Union, Iterable, Dict, Tuple

__all__ = [
    'display',
    'in_ipynb',
    'end',
    'import_tqdm',
    'notebook_fullwidth',
    'export_notebook',
    'copy_plotlyjs',
    'set_conda_env',
    'py_to_ipynb',
    'run_ipynb',
    'ipynb_to_html',
    'folder_py_to_ipynb',
    'folder_run_ipynb',
    'folder_ipynb_to_html',
    'py_to_ipy',
    'run_ipy',
    'ipy_to_html',
    'folder_py_to_ipy',
    'folder_run_ipy',
    'folder_ipy_to_html',
]


def in_ipynb():
    '''
        Check if we are in a IPython Environment
        Returns True if in IPython, or False otherwise
    '''
    #pylint: disable=import-outside-toplevel
    #pylint: disable=expression-not-assigned
    #pylint: disable=bare-except

    try:
        from IPython.core.getipython import get_ipython
        get_ipython().config
        return True
    except:
        return False
    #pylint: enable=import-outside-toplevel
    #pylint: enable=expression-not-assigned
    #pylint: enable=bare-except


def display(*args, **kwargs):
    if in_ipynb():
        try:
            from IPython.display import display as ipython_display
            return ipython_display(*args, **kwargs)
        except:

            warnings.warn("ERROR loading display from IPython")
            pass


def base_name(filename):
    return filename.replace('.tmp', "").replace('.py', "")


def end(
    message: str = 'This is the END.',
    only_others: bool = False,
):
    """
    Stop the execution with a message:
        - Raising an exception in Jupyter/IPython environment
        - Quitting in other environments

    Args:
        message (str, optional): Message that is displayed. Defaults to 'This is the END.'.
        only_others (bool, optional): Ends exeution only in other environments. Defaults to False.
    """
    if in_ipynb():
        if not only_others:
            raise Exception(message)
    else:
        print(message)
        quit()


def import_tqdm():
    #pylint: disable=import-outside-toplevel
    if in_ipynb():
        from tqdm.notebook import tqdm
    else:
        from tqdm import tqdm
    #pylint: enable=import-outside-toplevel
    return tqdm


def notebook_fullwidth():
    """Set the Jupyter Notebook width to the maximum page width
    """
    if in_ipynb():
        #pylint: disable=import-outside-toplevel
        from IPython.core.display import display, HTML
        #pylint: enable=import-outside-toplevel

        display(HTML("<style>.container { width:100% !important; }</style>"))


def copy_plotlyjs(path):
    """
        Copy `plotly.js` into the `path` folder if not existing already.
    """
    try:
        import plotly
        if 'plotly.js' not in os.listdir(path):
            logging.info(f"plotly.js not found in '{path}'. Copying it from emutils.")
            copyfile(os.path.join(os.path.dirname(__file__), 'plotly.js'), os.path.join(path, 'plotly.js'))
    except:
        pass


def set_conda_env(env):
    if env is not None:
        logging.info(f"Activating '{env}' conda environment.")
        # Windows
        if os.name in ['nt']:
            return os.system(f'conda activate {env}')
        # Posix OS (Linux, Max)
        else:
            os.system('/bin/bash -c "source activate"')
            os.system(f'/bin/bash -c "conda activate {env}"')


def export_notebook(name, recursive=False, in_ipy_only=True, _main=True):
    """
        Export a Jupyter Notebook

        recursive : Export also the notebooks that are %run inside the main notebook
        in_ipy_only : Export only whene executing this function in a Jupyter notebook
        
    """

    if in_ipy_only and not in_ipynb():
        return None

    if _main:
        print('Exporting script...\n')

    name = name.replace('.ipynb', '').strip()
    notebook_name, script_name = name + '.ipynb', name + '.py'
    if os.path.exists(script_name):
        os.remove(script_name)
    print(
        subprocess.run(
            ['jupyter', 'nbconvert', '--to', 'script', name],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        ).stdout.decode("utf-8")
    )
    # Read in the file
    lines = []
    # prevB = "."
    # prev = "."
    recursed_already = []
    with open(script_name, 'r') as fp:
        for line in fp.readlines():
            #pylint: disable=anomalous-backslash-in-string
            s = re.search(r"get.*ipython.*\'run\', \'(.*)\.ipynb", line)

            if s is not None:
                beginning_whitespaces = re.search(r"^([\s]*).*", line).group(1)
                import_name = s.group(1)
                line = f"{beginning_whitespaces}from {import_name} import *\n"
                if recursive and import_name not in recursed_already:
                    print(notebook_name + ' ==>> ' + import_name + '.ipynb')
                    export_notebook(import_name, _main=False)
                    recursed_already.append(import_name)

            s = re.search(r'# In\[.*\]\:', line)
            if s is not None:
                line = ""

            #pylint: enable=anomalous-backslash-in-string

            # If the line is not empty (or the previous too was empty...)
            # nospace_line = remove_all_empty_spaces(line)
            # if True or len(nospace_line) > 0 or (len(prev) == 0 and len(prevB) > 0):
            lines.append(line)

            # prevB = prev
            # prev = nospace_line
            s = None
    if _main:
        print('Done.')

    # Write the file out again
    with open(script_name, 'w') as fp:
        fp.write("".join(lines))


#pylint: disable=anomalous-backslash-in-string
CELL_PATTERN_REST = r"#[ ]*%%[ \t\v\f]*(?:\[markdown\])*[ " + "\t\v\f" + r"]*[" + "\n" + r"]"
CELL_PATTERN_TOP = '^' + CELL_PATTERN_REST
CELL_PATTERN_NEWLINE = '\n' + CELL_PATTERN_REST
MARKDOWN_PATTERN = '[markdown]'
#pylint: enable=anomalous-backslash-in-string


def py_to_ipynb(
    py_path,
    nb_path=None,
    replace_dict: Union[Dict[str, str], None] = None,
    replace_re: bool = True,
):
    """Transform a VSCODE compatible .py Python script to a .ipynb Jupyter Notebook using
    nbformat library. (see https://nbformat.readthedocs.io/en/latest/api.html for more info)

    Args:
        py_path : Python script filename
        nb_path (optional): [description]. Defaults to None.
        replace_dict (Union[dict, None], optional): [description]. Defaults to None.
        replace_re (bool, optional): [description]. Defaults to True.

    Raises:
        FileNotFoundError: [description]

    Returns:
        [type]: [description]
    """
    import nbformat as nbf

    # Check that the input file is a Python (.py) file
    if not py_path.endswith('.py'):
        raise FileNotFoundError('File is not a Python script (.py). Expecting a file ending with .py')

    # If no output path is provided the same as the input (py_path) will be used with `.ipynb` extension
    if nb_path is None:
        nb_path = py_path[:-2] + 'ipynb'

    # Create plotly.js if it doesn't exists
    copy_plotlyjs(os.path.dirname(nb_path))

    # Read python file
    with open(py_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Replace by pattern
    if replace_dict is not None:
        for o, r in replace_dict.items():
            if replace_re:
                text = re.sub(str(o), str(r), text)
            else:
                text = text.replace(str(o), str(r))

    # Find all the cells (starting point)
    matches = re.findall(CELL_PATTERN_TOP, text) + re.findall(CELL_PATTERN_NEWLINE, text)

    # Split the file at all cells starting points
    chunks = re.split(CELL_PATTERN_NEWLINE, re.split(CELL_PATTERN_TOP, text)[-1])

    # Check cell type based on the pattern matched
    cell_types = ['markdown' if MARKDOWN_PATTERN in match else 'code' for match in matches]

    # Export to ipynb
    nb = nbf.v4.new_notebook()
    cells = []
    for cell_type, chunk in zip(cell_types, chunks):
        if cell_type == 'code':
            cells.append(nbf.v4.new_code_cell(chunk))
        elif cell_type == 'markdown':
            # Remove starting comment sign (and spaces)
            chunk = re.sub('^#[ ]*', '', re.sub('\n#[ ]*', '\n', chunk))
            cells.append(nbf.v4.new_markdown_cell(chunk))
    nb['cells'] = cells

    nbf.write(nb, nb_path)

    return nb


def run_ipynb(filename, conda_env=None):
    set_conda_env(conda_env)
    print(
        subprocess.run(
            [
                'jupyter',
                'nbconvert',
                '--ExecutePreprocessor.timeout=-1',
                '--to',
                'notebook',
                '--inplace',
                '--execute',
                filename,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        ).stdout.decode("utf-8")
    )


def ipynb_to_html(filename, conda_env=None):
    set_conda_env(conda_env)
    print(
        subprocess.run(
            ['jupyter', 'nbconvert', '--to', 'html', filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        ).stdout.decode("utf-8")
    )


def folder_py_to_ipynb(
    folder,
    custom_templates: Union[None, Iterable[Tuple[str, Dict[str, str]]]],
    match: Union[None, str] = None,
    template_extension: str = '.tmp.py',
):

    # Add extension if the template do not have one
    if custom_templates is not None:
        for filename in list(custom_templates.keys()):
            if not filename.endswith(template_extension):
                logging.warning(
                    f"Custom template '{filename}' do not have expected extension ({template_extension}). Adding the extension to the file name",
                )
                custom_templates[filename + template_extension] = custom_templates[filename]
                del custom_templates[filename]

        # Copy templates
        templates = dict(custom_templates)
    else:
        templates = dict()

    # Non-custom templates import
    for filename in os.listdir(folder):
        if filename.endswith(template_extension) and filename not in templates:
            templates[filename] = None

    # Run all templates
    for template_file, replaces in templates.items():
        if not os.path.exists(os.path.join(folder, template_file)):
            continue
        print(template_file, end='')
        if (match is None) or (match.lower() in template_file.lower()):
            print(' MATCH')
            logging.info(f'Exporting templates for {template_file}')
            if replaces is not None:
                for name, replace_dict in replaces:
                    py_to_ipy(
                        py_path=os.path.join(folder, template_file),
                        nb_path=os.path.join(folder, f"{base_name(template_file)}_{name}.ipynb"),
                        replace_dict=replace_dict,
                    )

            else:
                py_to_ipy(
                    py_path=os.path.join(folder, template_file),
                    nb_path=os.path.join(folder, f'{base_name(template_file)}.ipynb'),
                )
            logging.info(f'Export templates for {template_file} done.')
        else:
            print()

    return True


def folder_run_ipynb(
    folder,
    match: Union[None, str] = None,
    conda_env: Union[None, str] = None,
):
    set_conda_env(conda_env)
    for filename in os.listdir(folder):
        if filename.endswith('.ipynb') and ((match is None) or (match.lower() in filename.lower())):
            run_ipynb(os.path.join(folder, filename))
    return True


def folder_ipynb_to_html(
    folder,
    match: Union[None, str] = None,
    conda_env: Union[None, str] = None,
):
    set_conda_env(conda_env)
    for filename in os.listdir(folder):
        if filename.endswith('.ipynb') and ((match is None) or (match.lower() in filename.lower())):
            ipynb_to_html(os.path.join(folder, filename))
    return True


py_to_ipy = py_to_ipynb
run_ipy = run_ipynb
ipy_to_html = ipynb_to_html
folder_py_to_ipy = folder_py_to_ipynb
folder_run_ipy = folder_run_ipynb
folder_ipy_to_html = folder_ipynb_to_html