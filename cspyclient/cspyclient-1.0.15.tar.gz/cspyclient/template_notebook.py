'''This module is a tool to generate jupyter notebook based on a notebook as the template'''
import nbformat as nbf
import re
import json
import os

class TemplateNotebook:
    @classmethod
    def generate_notebook_from_cells(cls, cells: list, output_path:str, variables_dict:dict, overwrite=False):
        if os.path.exists(output_path) and not overwrite:
            print(f'The process will not overwrite {output_path}. Turn overwrite to be True only if you want to overwrite the output file')
            return

        if os.path.splitext(output_path)[1] != '.ipynb':
            print('Output file type must be jupyter notebook (.ipynb)')
            return

        new_nb = nbf.v4.new_notebook()

        # Find set of variables to be replace in all cells
        regex = r'%(\w+)%'
        variables_set = set()
        for cell in cells:
            for line in cell['source']:
                matches = [m.group(1) for m in re.finditer(regex, line)]
                variables_set |= set(matches)
        # Raise error if there are variables in the template that are not in variables_dict
        diff = variables_set - set(variables_dict.keys())
        if diff:
            print('ERROR: undefined variables')
            print('Undefined variables in template:\n', diff)
            print('Variables in variables_dict that not in template:\n', set(variables_dict.keys()) - variables_set)
            return
        
        for cell in cells:
            new_cell = []
            for line in cell['source']:
                new_line = line
                for variable, value in variables_dict.items():
                    new_line = re.sub(f'%{variable}%', str(value), new_line)
                new_cell.append(new_line)
            new_cell = ''.join(new_cell)
            
            if cell['cell_type'] == 'markdown':
                new_nb['cells'].append(nbf.v4.new_markdown_cell(new_cell))
            elif cell['cell_type'] == 'code':
                new_nb['cells'].append(nbf.v4.new_code_cell(new_cell))

        with open(output_path, 'w') as f:
            nbf.write(new_nb, f)

    @classmethod
    def generate_notebook_from_template(cls, template_path:str, output_path:str, variables_dict:dict, overwrite=False):
        '''Generate a jupyter notebook to output_path based on the template at template_path.
        The template contains variables in form %variable_name% which should be replace with the values in variables_dict
        Parameters:
            - template_path: path to the template .ipynb file
            - output_path: path to the exported notebook
            - variables_dict: dictionary of pairs: {variable_name: value}
            - overwrite: overwrite the output file if exists or not
        '''
        if not os.path.exists(template_path):
            print('Template not exists')
            return
        if os.path.exists(output_path) and not overwrite:
            print(f'The process will not overwrite {output_path}. Turn overwrite to be True only if you want to overwrite the output file')
            return
        if os.path.splitext(template_path)[1] != '.ipynb':
            print('Template file type must be jupyter notebook (.ipynb)')
            return
        if os.path.splitext(output_path)[1] != '.ipynb':
            print('Output file type must be jupyter notebook (.ipynb)')
            return

        nb_json = json.load(open(template_path, 'r'))
        cells = nb_json['cells']

        cls.generate_notebook_from_cells(cells, output_path, variables_dict, overwrite)

    @classmethod
    def generate_notebook_from_package_template(cls, filename: str, output_path: str, variables_dict: dict, overwrite=False):
        try:
            import importlib.resources as pkg_resources
        except ImportError:
            # Try backported to PY<37 `importlib_resources`.
            import importlib_resources as pkg_resources

        from . import template_notebooks  # relative-import the *package* containing the templates

        template = pkg_resources.read_text(template_notebooks, filename)
        # or for a file-like stream:
        # template = pkg_resources.open_text(template_notebooks, filename)
        nb_json = json.load(template)
        cells = nb_json['cells']

        cls.generate_notebook_from_cells(cells, output_path, variables_dict, overwrite=False)