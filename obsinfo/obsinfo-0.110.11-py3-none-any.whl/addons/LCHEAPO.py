"""
Write extraction script for LCHEAPO instruments (proprietary to miniseed)
"""
import obsinfo
from obsinfo.network import Network
from ..misc.discoveryfiles import (Datapath)
from ..obsMetadata.obsmetadata import (ObsMetadata)
import os.path

SEPARATOR_LINE = "\n# " + 60 * "=" + "\n"


def process_script(network_code,
                   station, station_dir, distrib_dir, input_dir=".",
                   output_dir="miniseed_basic", include_header=True):
    """
    Writes script to transform raw OBS data to miniSEED

    Arguments:
        network_code (str): FDSN network_code
        station (:class: ~obsinfo.Station): the station to process
        station_dir (str): the base directory for the station data
        distrib_dir (str): directory where the lcheapo executables and
                           property files are found
        input_dir (str): directory beneath station_dir for LCHEAPO data
        output_dir (str): directory beneath station_dir for basic miniseed]
        include_header (bool): include the header that sets up paths
                               (should be done once)
    """
    fixed_dir = "lcheapo_fixed"
    s = ""
    if include_header:
        s += __header(station.label)
    s += __setup_variables(distrib_dir, station_dir)
    s += __lcfix_commands(station, input_dir, fixed_dir)
    s += __lc2ms_commands(network_code, station, fixed_dir, output_dir)
    s += __force_quality_commands(output_dir, "D")

    return s


def __header(station_name):

    s = "#!/bin/bash\n"
    s += SEPARATOR_LINE + f'echo "Working on station {station_name}"' + SEPARATOR_LINE
    return s


def __setup_variables(distrib_dir, station_dir):
    """
    distrib_dir: directory containing lcheapo bin/ and config/ directories
                (with lcfix and lc2ms)
    station_dir: base directory for station data files
    """

    s = SEPARATOR_LINE + "# LCHEAPO STEPS" + SEPARATOR_LINE
    s += "#  - Set up paths\n"
    s += f"STATION_DIR={station_dir}\n"
    s += f"LCFIX_EXEC={os.path.join(distrib_dir,'bin','lcfix')}\n"
    s += f"LC2MS_EXEC={os.path.join(distrib_dir,'bin','lc2ms')}\n"
    s += f"LC2MS_CONFIG={os.path.join(distrib_dir,'config','lc2ms.properties')}\n"
    s += f"SDPPROCESS_EXEC={os.path.join(distrib_dir,'bin','sdp-process')}\n"
    s += f"MSMOD_EXEC={os.path.join('/opt/iris','bin','msmod')}\n"
    s += f"\n"
    return s


def __lcfix_commands(station, in_path, out_path, in_fnames="*.raw.lch"):

    """
        Write an lc2ms command line

        Inputs:
            in_path:       relative path to directory containing input files
            out_path:      relative path to directory for output files
            in_fnames:     search string for input files within in_path ['*.fix.lch']
         Output:
            string of bash script lines
    """

    s = f'echo "{"-"*60}"\n'
    s += 'echo "Running LCFIX: Fix common LCHEAPO data bugs"\n'
    s += f'echo "{"-"*60}"\n'
    s += f'in_dir="{in_path}"\n'
    s += f'out_dir="{out_path}"\n'

    s += "# - Create output directory\n"
    s += "mkdir $STATION_DIR/$out_dir\n"

    s += "# - Collect input filenames\n"
    s += "command cd $STATION_DIR/$in_dir\n"
    s += f"lchfiles=$(ls {in_fnames})\n"
    s += "command cd -\n"
    s += 'echo "lchfile(s): " $lchfiles\n'

    s += "# - Run executable\n"
    s += '$LCFIX_EXEC $lchfiles -d "$STATION_DIR" -i $in_dir -o $out_dir\n'
    s += "\n"

    return s


def __lc2ms_commands(network_code, station, in_path, out_path,
                     in_fnames="*.fix.lch",
                     out_fnames_model="%E.%S.00.%C.%Y.%D.%T.mseed",
                     force_quality_D=True):
    """
    Write an lc2ms command line

    Arguments:
        station (:class: ~obsinfo.Station): station to process
        in_path (str): relative path to directory containing input files
        in_fnames (str): search string for input files within in_path ['*.fix.lch']
        out_path (str): relative path to directory for output files
        out_fnames_model (str): model for output filenames (should change
            default to '%E.%S.%L.%C.%Y.%D.%T.mseed' once lc2ms handles
            location codes)
        force_quality_D: make a separate call to msmod to force the data
            quality to "D" (should be unecessary once lc2ms is upgraded)
    Returns:
        (str): bash script lines
    """

    network_code = network_code
    station_code = station.label
    obs_type = _get_ref_code(station.instrumentation)
    obs_SN = station.instrumentation.equipment.serial_number
    # CHANNEL CORRESPONDENCES WILL ALLOW THE CHANNEL NAMES TO BE EXPRESSED ON
    # THE COMMAND LINE, WITHOUT USING A DEDICATED CSV FILE
    # channel_corresp = station.instrument.channel_correspondances()

    s = f'echo "{"-"*60}"\n'
    s += 'echo "Running LC2MS: Transform LCHEAPO data to miniseed"\n'
    s += f'echo "{"-"*60}"\n'
    s += f'in_dir="{in_path}"\n'
    s += f'out_dir="{out_path}"\n'

    s += "# - Create output directory\n"
    s += "mkdir $STATION_DIR/$out_dir\n"

    s += "# - Collect input filenames\n"
    s += "command cd $STATION_DIR/$in_dir\n"
    s += f"lchfiles=$(ls {in_fnames})\n"
    s += "command cd -\n"
    s += 'echo "lchfile(s): " $lchfiles\n'

    s += "# - Run executable\n"
    s += '$LC2MS_EXEC $lchfiles -d "$STATION_DIR" -i $in_dir -o $out_dir '
    s += f'-m ":{out_fnames_model}" '
    s += f'--experiment "{network_code}" '
    s += f'--sitename "{station_code}" '
    s += f'--obstype "{obs_type}" '
    s += f'--sernum "{obs_SN}" '
    # s += f'--binding "{channel_corresp}"' '
    s += "-p $LC2MS_CONFIG\n"
    s += "\n"

    return s


def __force_quality_commands(rel_path, quality="D"):
    """ Forces miniseed files to have given quality ('D' by default)
    """
    s = f'echo "{"-"*60}"\n'
    s += f'echo "Forcing data quality to {quality}"\n'
    s += f'echo "{"-"*60}"\n'
    # THE FOLLOWING ASSUMES THAT SDP-PROCESS IS IN OUR PATH, NOT NECESSARILY THE CASE
    s += f'$SDPPROCESS_EXEC -d $STATION_DIR -c="Forcing data quality to {quality}" --cmd="$MSMOD_EXEC --quality {quality} -i {rel_path}/*.mseed"\n'
    s += "\n"
    return s


def _console_script(argv=None):
    """
    Create a bash-script to convert LCHEAPO data to basic miniSEED
    Data should be in station_data_path/{STATION_NAME}/{input_dir}/*.fix.lch

    requires O Dewee program lc2ms, and IRIS program msmod

    """
    from argparse import ArgumentParser

    parser = ArgumentParser(
        prog="obsinfo-make_process_scripts_LC2MS", description=__doc__
    )
    parser.add_argument("network_file", help="Network information file")
    parser.add_argument("station_data_path", help="Base path containing stations data")
    parser.add_argument("distrib_path", help="Path to lcheapo software distribution")
    parser.add_argument("-i", "--input_dir", default=".",
                        help="subdirectory of station_data_path/{STATION}/ "
                             "containing input *.raw.lch files")
    parser.add_argument("-o", "--output_dir", default="2_miniseed_basic",
                        help="subdirectory of station_data_path/{STATION}/ "
                             "to put output *.mseed files")
    parser.add_argument("--suffix", default="_LC2MS",
                        help="suffix for script filename")
    parser.add_argument("--append", action="store_true",
                        help="append to existing script file")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="increase output verbosity")
    parser.add_argument("--no_header", action="store_true",
                        help="do not include a script header")
    parser.add_argument("-q", "--quiet", action="store_true", help="run silently")
    args = parser.parse_args()

    if not args.quiet:
        print(f"Creating LC2MS process scripts, ", end="", flush=True)

    # READ IN NETWORK INFORMATION
    dp = Datapath()
    if args.verbose:
        print(f'Reading network file: {args.network_file}')
    args.network_file = str(Path(os.getcwd()).joinpath(args.network_file))
    info_dict = ObsMetadata.read_info_file(args.network_file, dp, False)
    net_dict = info_dict.get('network', None)
    if not net_dict:
        return 
    if args.verbose:
        print(f'Processing network file: {args.network_file}')
    network = Network(ObsMetadata(net_dict))
    # network = oi_Network(args.network_file)

    if not args.quiet:
        print(f"network {network.fdsn_code}, stations ", end="", flush=True)
        if args.verbose:
            print("")

    first_time = True
    for station in network.stations:
        if not args.quiet:
            if args.verbose:
                print(f"\t{station.label}", end="")
            else:
                if first_time:
                    print(f"{station.label}", end="", flush=True)
                else:
                    print(f", {station.label}", end="", flush=True)
        station_dir = os.path.join(args.station_data_path, station.label)
        script = process_script(
            network.fdsn_code,
            station,
            station_dir,
            args.distrib_path,
            input_dir=args.input_dir,
            output_dir=args.output_dir,
            include_header=not args.no_header,
        )
        fname = "process_" + station.label + args.suffix + ".sh"
        if args.verbose:
            print(f" ... writing file {fname}", flush=True)
        if args.append:
            write_mode = "a"
        else:
            write_mode = "w"
        with open(fname, write_mode) as f:
            # f.write('#'+'='*60 + '\n')
            f.write(script)
            f.close()
        first_time = False
    if not args.verbose and not args.quiet:
        print("")

def _get_ref_code(inst):
    """
    Returns the LCHEAPO reference code corresponding to the instrumentation
    
    Arguments:
        inst (:class: ~obsinfo.Instrumentation)
    """
    sps=50
    ch=inst.channels
    if len(ch) == 2:
        if (ch[0].channel_code(sps) == 'SH3' and \
                ch[1].channel_code(sps) == 'BDH'):
            return 'SPOBS1'
    elif len(ch) == 4:
        if   (ch[0].channel_code(sps) == 'BDH' and \
              ch[1].channel_code(sps) == 'SH2' and \
              ch[2].channel_code(sps) == 'SH1' and \
              ch[3].channel_code(sps) == 'SH3'):
            return 'SPOBS2'
        elif (ch[0].channel_code(sps) == 'BH2' and \
              ch[1].channel_code(sps) == 'BH1' and \
              ch[2].channel_code(sps) == 'BHZ' and \
              ch[3].channel_code(sps) == 'BDH'):
            return 'BBOBS1'
        elif (ch[0].channel_code(sps) == 'BDH' and \
              ch[1].channel_code(sps) == 'BDH' and \
              ch[2].channel_code(sps) == 'BDH' and \
              ch[3].channel_code(sps) == 'BDH'):
            return 'HYDROCT'
    return "UNKNOWN"
