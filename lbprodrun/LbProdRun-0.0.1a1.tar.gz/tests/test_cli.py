###############################################################################
# (c) Copyright 2021 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
import json

from typer.testing import CliRunner

from LbProdRun.__main__ import app

runner = CliRunner()


def test_valid(tmp_path, monkeypatch):
    monkeypatch.setattr("os.execvpe", lambda *x: True)

    tmp_path = tmp_path / "prod_spec.json"
    tmp_path.write_text(
        json.dumps(
            {
                "spec_version": 1,
                "application": {
                    "name": "DaVinci",
                    "version": "v45r8",
                    "data_pkgs": ["AppConfig v3r405"],
                },
                "options": {
                    "format": "Merge",
                    "files": [
                        "$APPCONFIGOPTS/Merging/DVMergeDST.py",
                        "$APPCONFIGOPTS/DaVinci/DataType-2017.py",
                        "$APPCONFIGOPTS/Merging/WriteFSR.py",
                        "$APPCONFIGOPTS/Merging/MergeFSR.py",
                        "$APPCONFIGOPTS/Persistency/Compression-LZMA-4.py",
                        "$APPCONFIGOPTS/DaVinci/Simulation.py",
                    ],
                },
                "input": {
                    "files": [
                        "LFN:/lhcb/MC/2018/D02HHLL.STRIP.MDST/00145917/0000/00145917_00000643_7.D02hhll.Strip.mdst",
                        "LFN:/lhcb/MC/2018/D02HHLL.STRIP.MDST/00145917/0000/00145917_00000335_7.D02hhll.Strip.mdst",
                    ],
                    "xml_summary_file": "summaryDaVinci_00145918_00000004_1.xml",
                    "xml_file_catalog": "pool_xml_catalog.xml",
                },
                "output": {
                    "prefix": "00145918_00000004_1",
                    "types": ["d02hhll.strip.mdst"],
                },
                "db_tags": {
                    "dddb_tag": "dddb-20170721-3",
                    "conddb_tag": "sim-20190430-vc-md100",
                },
            }
        )
    )
    result = runner.invoke(app, str(tmp_path))
    assert result.exit_code == 0
    assert "DaVinci/v45r8" in result.stdout


def test_invalid_file(tmp_path):
    result = runner.invoke(app, str(tmp_path))
    assert result.exit_code != 0
    assert "is a directory" in result.stdout

    tmp_path = tmp_path / "prod_spec.json"

    result = runner.invoke(app, str(tmp_path))
    assert result.exit_code != 0
    assert "does not exist" in result.stdout

    tmp_path.write_text("")
    result = runner.invoke(app, str(tmp_path))
    assert result.exit_code >= 64
    assert "Failed to parse" in result.stdout

    tmp_path.write_text("{}")
    result = runner.invoke(app, str(tmp_path))
    assert result.exit_code >= 64
    assert "'spec_version' is not specified" in result.stdout

    tmp_path.write_text('{"spec_version": 1}')
    result = runner.invoke(app, str(tmp_path))
    assert result.exit_code >= 64
    assert "errors when validating" in result.stdout

    tmp_path.write_text('{"spec_version": 1000}')
    result = runner.invoke(app, str(tmp_path))
    assert result.exit_code >= 64
    assert "Unknown spec_version" in result.stdout
