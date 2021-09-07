import os
import copy
import datetime
import numpy as np
import pandas as pd
from finlab import data

import sys

class FinlabDataFrame(pd.DataFrame):

    @property
    def _constructor(self):
        return FinlabDataFrame

    @staticmethod
    def reshape(df1, df2):

        if isinstance(df2, pd.Series):
            df2 = pd.DataFrame({c:df2 for c in df1.columns})

        if isinstance(df2, FinlabDataFrame) or isinstance(df2, pd.DataFrame):
            index = df1.index.union(df2.index)
            columns = df1.columns.intersection(df2.columns)
            return df1.reindex(index=index,columns=columns, method='ffill'), \
            df2.reindex(index=index,columns=columns, method='ffill')
        else:
            return df1, df2

    def __lt__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__lt__(df1, df2)

    def __gt__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__gt__(df1, df2)

    def __le__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__le__(df1, df2)

    def __ge__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__ge__(df1, df2)

    def __eq__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__eq__(df1, df2)

    def __ne__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__ne__(df1, df2)

    def __sub__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__sub__(df1, df2)

    def __add__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__add__(df1, df2)

    def __mul__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__mul__(df1, df2)

    def __truediv__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__truediv__(df1, df2)

    def __rshift__(self, other):
        return self.shift(-other)

    def __lshift__(self, other):
        return self.shift(other)

    def __and__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__and__(df1, df2)

    def __or__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__or__(df1, df2)

    def average(self, n):
        return self.rolling(n, min_periods=int(n/2)).mean()

    def is_largest(self, n):
        return self.apply(lambda s: s.nlargest(n), axis=1).notna()

    def is_smallest(self, n):
        return self.apply(lambda s: s.nsmallest(n), axis=1).notna()

    def is_entry(self):
        return (self & ~self.shift(fill_value=False))

    def is_exit(self):
        return (~self & self.shift(fill_value=False))

    def rise(self, n=1):
        return self > self.shift(n)

    def fall(self, n=1):
        return self < self.shift(n)

    def groupby_category(self):
        categories = data.get('security_categories')
        cat = categories.set_index('stock_id').category.to_dict()
        org_set = set(cat.values())
        set_remove_illegal = set(o for o in org_set if isinstance(o, str) and o != 'nan')
        set_remove_illegal

        refine_cat = {}
        for s, c in cat.items():
            if c == None or c == 'nan':
                refine_cat[s] = '其他'
                continue

            if c == '電腦及週邊':
                refine_cat[s] = '電腦及週邊設備業'
                continue

            if c[-1] == '業' and c[:-1] in set_remove_illegal:
                refine_cat[s] = c[:-1]
            else:
                refine_cat[s] = c

        col_categories = pd.Series(self.columns.map(lambda s:refine_cat[s] if s in cat else '其他'))

        return self.groupby(col_categories.values, axis=1)

    def entry_price(self, trade_at='close'):

        signal = self.is_entry()
        adj = data.get('etl:adj_close') if trade_at == 'close' else data.get('etl:adj_open')
        adj, signal = adj.reshape(adj.loc[signal.index[0] : signal.index[-1]], signal)
        return adj.bfill()[signal.shift(fill_value=False)].ffill()

    def sustain(self, nwindow, nsatisfy=None):
        nsatisfy = nsatisfy or nwindow
        return self.rolling(nwindow).sum() >= nsatisfy

    def quantile_row(self, c):
        s = self.quantile(c, axis=1)
        return s

    def exit_when(self, exit):

        df, exit = self.reshape(self, exit)

        df.fillna(False, inplace=True)
        exit.fillna(False, inplace=True)

        entry_signal = df.is_entry()
        exit_signal = df.is_exit()
        exit_signal |= exit

        # build position using entry_signal and exit_signal
        position = pd.DataFrame(np.nan, index=df.index, columns=df.columns)
        position[entry_signal] = 1
        position[exit_signal] = 0

        position.ffill(inplace=True)
        position = position == 1
        position.fillna(False)
        return position

    def hold_until(self, exit, nstocks_limit=100, stoploss=-np.inf, takeprofit=np.inf, trade_at='close', rank=None):

        union_index = self.index.union(exit.index)
        intersect_col = self.columns.intersection(exit.columns)

        if stoploss != -np.inf or takeprofit != np.inf:
            price = data.get(f'etl:adj_{trade_at}')
            union_index = union_index.union(price.loc[union_index[0]: union_index[-1]].index)
            intersect_col = intersect_col.intersection(price.columns)
        else:
            price = pd.DataFrame()

        if rank is not None:
            union_index = union_index.union(rank.index)
            intersect_col = intersect_col.intersection(rank.columns)

        entry = self.reindex(union_index, columns=intersect_col, method='ffill').ffill().fillna(False)
        exit = exit.reindex(union_index, columns=intersect_col, method='ffill').ffill().fillna(False)

        if price is not None:
            price = price.reindex(union_index, columns=intersect_col, method='ffill')

        if rank is not None:
            rank = rank.reindex(union_index, columns=intersect_col, method='ffill')
        else:
            rank = pd.DataFrame(1, index=union_index, columns=intersect_col)

        max_rank = rank.max().max()
        min_rank = rank.min().min()
        rank = (rank - min_rank) / (max_rank - min_rank)
        rank.fillna(0, inplace=True)

        def rotate_stocks(ret, entry, exit, nstocks_limit, stoploss=-np.inf, takeprofit=np.inf, price=None, ranking=None):

            nstocks = 0

            ret[0][np.argsort(entry[0])[-nstocks_limit:]] = 1
            ret[0][exit[0] == 1] = 0
            ret[0][entry[0] == 0] = 0

            entry_price = np.empty(entry.shape[1])
            entry_price[:] = np.nan

            for i in range(1, entry.shape[0]):

                # regitser entry price
                if stoploss != -np.inf or takeprofit != np.inf:
                    is_entry = ((ret[i-2] == 0) if i > 1 else (ret[i-1] == 1)) & (ret[i-1] == 1)
                    is_waiting_for_entry = np.isnan(entry_price) & (ret[i-1] == 1)
                    is_entry |= is_waiting_for_entry
                    entry_price[is_entry == 1] = price[i][is_entry == 1]

                    # check stoploss and takeprofit
                    returns = price[i] / entry_price
                    stop = (returns > 1 + abs(takeprofit)) | (returns < 1 - abs(stoploss))
                    exit[i] |= stop

                # run signal
                rank = (1 - exit[i]) * (entry[i] * ranking[i] + ret[i-1] * 3)
                ret[i][np.argsort(rank)[-nstocks_limit:]] = 1
                ret[i][exit[i] == 1] = 0
                ret[i][(entry[i] == 0) & (ret[i-1] == 0)] = 0

            return ret

        ret = pd.DataFrame(0, index=entry.index, columns=entry.columns)
        ret = rotate_stocks(ret.values,
                entry.astype(int).values,
                exit.astype(int).values,
                nstocks_limit,
                stoploss,
                takeprofit,
                price=price.values,
                ranking=rank.values)

        return pd.DataFrame(ret, index=entry.index, columns=entry.columns)
