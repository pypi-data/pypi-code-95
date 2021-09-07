import desktop
import openpyxl

def LofterString(filename,sheetname,coordinate):
    workbook = openpyxl.load_workbook(filename=desktop.desktop(filename), data_only=True)
    worksheet = workbook[sheetname]
    cookie_list = [values[0].value for values in worksheet[coordinate]]
    return str(cookie_list).replace("'","").replace(" ","").replace("[","").replace("]","")

# LofterString('data.xlsx','Active','A3:A134')