from botnoi import botnoigooglesheet as bg
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import numpy as np
import os
cpath = os.path.join(os.path.dirname(bg.__file__),'credentials.json')

class botnoigsheet():
    def __init__(self,sheeturl,sheetindex=0,credentialjson=cpath):
        scope = ['https://www.googleapis.com/auth/spreadsheets']
        creds = ServiceAccountCredentials.from_json_keyfile_name(credentialjson, scope)
        client = gspread.authorize(creds)
        s = client.open_by_url(sheeturl)
        s = s.get_worksheet(index=sheetindex)
        self.sheet = s

    def getalldata(self):
        d = np.array(self.sheet.get_all_values())
        d = pd.DataFrame(data=d[1:,:],columns=d[0,:])
        self.dat = d

    def dump_df_tosheet(self,df):
        self.sheet.delete_row(1)
        colList = [''] + list(df.columns.astype('str'))
        self.sheet.insert_row(colList,1)
        for i in range(len(df)):
            self.sheet.delete_row(i+2)
            val = list(df.iloc[i].astype('str').values)
            self.sheet.insert_row(val,i+2)

    def updatecell(self,selectcol,selectvalue,replacecol,replacevalue):
        rowpos, colpos, value = self.getcellvalue(selectcol,selectvalue,replacecol)
        self.sheet.update_cell(rowpos,colpos,replacevalue)
        return 'updated'

    def getcellvalue(self,selectcol,selectvalue,replacecol):
        colpos = self.sheet.find(selectcol,in_row=0).col
        rowpos = self.sheet.find(selectvalue,in_column=colpos).row
        colvalpos = self.sheet.find(replacecol,in_row=0).col
        value = self.sheet.cell(rowpos, colvalpos).value
        result = {}
        result['updatedrow'] = rowpos
        result['updatedcol'] = colvalpos
        result['updatedvalue'] = value
        return result

    def getcol_fromcolname(self,selectcol):
        colpos = self.sheet.find(selectcol,in_row=0).col
        values_list = self.sheet.col_values(colpos)
        return values_list

    def getrow_fromcolnamevalue(self,selectcol,selectvalue):
        colpos = self.sheet.find(selectcol,in_row=0).col
        rowpos = self.sheet.find(selectvalue,in_column=colpos).row
        values_list = self.sheet.row_values(rowpos)
        return values_list

    def getcol_fromcolindex(self,colindex):
        values_list = self.sheet.col_values(colindex)
        return values_list

    def getrow_fromrowindex(self,rowindex):
        values_list = self.sheet.row_values(rowindex)
        return values_list