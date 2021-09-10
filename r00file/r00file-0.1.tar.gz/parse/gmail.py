import csv, pyodbc
import re
import os
try:
    from .tools import recur
except:
    from r00fileparse.tools import recur


class ParseGmail:
    """Ищет gmail почты в файле и сохраняет их в файл"""
    def __init__(self, scr: str, dst: str):
        """
        Первоначальные настройки
        :param scr: Путь до папки или файла, где нужно найти почты
        :param dst: Путь до файла с результатом
        """
        self.scr = scr
        self.dst = dst


    def start(self):
        all_count = 0
        filepaths = recur(self.scr) if os.path.isdir(self.scr) else [self.scr]

        # Parse file
        for filepath in filepaths:
            result = set()
            print(f'Parse file {filepath}...')
            with open(filepath, encoding='utf-8', errors='ignore') as f:
                data = f.read()
            p = re.compile('([a-z0-9]\.?[a-z0-9]{5,}@gmail\.com)')
            filepath_result = p.findall(data, re.MULTILINE)
            [result.add(item) for item in filepath_result]
            all_count += len(filepath_result)
            print(f'    Count in file: {len(filepath_result)}, All: {all_count}')

            # Save file
            with open(self.dst, 'a') as f:
                f.write('\n'.join(str(item) for item in result))


if __name__ == '__main__':
    _infile = r"C:\Users\Administrator\Desktop\tasks"
    _outfile = r"C:\Users\Administrator\Desktop\res.txt"
    _parsegmail = ParseGmail(_infile, _outfile)
    _parsegmail.start()
