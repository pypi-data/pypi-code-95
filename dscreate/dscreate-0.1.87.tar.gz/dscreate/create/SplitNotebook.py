import json
import os


class SplitNotebook:
    """
    Splits a jupyter notebook into lesson and solution notebooks.
    =============================================================
            This class looks for `#__SOLUTION__` in code cells
            and `===SOLUTION===` in markdown cells. If a solution tag
            is found in a code cell, the cell is added to the solution
            notebook and withheld from the lesson notebook.
            If a solution tag is found in a markdown cell, the cell
            is added to the solution notebook and is replaced with
            `*YOUR ANSWER HERE*` in the lesson notebook.
    """
    def __init__(self, filename='index.ipynb', dir=False):
        self.solution_tags = ["__SOLUTION__", f"#__SOLUTION__", 
                            "==SOLUTION==", f"#==SOLUTION=="]
        self.data = self.get_notebook_json(filename=filename)
        self.dir = dir

    def get_notebook_json(self, filename="index.ipynb"):
        """
        Import raw json data for a source notebook
        """
        with open(filename, 'r') as f:
            data = json.load(f)
        return data
        
    def split_notebook(self):
        """
        Loops over each cell in a notebook
        and appends all solution and lesson cells to the
        `solution_cells` and `lesson_cells` attributes.
        """
        count = 0
        lesson_cells = []
        solution_cells = []
        for cell in self.data['cells']:
            cell_type = cell['cell_type']
            solution, lines = self._parse_cell(cell)
            cell["source"] = lines
            cell['metadata']['index'] = count
            placeholder = dict(cell)
            placeholder['metadata'] = dict(cell['metadata'])
            placeholder['metadata']['index'] = 'Placeholder'
            
            if cell_type == "markdown":

                if solution:
                    solution_cells.append(cell)
                    placeholder.update({"source": ['*YOUR ANSWER HERE*']})
                    lesson_cells.append(placeholder)
                else:
                    lesson_cells.append(cell)
                    solution_cells.append(placeholder)
            else:
                if solution:
                    solution_cells.append(cell)

                else:
                    lesson_cells.append(cell)
                    if self.dir:
                        solution_cells.append(placeholder) 
                    else:
                        solution_cells.append(cell)
            count += 1 
        return lesson_cells, solution_cells 

    def _parse_cell(self, cell):
        """
        Loops over every line in a cell and 
        searches for a solution tag. 
        
        Returns a boolean indicating if a solution tag was found
        in the cel and a list of all lines that did not contain a solution tag. 

        """
        is_solution = False
        lines = []
        for line in cell["source"]:
            found = False
            for tag in self.solution_tags:
                if tag in line.strip().split(" "):
                    is_solution = True
                    found = True
            if not found:
                lines.append(line)
        return is_solution, lines

    def write_notebook(self, name, cells):
        """
        Write a notebook to file.

        name - The name of the notebook file (excluding .ipynb)
        cells - The cells the notebook will contain.
        """
        notebook = dict(self.data)
        notebook.update({"cells": cells})
        file = open(f"{name}.ipynb", "w")
        file.write(json.dumps(notebook))
        file.close()