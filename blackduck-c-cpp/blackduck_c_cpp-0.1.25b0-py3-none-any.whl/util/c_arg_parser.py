"""
Copyright (c) 2021 Synopsys, Inc.
Use subject to the terms and conditions of the Synopsys End User Software License and Maintenance Agreement.
All rights reserved worldwide.
"""

import configargparse
import os


class C_Parser:

    @staticmethod
    def required_dir_exists(path):
        # Check input does not contain spaces
        if not os.path.exists(path):
            msg = " No buildable directory found at {}".format(path)
            raise configargparse.ArgumentTypeError(msg)
        return path

    @staticmethod
    def str2bool(v):
        # convert possible options for boolean values into a bool itself.
        if isinstance(v, bool):
            return v
        if v.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif v.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise configargparse.ArgumentTypeError('Boolean value expected.')

    def __init__(self):
        # from: https://realpython.com/command-line-interfaces-python-argparse/

        self.parser = configargparse.ArgParser(description='Capture all build files and send for analysis.', )

        self.parser.add_argument('-c', '--config', is_config_file=True, help='Configuration file path.')

        # Add the arguments
        self.parser.add_argument('-bc', '--build_cmd',
                                 required=True,
                                 type=str,
                                 help='Command used to execute the build')

        self.parser.add_argument('-d', '--build_dir',
                                 required=True,
                                 type=C_Parser.required_dir_exists,
                                 help='Directory from which to run build')

        self.parser.add_argument('-Cov', '--coverity_root',
                                 required=True,
                                 type=C_Parser.required_dir_exists,
                                 help='Base directory for coverity')

        self.parser.add_argument('-cd', '--cov_output_dir',
                                 metavar='cov_output_dir',
                                 dest='cov_output_dir',
                                 default='',
                                 type=str,
                                 help='Target directory for coverity output files')

        self.parser.add_argument('-od', '--output_dir',
                                 metavar='output_dir',
                                 dest='output_dir',
                                 default='',
                                 type=str,
                                 help='Target directory for blackduck-c-cpp output files')

        self.parser.add_argument('-s', '--skip_build',
                                 type=C_Parser.str2bool,
                                 nargs='?',
                                 const=True,
                                 default=False,
                                 help='Skip build and use previously generated build data.')

        self.parser.add_argument('-v', '--verbose',
                                 metavar='verbose',
                                 type=C_Parser.str2bool,
                                 nargs='?',
                                 const=True,
                                 default=False,
                                 help='verbose mode selection')

        self.parser.add_argument('-proj', '--project_name',
                                 required=True,
                                 dest='project_name',
                                 type=str,
                                 help='Black Duck project name')

        self.parser.add_argument('-vers', '--project_version',
                                 required=True,
                                 dest='project_version',
                                 type=str,
                                 help='Black Duck project version')

        self.parser.add_argument('-Cl', '--codelocation_name',
                                 dest='codelocation_name',
                                 type=str,
                                 help='Codelocation name')

        self.parser.add_argument('-bd', '--bd_url',
                                 required=True,
                                 metavar='bd_url',
                                 type=str,
                                 help='Black Duck URL')

        self.parser.add_argument('-a', '--api_token',
                                 dest='api_token',
                                 required=True,
                                 metavar='api_token',
                                 type=str,
                                 help='Black Duck API token')

        self.parser.add_argument('-as', '--additional_sig_scan_args',
                                 metavar='additional_sig_scan_args',
                                 dest='additional_sig_scan_args',
                                 type=str,
                                 default=None,
                                 help='Any additional args to pass to the signature scanner')

        self.parser.add_argument('-i', '--insecure',
                                 dest='insecure',
                                 metavar='insecure',
                                 type=C_Parser.str2bool,
                                 nargs='?',
                                 const=True,
                                 default=False,
                                 help='Disable SSL verification')

        self.parser.add_argument('-djs', '--disable_json_splitter',
                                 dest='disable_json_splitter',
                                 type=C_Parser.str2bool,
                                 nargs='?',
                                 const=True,
                                 default=False,
                                 help='Disable the json splitter and always upload as a single scan')

        self.parser.add_argument('-si', '--scan_interval',
                                 dest='scan_interval',
                                 type=int,
                                 default=60,
                                 help='Set the number of seconds to wait between scan uploads in case of multiple scans')

        self.parser.add_argument('-jsl', '--json_splitter_limit',
                                 dest='json_splitter_limit',
                                 default=4750000000,
                                 metavar='json_splitter_limit',
                                 type=int,
                                 help='Set the limit for a scan size in bytes')

        self.parser.add_argument('-dg', '--debug',
                                 metavar='debug',
                                 type=C_Parser.str2bool,
                                 nargs='?',
                                 const=True,
                                 default=False,
                                 help='Debug mode selection')

        self.parser.add_argument('-st', '--skip_transitives',
                                 type=C_Parser.str2bool,
                                 nargs='?',
                                 const=True,
                                 default=False,
                                 help='Skipping all transitive dependencies')

        self.parser.add_argument('-sh', '--skip_includes',
                                 type=C_Parser.str2bool,
                                 nargs='?',
                                 const=True,
                                 default=False,
                                 help='Skipping all .h & .hpp files from all types of scan')

        self.parser.add_argument('-sd', '--skip_dynamic',
                                 type=C_Parser.str2bool,
                                 nargs='?',
                                 const=True,
                                 default=False,
                                 help='Skipping all .so files from all types of scan')

        self.parser.add_argument('-off', '--offline',
                                 type=C_Parser.str2bool,
                                 nargs='?',
                                 const=True,
                                 default=False,
                                 help='store bdba and sig tar files and c_cpp_bdio2.jsonld to disk if offline mode is true')

        self.parser.add_argument('-md', '--modes',
                                 metavar='modes',
                                 dest='modes',
                                 type=str,
                                 default="ALL",
                                 help="comma separated list of modes to run - 'all'(default),'bdba','sig','pkg_mgr'")

        self.parser.add_argument('-uo', '--use_offline_files',
                                 type=C_Parser.str2bool,
                                 nargs='?',
                                 const=True,
                                 default=False,
                                 help='use offline generated files for upload in online mode')

        self.parser.add_argument('-sc', '--scan_cli_dir',
                                 metavar='scan_cli_dir',
                                 dest='scan_cli_dir',
                                 default=None,
                                 type=str,
                                 help='scan cli directory')

        self.args = self.parser.parse_args()
