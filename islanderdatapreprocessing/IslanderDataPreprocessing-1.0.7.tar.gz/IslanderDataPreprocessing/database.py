import os
import zipfile
import pandas as pd
class DataBase:
    def __init__(self,API_command):
        os.system(API_command)
        self.name = API_command.split('/')
        self.Open()
        os.remove(self.name[1]+".zip")
    def Open(self):
        self.dataset = []
        with zipfile.ZipFile(self.name[1]+".zip", "r") as zip:
            filenames = zip.namelist()
            zip.extractall()
        for i in filenames:
            self.dataset.append(pd.read_csv(i))
        self.filenames = filenames

