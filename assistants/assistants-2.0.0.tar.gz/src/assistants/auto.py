from __future__ import annotations

from pathlib import Path

try:
    import compass.core as ci
except ImportError:
    raise ImportError("Missing optional dependency 'compass.core'. Use pip or conda to install compass-interface-core.") from None

from compass.core import login

__all__ = ("login", "appointments_report", "disclosures_report", "training_report", )


def appointments_report(export_path: Path, *, api: ci.CompassInterface, formats: ci.TYPES_FORMAT_CODES = ("CSV",)) -> None:
    exported_reports = api.reports.appointments(formats)
    _write_exported(export_path, exported_reports)


def disclosures_report(export_path: Path, api: ci.CompassInterface, formats: ci.TYPES_FORMAT_CODES = ("CSV",)) -> None:
    exported_reports = api.reports.disclosure_management(formats)
    _write_exported(export_path, exported_reports)


def training_report(export_path: Path, api: ci.CompassInterface, formats: ci.TYPES_FORMAT_CODES = ("CSV",)) -> None:
    exported_reports = api.reports.training(formats)
    _write_exported(export_path, exported_reports)


def _write_exported(export_path: Path, exported_reports: ci.TYPES_EXPORTED_REPORTS) -> None:
    if "CSV" in exported_reports:
        export_path.with_suffix(".csv").write_bytes(exported_reports["CSV"])
    if "EXCEL" in exported_reports:
        export_path.with_suffix(".xlsx").write_bytes(exported_reports["EXCEL"])
    if "XML" in exported_reports:
        export_path.with_suffix(".xml").write_bytes(exported_reports["XML"])
