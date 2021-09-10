# This file is part of Sympathy for Data.
# Copyright (c) 2013, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
"""
Merge two tables or two lists of tables (database style) using these nodes:
    - :ref:`Merge Table`
    - :ref:`Merge Tables`

Internally uses `pandas.DataFrame.merge <https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.merge.html>`_ for
More information see that documentation.

Essentially, this node calls:

.. code-block:: python

    pandas.merge(
        input_a, input_b, how=join_operation,
        on=index_column)

Values for Join Operation are:

    - Union, similar to SQL full outer join
    - Intersection, similar to SQL inner join
    - Index from A, similar to SQL left outer join
    - Index from B, similar to SQL right outer join

"""
from sympathy.api import node
from sympathy.api import node_helper
from sympathy.api import table
from sympathy.api.nodeconfig import Tag, Tags, adjust
import pandas
import collections
import itertools


MERGE_OPERATIONS = collections.OrderedDict([
    ('Union', 'outer'),
    ('Intersection', 'inner'),
    ('Index from A', 'left'),
    ('Index from B', 'right')])


class MergeTableOperation(node_helper._TableOperation):
    author = 'Greger Cronquist'
    version = '1.0'
    description = 'Merge Tables while matching an Index'
    tags = Tags(Tag.DataProcessing.TransformStructure)
    icon = 'merge.svg'
    inputs = ['Input A', 'Input B']
    outputs = ['Output']
    update_using = None

    @staticmethod
    def get_parameters(parameter_group):
        parameter_group.set_list(
            'index', label='Index column',
            values=[0],
            description='Column with indices to match',
            editor=node.Util.combo_editor(edit=True))
        parameter_group.set_list(
            'operation', label='Join operation',
            description='Column with y values.',
            list=list(MERGE_OPERATIONS.keys()),
            value=[0],
            editor=node.Util.combo_editor())

    def adjust_table_parameters(self, in_table, parameter_root):
        adjust(parameter_root['index'], in_table['Input A'])

    def execute_table(self, in_table, out_table, parameter_root):
        index_column = parameter_root['index'].selected
        operation = parameter_root['operation'].selected
        if (in_table['Input A'].is_empty() and not
                in_table['Input B'].is_empty()):
            out_table['Output'].source(in_table['Input B'])
        elif (in_table['Input B'].is_empty() and not
                in_table['Input A'].is_empty()):
            out_table['Output'].source(in_table['Input A'])
        elif (in_table['Input B'].is_empty() and
                in_table['Input A'].is_empty()):
            return
        else:
            table_a = in_table['Input A'].to_dataframe()
            table_b = in_table['Input B'].to_dataframe()

            new_table = pandas.merge(
                table_a, table_b, how=MERGE_OPERATIONS[operation],
                on=index_column)

            out_table['Output'].source(table.File.from_dataframe(new_table))

            attributes_a = in_table['Input A'].get_attributes()
            attributes_b = in_table['Input B'].get_attributes()
            attributes_c = tuple(dict(itertools.chain(attributes_a[i].items(),
                                                      attributes_b[i].items()))
                                 for i in range(2))
            out_table['Output'].set_attributes(attributes_c)


MergeTable = node_helper._table_node_factory(
    'MergeTable', MergeTableOperation,
    'Merge Table', 'org.sysess.data.table.mergetable')

MergeTables = node_helper._tables_node_factory(
    'MergeTables', MergeTableOperation,
    'Merge Tables', 'org.sysess.data.table.mergetables')
