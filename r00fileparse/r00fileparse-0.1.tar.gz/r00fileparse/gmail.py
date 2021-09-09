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
        filepaths = recur(self.scr) if os.path.isdir(self.scr) else [self.scr]
        result = set()
        # Parse
        for filepath in filepaths:
            with open(filepath, encoding='utf-8', errors='ignore') as f:
                data = f.read()
            p = re.compile('([a-z0-9]\.?[a-z0-9]{5,}@gmail\.com)')
            [result.add(item) for item in p.findall(data, re.MULTILINE)]

        # Save
        with open(self.dst, 'w') as f:
            f.write('\n'.join(str(item) for item in result))


if __name__ == '__main__':
    _infile = r"C:\Users\Administrator\Desktop\immunization_covid19_2021_14.08.2021.csv"
    _infile = r"C:\Users\Administrator\Desktop\test.txt"
    _outfile = r"C:\Users\Administrator\Desktop\res.txt"
    _parsegmail = ParseGmail(_infile, _outfile)
    _parsegmail.start()
