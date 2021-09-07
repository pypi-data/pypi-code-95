import pandas as pd
import pathlib
from pathlib import Path
import glob
import os, shutil
import time

class FileRegistry:
    filelist = ()
    ex = []

    def __init__(self, kind, name, ftype='csv', path=''):
        self.name = name
        if kind == 'options':
            self.path = '/Volumes/GoogleDrive/My Drive/Premind_Light/Xignite/Options/' + path + '/'
        elif kind == 'options_main':
            self.path = '/Volumes/GoogleDrive/My Drive/Premind_Light/Xignite/OptionsMain/' + path + '/'
        elif kind == 'daily_price':
            self.path = '/Volumes/GoogleDrive/My Drive/Premind_Light/Xignite/DailyPrice/' + path + '/'
        elif kind == 'xlsx':
            self.path = '/Volumes/GoogleDrive/My Drive/__Premind/6. Product-Tech/14. FraudArb' + path + '/'
        elif kind == 'historic':
            self.path = '/Volumes/GoogleDrive/My Drive/__Premind/6. Product-Tech/14. FraudArb/HistoricData' + path + '/'
        elif kind == 'historic_ticker':
            self.path = '/Volumes/GoogleDrive/My Drive/__Premind/6. Product-Tech/14. FraudArb/Articles' + path + '/'
        elif kind == 'ticker':
            self.path = '/Volumes/GoogleDrive/My Drive/__Python/Premind_Light/Analytics/Analytics_Cloud/Analytics_Docker/data/FraudArb/Tickers' + path + '/'

        if ftype == "":
            self.fullpath = self.path + name
        else:
            self.fullpath = self.path + name + '.' + ftype

        flist = list(self.filelist)
        flist.append(self.name)
        self.filelist = tuple(flist)

    def file_exists(self):
        return Path(self.fullpath).is_file()

    def move_rename(self):
        downloads = '/Users/burakozkan/downloads/'
        pathlib.Path(self.path).mkdir(parents=True, exist_ok=True)
        time.sleep(2)
        list_of_files = glob.glob(downloads + '/*.csv')  # * means all if need specific format then *.csv
        filename = max(list_of_files, key=os.path.getctime)
        shutil.move(os.path.join(downloads, filename), os.path.join(self.path, self.name))

    def just_move(self):
        new_path = '/Users/burakozkan/MarketData/xdaily'
        shutil.move(os.path.join(self.path, self.name), os.path.join(new_path, self.name))

    def get_data(self):
        if 'EURO' in self.name and 'static_data' in self.path:
            df = pd.read_csv(self.fullpath, sep=';', parse_dates=True, skiprows=[1, 2, 3])
            df = df.rename(columns={'Name': 'Name1', 'Symbol': 'Symbol1'})
            df.insert(1, 'Symbol', df['Symbol1'])
            df.insert(0, 'Name', df['Name1'])
            return df
        return pd.read_csv(self.fullpath, parse_dates=True)

    def export_data(self, data_list, append=False):
        if append and self.file_exists():
            pd.read_csv(self.fullpath).append(data_list).to_csv(self.fullpath, encoding='utf-8', index=False)
        else:
            pathlib.Path(self.path).mkdir(parents=True, exist_ok=True)
            data_list.to_csv(self.fullpath, encoding='utf-8', index=False)

    def export_data_indexed(self, data_list):
        pathlib.Path(self.path).mkdir(parents=True, exist_ok=True)
        data_list.to_csv(self.fullpath, encoding='utf-8', index=True)
