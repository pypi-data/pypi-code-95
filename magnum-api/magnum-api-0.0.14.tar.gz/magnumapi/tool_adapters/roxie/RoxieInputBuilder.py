import pandas as pd

from magnumapi.tool_adapters.roxie import RoxieAPI


class RoxieInputBuilder:
    """ Class RoxieInputBuilder builds a ROXIE input

    """

    comment = ''
    bhdata_path = ''
    cadata_path = ''
    iron_path = ''
    flags = {'LEND': False, 'LWEDG': False, 'LPERS': False, 'LQUENCH': False, 'LALGO': False, 'LMIRIRON': False,
             'LBEMFEM': False, 'LPSI': False, 'LSOLV': False, 'LIRON': False, 'LMORPH': False, 'LHARD': False,
             'LPOSTP': False, 'LPEAK': True, 'LINMARG': False, 'LMARG': True, 'LSELF': False, 'LMQE': False,
             'LINDU': False, 'LEDDY': False, 'LSOLE': False, 'LFIELD3': False, 'LFISTR': False, 'LSELF3': False,
             'LBRICK': False, 'LLEAD': False, 'LVRML': False, 'LOPERA': False, 'LOPER20': False, 'LANSYS': False,
             'LRX2ANS': False, 'LANS2RX': False, 'LDXF': False, 'LMAP2D': False, 'LMAP3D': False, 'LEXPR': False,
             'LFIL3D': False, 'LFIL2D': False, 'LCNC': False, 'LANSYSCN': False, 'LWEIRON': False, 'LCATIA': False,
             'LEXEL': False, 'LFORCE2D': False, 'LAXIS': True, 'LIMAGX': False, 'LIMAGY': False, 'LRAEND': False,
             'LMARKER': False, 'LROLER2': False, 'LROLERP': False, 'LIMAGZZ': False, 'LSTEP': False, 'LIFF': False,
             'LICCA': False, 'LICC': False, 'LICCIND': False, 'LITERNL': False, 'LTOPO': False, 'LQUEN3': False,
             'LAYER': True, 'LEULER': True, 'LHEAD': True, 'LPLOT': True, 'LVERS52': True, 'LHARM': True,
             'LMATRF': False, 'LF3LIN': False}
    global2doption = pd.DataFrame()
    global3d = pd.DataFrame()
    block = pd.DataFrame()
    blockoption = pd.DataFrame()
    block3d = pd.DataFrame()
    lead = pd.DataFrame()
    brick = pd.DataFrame()

    def set_flag(self, flag_name: str, flag_value: bool) -> "RoxieInputBuilder":
        """ Method setting a flag in a ROXIE input file. An error is thrown if a flag does not exist

        :param flag_name: name of a flag
        :param flag_value: value of a flag
        :return: an updated RoxieInputBuilder instance
        """
        if flag_name in self.flags.keys():
            self.flags[flag_name] = flag_value
        else:
            raise KeyError('Key')
        return self

    def build(self, template_path: str, output_path: str) -> None:
        """ Method building a ROXIE input based on a template file

        :param template_path: path to a template file
        :param output_path: an output path for the input .data file
        """
        output_str = self.prepare_data_file_str()

        # Read template file
        with open(template_path, 'r') as template_file:
            template_content = template_file.read()

        with open(output_path, 'wb') as input_file:
            input_file.write(bytes(template_content.format(output_str), 'utf-8').replace(b'\r\n', b'\n'))

    def prepare_data_file_str(self) -> str:
        """ Method preparing a data file string content

        :return: a string with lines for an input data file
        """
        outputs = ['VERSION 10.2.1',
                   '\'%s\'' % self.comment,
                   '\'%s\'' % self.bhdata_path,
                   '\'%s\'' % self.cadata_path,
                   '\'%s\'' % self.iron_path,
                   '\n'
                   '&OPTION']
        # Add OPTION
        outputs.append(RoxieInputBuilder.convert_flag_dct_to_str(self.flags))
        # Add GLOBAL2DOPTION
        RoxieInputBuilder.append_to_outputs(outputs, 'GLOBAL2DOPTION', self.global2doption)
        # Add GLOBAL3D
        RoxieInputBuilder.append_to_outputs(outputs, 'GLOBAL3D', self.global3d)
        # Add BLOCK
        RoxieInputBuilder.append_to_outputs(outputs, 'BLOCK', self.block)
        # Add BLOCKOPTION
        RoxieInputBuilder.append_to_outputs(outputs, 'BLOCKOPTION', self.blockoption)
        # Add BLOCK3D
        RoxieInputBuilder.append_to_outputs(outputs, 'BLOCK3D', self.block3d)
        # Add LEAD
        RoxieInputBuilder.append_to_outputs(outputs, 'LEAD', self.lead)
        # Add BRICK
        RoxieInputBuilder.append_to_outputs(outputs, 'BRICK', self.brick)
        return '\n'.join(outputs)

    @staticmethod
    def convert_flag_dct_to_str(flags: dict) -> str:
        """ Static method converting a dictionary with flags into a formatted string

        :param flags: a dictionary with flags
        :return: a formatted string representation of the dictionary with flags
        """
        COLUMN_WIDTH = 11
        flag_per_line_count = 1
        flag_str = '  '
        for key, value in flags.items():
            temp = "%s=%s" % (key, "T" if value else "F")
            temp += (COLUMN_WIDTH - len(temp)) * ' '
            if flag_per_line_count < 6:
                flag_str += temp
                flag_per_line_count += 1
            else:
                flag_str += temp + "\n  "
                flag_per_line_count = 1

        flag_str += '\n  /'
        return flag_str

    @staticmethod
    def append_to_outputs(outputs, keyword, df) -> None:
        """ Static method appending to the output list (in place) a dataframe with a keyword

        :param outputs: a list of outputs for an input file
        :param keyword: a table keyword
        :param df: a dataframe
        """
        outputs.append('')
        outputs.append(RoxieAPI.convert_bottom_header_table_to_str(df, keyword))
