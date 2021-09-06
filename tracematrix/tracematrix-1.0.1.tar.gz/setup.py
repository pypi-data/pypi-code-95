# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['tracematrix', 'tracematrix.reporters']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.0.1,<4.0.0']

setup_kwargs = {
    'name': 'tracematrix',
    'version': '1.0.1',
    'description': 'Tool to create a traceability matrix',
    'long_description': '# tracematrix\nA Python tool to create a traceability matrix.\n\n## Scope\nThis package focuses on generating the traceability matrix itself.\nAs the APIs and export formats of different test management and/or requirement management tools can be very different, the data acquisition and conversion is not in the scope of this package. However, it aims to provide a convenient way to create the individual items (e.g. requirements, testcases or any other traceable item) and traces between them.\n\n## How to use this package\nCurrently it is only possible to use this package programmatically in your own script.\n\nYou start by creating an instance of ``TraceabilityMatrix``.\nThe output format is controlled by the ``reporter`` parameter.\nBy default ``CsvReporter`` is used, but you can also generate HTML output by passing ``HtmlReporter``.\n```Python\nfrom tracematrix.matrix import TraceabilityMatrix\nfrom tracematrix.reporters import HtmlReporter\n\nmatrix = TraceabilityMatrix(reporter=HtmlReporter)\n```\n\nIn the next step you add rows and columns to the ``matrix``. Rows and columns can represent anything\nwhich may be traced against each other. Let\'s assume that we want to see traces between requirements and test cases.\nThis is where your own logic comes into play - the way you determine which items exist and what is traced against each other is up to you and what the source of your data is. For this example, we just use some hardcoded values.\n```Python\nfor testcase_id in ("TC_1", "TC_2", "TC_3"):\n    matrix.add_row(testcase_id)\nfor requirement_id in ("REQ_1", "REQ_2", "REQ_3", "REQ_4"):\n    matrix.add_column(requirement_id)\n\nmatrix.add_trace("TC_1", "REQ_1")\nmatrix.add_trace("TC_2", "REQ_2")\nmatrix.add_trace("TC_2", "REQ_3")\n```\nNote that rows and columns must be unique - you cannot have two rows or two columns with the same ``id``.\nWhen you add a trace between a row and a column, the ``TraceabilityMatrix`` will look up the corresponding\n``TraceItem`` instances itself.\n\nFinally, you can save the output to disk:\n```Python\nmatrix.write_matrix("traceability_matrix.html)\n```\n\n# Changelog\n\n## V1.0.1\n### Fixes\n* Remove empty lines in CSV output on windows\n  Closes #2\n\n## V1.0.0\n### API changes:\n* ``TraceItem`` has been degraded to a simple dataclass. The methods ``get_by_id`` and ``add_trace`` have been removed. Adding items (rows or columns) to a ``TraceabilityMatrix`` is now done by using ``TraceabilityMatrix.add_row(row_id)`` and ``TraceabilityMatrix.add_column(column_id)``. Traces between rows and columns are created by calling ``TraceabilityMatrix.add_trace(row_id, column_id)``. To all these methods, the ``id`` is passed as a string. The end user does not need to work with the ``TraceItem`` class any more.\n',
    'author': 'Andreas Finkler',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/DudeNr33/tracematrix',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
