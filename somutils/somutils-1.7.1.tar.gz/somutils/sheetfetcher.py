#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io, sys
import json
import gspread
from consolemsg import error, fail

class SheetFetcher():

    def __init__(self, documentName, credentialFilename):
        from oauth2client.service_account import ServiceAccountCredentials
        try:
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                credentialFilename,
                scopes=['https://spreadsheets.google.com/feeds',
                        'https://www.googleapis.com/auth/drive',],
                )
        except Exception as e:
            fail(str(e))

        gc = gspread.authorize(credentials)
        try:
            self.doc = gc.open(documentName)
        except Exception as e:
            credentialContent = json.load(io.open(credentialFilename))
            error("No s'ha trobat el document, o no li has donat permisos a l'aplicacio")
            error("Cal compartir el document '{}' amb el següent correu:"
                .format(documentName,credentialContent['client_email']))
            error(str(e))
            sys.exit(-1)

    def _worksheet(self, selector):
        if type(selector) is int:
            return self.doc.get_worksheet(selector)

        for s in self.doc.worksheets():
            if selector == s.id: return s
            if selector == s.title: return s

        raise Exception("Worksheet '{}' not found".format(selector))

    def get_range(self, worksheetsSelector, rangeName):
        worksheet = self._worksheet(worksheetsSelector)
        cells = worksheet.range(rangeName)
        width = cells[-1].col-cells[0].col +1
        height = cells[-1].row-cells[0].row +1
        return [
            [cell.value for cell in row]
            for row in zip( *(iter(cells),)*width)
            ]

    def get_fullsheet(self, worksheetsSelector):
        workSheet = self._worksheet(worksheetsSelector)
        return workSheet.get_all_values()

    def get_sheets(self):
        sheets = []
        for c, s in enumerate(self.doc.worksheets()):
            sheets.append((c, s.title, s.id))
        return sheets

    def add_to_last_row(self, worksheetsSelector, values):
        workSheet = self._worksheet(worksheetsSelector)
        last_index = len(workSheet.get_all_values()) + 1
        workSheet.insert_row(values, last_index)

    def add_to_first_row(self, worksheetsSelector, values):
        workSheet = self._worksheet(worksheetsSelector)
        workSheet.insert_row(values)
