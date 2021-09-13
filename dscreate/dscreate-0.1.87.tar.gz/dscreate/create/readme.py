import os
import re
import nbformat
from nbconvert import MarkdownExporter
from nbconvert.writers import FilesWriter
from traitlets.config import Config
    
def generate_readme(notebook_path, filename):
    """
    Saves a jupyter notebook as a README.md file using nbformat and nbconvert

    Inputs:
    1. The path for a jupyter notebook to be converted into markdown. str.
    2. The directory path for saving the README.md file. str.
    3. The name of the file without the `.filetype` (README instead of README.md). str.

    Returns:
    None
    """

    notebook = nbformat.read(notebook_path, as_version=4)

    resources = {}
    resources['unique_key'] = 'index'
    resources['output_files_dir'] = 'index_files'

    mark_exporter = MarkdownExporter()
    (output, resources) = mark_exporter.from_notebook_node(notebook, resources=resources)

    c = Config()
    fw = FilesWriter(config=c)
    fw.write(output, resources, notebook_name=filename)