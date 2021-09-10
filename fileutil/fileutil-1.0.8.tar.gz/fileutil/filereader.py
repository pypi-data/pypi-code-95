import pandas as pd
from pathlib import Path


class FileReader:

    def _excel_engine(self, filepath, sheet_name=0, dtypes=None, **kwargs):
        sheets = pd.read_excel(filepath, sheet_name=sheet_name, engine='openpyxl', **kwargs)
        if not dtypes is None:
            if isinstance(sheets, dict):
                for name, sheet in sheets.items():
                    sheets[name] = self.trans_cols_dtype(sheet, dtypes)
            else:
                sheets = self.trans_cols_dtype(sheets, dtypes)
        return sheets

    def _csv_engine(self, filepath, encoding='gbk', dtypes=None, **kwargs):
        chunksize = 10000
        df = pd.read_csv(filepath, encoding=encoding, low_memory=False, chunksize=chunksize, **kwargs)
        chunklist = []
        for chunk in df:
            if not dtypes is None:
                chunk = self.trans_cols_dtype(chunk, dtypes)
            chunklist.append(chunk)
        return chunklist[0] if len(chunklist) == 1 else pd.concat(chunklist)

    def read_file(self, filepath, encoding='gbk', dtypes=None, sheet_name=None, **kwargs):
        filepath = Path(filepath)
        if not filepath.exists():
            raise ValueError('文件路径不存在')
        if '.xls' in filepath.__str__():
            kwargs.update(dtypes=dtypes, sheet_name=sheet_name)
            return self._excel_engine(filepath, **kwargs)
        else:
            kwargs.update(encoding=encoding, dtypes=dtypes)
            return self._csv_engine(filepath, **kwargs)

    def trans_cols_dtype(self, dataframe, newdtypes):
        for col, newtype in newdtypes.items():
            if str(dataframe[col].dtype) != newtype:
                try:
                    dataframe[col] = dataframe[col].astype(newtype)
                except Exception as e:
                    # 字符型数据转为数值型的数据时，如果元素内容包括非数组的字符，需要先将元素替换为nan
                    dataframe[col] = dataframe[col].replace(r'\D+', pd.NA, regex=True)
                    # 删除dataframe的nan
                    dataframe.dropna(inplace=True, how='any', subset=[col])
                    dataframe[col] = dataframe[col].astype(newtype)
        return dataframe
