#!/user/bin/env python
"""
w7x option starter
# TODO(@dboe) make this work after refactoring
"""
import sys
import argparse
import os
import numpy as np

import rna
import tfields
import w7x


def diffuse(args):
    """
    diffuse a extended vmec run and save the result
    """
    raise NotImplementedError("Paths should be set by user.")
    local_dir = rna.path.resolve("~/Data/EXTENDER/{args.vmec_id}/".format(**locals()))
    dat_path = os.path.join(local_dir, "{args.vmec_id}.dat".format(**locals()))

    cyl = w7x.extender.getHybridFromDat(dat_path)
    grid = w7x.flt.Grid(cylinder=cyl)
    config = w7x.flt.MagneticConfig.from_dat_file(dat_path, grid=grid)
    run = w7x.flt.Run(config)

    save_dir = os.path.join(args.baseDir, "{args.vmec_id}".format(**locals()))
    rna.path.mkdir(save_dir, is_dir=True)
    path = rna.path.resolve(
        os.path.join(save_dir, "{args.vmec_id}-fld.nest.npz".format(**locals()))
    )
    connection_length, component_loads, start_points = run.line_diffusion(
        startPoints=args.start_points
    )


def poincare(args):
    """poincare plot creation"""
    phiList = args.phi.values

    if args.phi.deg:
        phiList = [val / 180 * np.pi for val in phiList]

    if not args.assemblies.off:
        machine = w7x.flt.Machine.from_mm_ids(*args.assemblies.values)
    else:
        machine = w7x.flt.Machine()

    relativeCurrents = args.magnetic_config.relativeCurrents
    dat_path = args.magnetic_config.path
    if dat_path:
        dat_path = tfields.lib.in_out.resolve(dat_path)
        cyl = w7x.extender.getHybridFromDat(dat_path)
        grid = w7x.flt.Grid(cylinder=cyl)
        magnetic_config = w7x.flt.MagneticConfig.from_dat_file(dat_path, grid=grid)
    elif relativeCurrents:
        magnetic_config = w7x.flt.MagneticConfig.from_currents(
            relativeCurrents=relativeCurrents
        )
    else:
        magnetic_config = w7x.flt.MagneticConfig.from_currents()

    """ plotting """
    axis = rna.plotting.gca(2)
    for phi in phiList:
        axis.grid(color="lightgrey")
        machine.plot_poincare(phi, axis=axis)
        magnetic_config.plot_poincare(phi, axis=axis)
        rna.plotting.save(
            "~/tmp/poincare-{phi:.4f}".format(**locals()), "png", "pgf", "pdf"
        )
        axis.clear()


def parse_args(args_):
    """Parse args."""
    # create the top-level parser
    parser = argparse.ArgumentParser(prog="w7x app")
    parser.add_argument(
        "--version",
        action="version",
        version="v" + w7x.__version__,
        help="Show program's version number and exit",
    )
    parser = argparse.ArgumentParser(prog="w7x app")

    # subparsers
    subparsers = parser.add_subparsers(help="sub-command help")

    # create the parser for the "extend" command
    parser_extend = subparsers.add_parser("extend", help="extend help")
    parser_extend.add_argument("vmec_id", type=str, help="vmec_id to extend")
    parser_extend.set_defaults(func=w7x.extender.extend)

    # create the parser for the "diffuse" command
    parser_diffuse = subparsers.add_parser("diffuse", help="diffuse help")
    parser_diffuse.add_argument("vmec_id", type=str, help="already extended vmec_id")
    parser_diffuse.add_argument(
        "--start_points",
        type=int,
        help="hit points = 2 * " "start_points (forward and backward).",
        default=12500,
    )
    parser_diffuse.add_argument(
        "--baseDir",
        type=str,
        default="~/Data/Strikeline/",
        help="already extended vmec_id",
    )
    parser_diffuse.set_defaults(func=diffuse)

    # create the parser for the "poincare" command
    parser_poincare = subparsers.add_parser("poincare", help="poincare help")
    parser_poincare.add_argument(
        "--baseDir",
        type=str,
        default="~/Data/Strikeline/",
        help="already extended vmec_id",
    )
    parser_poincare.add_argument(
        "--phi", dest="phi.values", nargs="*", type=float, default=[0.0]
    )
    parser_poincare.add_argument(
        "--phi.deg",
        dest="phi.deg",
        help="switch phi from radian to degree",
        action="store_true",
    )
    parser_poincare.add_argument(
        "--assemblies",
        dest="assemblies.values",
        nargs="+",
        type=str,
        default=w7x.Defaults.Machine.mm_ids,
    )
    parser_poincare.add_argument("--assemblies.off", action="store_true")
    parser_poincare.add_argument(
        "--magnetic_config.relativeCurrents",
        help="relative currents in case of vacuum config",
    )
    parser_poincare.add_argument(
        "--magnetic_config.coilConfig",
        help="set the coil config for the relative currents",
    )
    parser_poincare.add_argument(
        "--magnetic_config.path",
        default=None,
        help="create config with magnetic field grid at path",
    )
    parser_poincare.set_defaults(func=poincare)

    # If no arguments were used, print base-level help with possible commands.
    if len(args_) == 0:
        parser.print_help(file=sys.stderr)
        sys.exit(1)

    args_ = parser.parse_args(args_)
    # let argparse do the job of calling the appropriate function after
    # argument parsing is complete
    return args_.func(args_)


if __name__ == "__main__":
    _ = parse_args(sys.argv[1:])
