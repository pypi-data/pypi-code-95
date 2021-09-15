# pkgs/sage-conf/sage_conf.py.  Generated from sage_conf.py.in by configure.

VERSION = "9.4"

# The following must not be used during build to determine source or installation
# location of sagelib.  See comments in SAGE_ROOT/src/Makefile.in
# These variables come first so that other substituted variable values can refer
# to it.
SAGE_LOCAL = "/Users/mkoeppe/s/sage/sage-rebasing/worktree-dist/.tox/local-macos-10.15-nohomebrew-python3_xcode/local"
SAGE_ROOT = "/Users/mkoeppe/s/sage/sage-rebasing/worktree-dist"

MAXIMA = "/Users/mkoeppe/s/sage/sage-rebasing/worktree-dist/.tox/local-macos-10.15-nohomebrew-python3_xcode/local/bin/maxima"

# Delete this line if your ECL can load maxima without further prodding.
MAXIMA_FAS = "${prefix}/lib/ecl/maxima.fas".replace('${prefix}', SAGE_LOCAL)

# Delete this line if your ECL can load Kenzo without further prodding.
KENZO_FAS = "${prefix}/lib/ecl/kenzo.fas".replace('${prefix}', SAGE_LOCAL)

ARB_LIBRARY = "arb"

NTL_INCDIR = ""
NTL_LIBDIR = ""

# Path to the ecl-config script
ECL_CONFIG = "${prefix}/bin/ecl-config".replace('${prefix}', SAGE_LOCAL)

SAGE_NAUTY_BINS_PREFIX = ""

# Colon-separated list of pkg-config modules to search for cblas functionality.
# We hard-code it here as cblas because configure (build/pkgs/openblas/spkg-configure.m4)
# always provides cblas.pc, if necessary by creating a facade pc file for a system BLAS.
CBLAS_PC_MODULES = "cblas"

# for sage_setup.setenv
SAGE_ARCHFLAGS = ""
SAGE_PKG_CONFIG_PATH = "".replace('$SAGE_LOCAL', SAGE_LOCAL)

# Used in sage.repl.ipython_kernel.install
MATHJAX_DIR = SAGE_LOCAL + "/share/mathjax"
THREEJS_DIR = SAGE_LOCAL + "/share/threejs-sage"

# OpenMP flags, if available.
OPENMP_CFLAGS = ""
OPENMP_CXXFLAGS = ""

SAGE_SPKG_WHEELS = "/Users/mkoeppe/s/sage/sage-rebasing/worktree-dist/.tox/local-macos-10.15-nohomebrew-python3_xcode/local/var/lib/sage/wheels"

# Entry point 'sage-config'.  It does not depend on any packages.

def _main():
    from argparse import ArgumentParser
    from sys import exit, stdout
    parser = ArgumentParser()
    parser.add_argument('--version', help="show version", action="version",
                       version='%(prog)s ' + VERSION)
    parser.add_argument("VARIABLE", nargs='?', help="output the value of VARIABLE")
    args = parser.parse_args()
    d = globals()
    if args.VARIABLE:
        stdout.write('{}\n'.format(d[args.VARIABLE]))
    else:
        for k, v in d.items():
            if not k.startswith('_'):
                stdout.write('{}={}\n'.format(k, v))

if __name__ == "__main__":
    _main()
