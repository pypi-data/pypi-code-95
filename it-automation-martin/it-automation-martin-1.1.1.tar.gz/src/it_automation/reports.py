#! /usr/bin/env python3
""" Functions for generating pdf reports. """
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Paragraph, Spacer, Table, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


def generate_report(report_path, title, paragraph):
    """ Generates pdf report with information passed into the function.

    Args:
        report_path(string): Path and name of report function will generate.

        title(string): Title in the report.

        paragraph(string): body text of the report.
    Returns:
        None
    """
    styles = getSampleStyleSheet()
    report = SimpleDocTemplate(report_path)
    report_title = Paragraph(title, styles["h1"])
    report_info = Paragraph(paragraph, styles["BodyText"])
    empty_line = Spacer(1, 20)
    report.build([report_title, empty_line, report_info])