import os
import json


def begin():
    notebook = {
                "cells": [
                {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "==SOLUTION==\n",
                    "\n",
                    ">This notebook is meant for curriculum development. \n",
                    "\n",
                    "## Instructions:\n",
                    "\n",
                    "### Overview\n",
                    "\n",
                    "When you have completed writing your lesson, run `ds -create` from the root of this lesson folder. This will create an `index.ipynb` notebook containing the student facing content in the root directory of this lesson. An `index.ipynb` file will be added to the `.solution_files` directory containing all solution materials. \n",
                    "\n",
                    "## How to use this file\n",
                    "\n",
                    "**Solution Tags:**\n",
                    "\n",
                    "Markdown cells: \n",
                    "- `==SOLUTION==`\n",
                    "\n",
                    "Code cells: \n",
                    "- `#__SOLUTION__`\n",
                    "\n",
                    "\n",
                    "#### Create Solution Cells:\n",
                    "- To designate a cell as a solution, place the solution tag on its own line within the cell. This cell is an example of a \"solution markdown cell\".\n",
                    "\n",
                    "- Below is an example of a solution code cell."
                ]
                },
                {
                "cell_type": "code",
                "execution_count": 0,
                "metadata": {},
                "outputs": [],
                "source": [
                    "#__SOLUTION__\n",
                    "\n",
                    "\"\"\"\n",
                    "This is a solution cell and \n",
                    "will not be copied \n",
                    "to the lesson index.ipynb file\n",
                    "\"\"\""
                ]
                }
                ],
                "metadata": {},
                "nbformat": 4,
                "nbformat_minor": 2
                }


    notebook_file = open('curriculum.ipynb', 'w')
    json.dump(notebook, notebook_file)
    notebook_file.close()

    if not os.path.isdir('data'):
        os.mkdir('data')



