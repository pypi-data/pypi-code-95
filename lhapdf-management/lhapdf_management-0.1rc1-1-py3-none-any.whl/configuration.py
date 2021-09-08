"""
    LHAPDF configuration environment

    It exposes an object (environment) that should contain
    all relevant external information
"""
import os
import re
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Some useful harcoded values
INDEX_FILENAME = "pdfsets.index"
CVMFSBASE = "/cvmfs/sft.cern.ch/lcg/external/lhapdfsets/current/"
URLBASE = r"http://lhapdfsets.web.cern.ch/lhapdfsets/current/"


class _Environment:
    """LHAPDF environment"""

    # TODO take control of the logger

    def __init__(self):
        cvmfs_base = os.environ.get("LHAPDF_CVMFSBASE", CVMFSBASE)
        url_base = os.environ.get("LHAPDF_URLBASE", URLBASE)
        self._sources = [cvmfs_base, url_base]
        self._datapath = _get_lhapdf_datapath()
        self._index_filename = INDEX_FILENAME
        self._listdir = self.datapath

    @property
    def sources(self):
        """Iterator of all sources"""
        for source in self._sources:
            yield source

    @property
    def datapath(self):
        return self._datapath

    @datapath.setter
    def datapath(self, new_datapath):
        """Set the LHAPDF datapath"""
        new_path = Path(new_datapath)
        if not new_path.is_dir():
            logger.error(
                "The new LHAPDF data path %s is not a directory but I'll believe you", new_path
            )
        self._datapath = new_path

    @property
    def listdir(self):
        return self._listdir

    @property
    def index_filename(self):
        return self._index_filename

    def add_source(self, new_source):
        """Adds a source to the environment
        New sources take priority
        """
        self._sources = [new_source] + self._sources


def _get_lhapdf_datapath():
    """Look for the LHAPDF data folder
    The look-for order is:
    LHAPDF_DATA_PATH, LHAPATH, current prefix
    """
    # Look at environ variables
    for i in ["LHAPDF_DATA_PATH", "LHAPATH"]:
        val = os.environ.get(i)
        if val is not None:
            return Path(val)
    # If we didn't find it in the environment variables, autodiscover prefix
    find_prefix = re.compile(r".*/lib/python3.\d*/site-packages.*")
    prefix_path = Path("/usr")
    if find_prefix.findall(__file__):
        prefix_path = Path(find_prefix.split(__file__)[0])
    lhapdf_path = prefix_path / "share/LHAPDF/lhapdf"
    if lhapdf_path.exists():
        return lhapdf_path
    # Ok, now we have an actual problem, try asking some old lhapdf installation...
    try:
        import lhapdf

        return Path(lhapdf.paths()[0])
    except ImportError:
        logger.error(
            "Data directory for LHAPDF not found, you can use the LHAPDF_DATA_PATH environ variable"
        )
        raise FileNotFoundError("No data directory for LHAPDF found")


environment = _Environment()
