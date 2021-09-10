# This file is part of Sympathy for Data.
# Copyright (c) 2013, 2017, Combine Control Systems AB
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
Convert a table with file paths to a list of data sources. The list will
contain one element for each row of the incoming table.

In the configuration GUI it is possible to select the column that contains the
file paths.
"""
import os.path
from sympathy.api import node as synode
from sympathy.api import datasource as dsrc
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, adjust
from sympathy.api.exceptions import sywarn
from sylib import datasource_conversion as dc


class SuperNode(synode.Node):
    author = 'Greger Cronquist'
    version = '1.1'
    icon = 'table2dsrc.svg'
    related = ['org.sysess.sympathy.data.table.tabletodsrcs',
               'org.sysess.sympathy.data.table.tablestodsrcs',
               'org.sysess.sympathy.data.table.dsrctotable']

    outputs = Ports([Port.Datasources('Datasources')])

    parameters = synode.parameters()
    parameters.set_list(
        'files', label='File names',
        description='Column containing the filenames',
        editor=synode.Util.combo_editor(edit=True))
    dc.set_input_relative_subflow_param(parameters)

    def verify_parameters(self, node_context):
        return node_context.parameters['files'].selected is not None

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['files'], node_context.input[0])


class TableToDsrc(SuperNode):
    """
    Export of data from Table to Datasources.

    For an explanation of relative datasource file paths, see
    :ref:`datasource_node_file`.

    """

    name = 'Table to Datasources'
    description = ('Convert a table with file paths into a list of data '
                   'sources pointing to those files.')
    nodeid = 'org.sysess.sympathy.data.table.tabletodsrcs'
    tags = Tags(Tag.DataProcessing.Convert)

    inputs = Ports([Port.Table('Table containing a column of filepaths.')])

    def execute(self, node_context):
        filenames_col = node_context.parameters['files'].selected
        create_datasources(
            filenames_col, node_context.input[0], node_context.output[0],
            dc.flow_path(node_context.parameters['subpath']))


class TablesToDsrc(SuperNode):
    """
    Export of data from Table to Datasources.

    For an explanation of relative datasource file paths, see
    :ref:`datasource_node_file`.

    """

    name = 'Tables to Datasources'
    description = ('Convert a list of tables with file paths into a list of '
                   'data sources pointing to those files.')
    nodeid = 'org.sysess.sympathy.data.table.tablestodsrcs'
    tags = Tags(Tag.DataProcessing.Convert)

    inputs = Ports([Port.Tables('Tables containing a column of filepaths.')])

    def execute(self, node_context):
        flow_path = dc.flow_path(node_context.parameters['subpath'])
        filenames_col = node_context.parameters['files'].selected
        for infile in node_context.input[0]:
            create_datasources(
                filenames_col, infile, node_context.output[0], flow_path)


def create_datasources(filenames_col, infile, outfile_list, flow_path):
    if filenames_col in infile:
        filenames = infile.get_column_to_array(filenames_col)
    else:
        sywarn('The selected column does not seem to exist. '
               'Assuming empty input.')
        filenames = []
    for f in filenames:
        outfile = dsrc.File()
        outfile.encode_path(_format_path(f, flow_path))
        outfile_list.append(outfile)


def _format_path(path, flow_path):
    if flow_path:
        return os.path.abspath(os.path.join(flow_path, path))
    else:
        return os.path.abspath(path)
