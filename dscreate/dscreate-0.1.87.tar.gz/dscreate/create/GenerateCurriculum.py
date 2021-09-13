import json
import os

class GenerateCurriculum:
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
    def __init__(self):
        self.cells = []
        self.solution_path = os.path.join('.solution_files', 'index.ipynb')
        self.notebook = {
                            "cells": [],
                            "metadata": {},
                            "nbformat": 4,
                            "nbformat_minor": 2
                            }

        

    def get_solution_cells(self):
        with open(self.solution_path, 'r') as file:
            data = json.load(file)
        
        for idx in range(len(data['cells'])):
            data['cells'][idx]['source'] = ['#==SOLUTION== \n'] + data['cells'][idx]['source']

        self.cells += data['cells']

    def get_lesson_cells(self):
        with open('index.ipynb', 'r') as file:
            data = json.load(file)

        self.cells += data['cells']

    def sort_cells(self):
        cells = []
        for cell in self.cells:
            if 'index' in cell['metadata']:
                if cell['metadata']['index'] != 'Placeholder':
                    cells.append(cell)
            else:
                continue
        self.notebook['cells'] = sorted(cells, key=lambda x: x['metadata']['index'])
        


    def create_curriculum_notebook(self):
        """
        Write a notebook to file.

        """

        file = open(f"curriculum.ipynb", "w")
        file.write(json.dumps(self.notebook))
        file.close()

    def main(self, filename="curriculum.ipynb"):
        """
        Main function for running the splitting process.
        """
        self.get_lesson_cells()
        self.get_solution_cells()
        self.sort_cells()
        self.create_curriculum_notebook()