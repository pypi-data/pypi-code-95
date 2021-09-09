import csv
import json
from io import StringIO
from typing import List, Dict

import openpyxl
from openpyxl.writer.excel import save_virtual_workbook


def load_json_file(path):
    content = ''
    with open(path, 'rb') as f:
        line = f.readline()
        while line:
            content += line.decode()
            line = f.readline()
    return json.loads(content)


def to_csv(titles: List[str], fields: List[str], data: List[Dict]):
    buffer = StringIO()
    csv_writer = csv.writer(buffer)
    csv_writer.writerow(titles)

    for d in data:
        csv_writer.writerow([d.get(f, '') for f in fields])

    return buffer


def to_excel(titles: List[str], fields: List[str], data: List[Dict]) -> bytes:
    wb = openpyxl.Workbook()
    ws = wb.active
    for index, title in enumerate(titles):
        ws.cell(1, index + 1, title)
    for d in data:
        ws.append([d.get(f, '') for f in fields])

    return save_virtual_workbook(wb)
