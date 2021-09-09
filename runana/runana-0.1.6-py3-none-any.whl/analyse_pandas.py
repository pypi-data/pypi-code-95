#!/usr/bin/python
import pandas as pd

from runana.run import is_it_tuple
from runana.read_numbers import ignored
from runana import analyse


class SeqsDataFrame(pd.DataFrame):
    numparam = 'NumParam'
    numparamval = 'NumParamValue'

    @property
    def _constructor(self):
        return SeqsDataFrame

    def iterator(self):
        for numparam, data in self.iterator_outer():
            for column in data:
                dat = data[column]
                yield (numparam, column), dat

    def iterator_outer(self):
        for numparam in self.index.levels[0]:
            data = self.loc[(numparam)]
            data.sort_index(inplace=True)
            yield numparam, data

    def iterator_drop(self):
        for (numparam, column), dat in self.iterator():
            dat = dat.dropna()
            if not dat.empty:
                yield (numparam, column), dat

    def iterator_all(self):
        for (numparam, column), dat in self.iterator():
            for (numparamvalue, elem) in dat.iteritems():
                yield ((numparam, numparamvalue), column), elem

    def iterator_all_drop(self):
        for (numparam, column), dat in self.iterator_drop():
            for (numparamvalue, elem) in dat.iteritems():
                yield ((numparam, numparamvalue), column), elem

    def import_from_seq(self, seqsnew, varvals, inplace=False):
        """Converts the seqs object into a SeqsDataFrame"""
        seqsdf = self if inplace else self.copy()
        multiindx = pd.MultiIndex(levels=[[], []], codes=[[], []],
                                  names=[seqsdf.numparam, seqsdf.numparamval])
        seqsdf.set_index(multiindx, inplace=True)
        whatever_scalar = 'lol'
        list_ = list(iterate_seqs(seqsnew, varvals))
        for multi_idx, dir_ in list_:
            seqsdf.loc[multi_idx] = whatever_scalar
            # for multi_idx, dir_ in list_:
            # It might seem strange to repeat the same command twice, and indeed it is.
            # It seems that pandas unpacks a tuple of length 1 first time its inserted,
            # but not the second time...
            seqsdf.at[multi_idx] = dir_
            seqsdf.at[multi_idx] = dir_
        if not inplace:
            return seqsdf

    def calc_reldiff(self):
        """Calculate relative difference of values and numerical parameter values.

        `(O2-O1)/(x2-x1)` where `O` are values and `x` are numerical
        parameters.

        All numerical parameter values have to be scalar and numeric.

        Returns a new `SeqsDataFrame`.

        """
        import numpy as np
        data_out = self.copy()
        columns = list(self.columns)
        data_out = data_out.drop(columns=columns)
        for (numparam, column), data in self.iterator():
            data = data.reset_index(level=self.numparamval)
            relDiff = data.diff()
            RelErrorEstimate = relDiff[column]/relDiff[self.numparamval]
            RelErrorEstimate = RelErrorEstimate.apply(np.abs)
            RelErrorEstimate = pd.Series(RelErrorEstimate.values,
                                         data[self.numparamval])
            for numparamval in data[self.numparamval]:
                data_out.loc[(numparam, numparamval), str(column)+'_reldiff'] = RelErrorEstimate[numparamval]
        return data_out

    def calc_convergence(self):
        """Calculate an estimate for relative convergence error.

        Calculates `(O2-O1)/O2*x2/(x2-x1)` where `O` are values and `x`
        are numerical parameters, which is an estimate of the difference
        between the value calculated at the given numerical parameter
        and the "true" value of the fully converged limit.

        All numerical parameter values have to be scalar and numeric.

        Returns a new `SeqsDataFrame`.

        """
        import numpy as np
        try:
            data_out = self.copy()
            columns = list(self.columns)
            data_out = data_out.drop(columns=columns)
            for (numparam, column), data in self.iterator():
                data = data.reset_index(level=self.numparamval)
                relDiff = data.diff()/data
                RelErrorEstimate = relDiff[column]/relDiff[self.numparamval]
                RelErrorEstimate = RelErrorEstimate.apply(np.abs)
                RelErrorEstimate = pd.Series(RelErrorEstimate.values,
                                             data[self.numparamval])
                for numparamval in data[self.numparamval]:
                    data_out.loc[(numparam, numparamval), str(column)+'_conv'] = RelErrorEstimate[numparamval]
            return data_out
        except TypeError as e:
            print(str(e))
            raise TypeError("Make sure that "+self.numparamval+" and values in"
                            + " the SeqsDataFrame are all numerical and scalar")

    def calc_convergence_func(self, func):
        """ Calculate `func(O1,O2)*x2/(x2-x1)` where `O` are values and `x` are
 numerical parameters

        All numerical parameter values have to be scalar and numeric

        Returns a new SeqsDataFrame
        """
        import numpy as np
        data_out = self.copy()
        columns = list(self.columns)
        data_out = data_out.drop(columns=columns)
        for (numparam, column), data in self.iterator():
            # print('data data[1:]')
            # print(type(data))
            # print(data)
            # print(data.iloc[1:])
            # print(data.iloc[:-1])
            for (x1, O1), (x2, O2) in zip(data.iloc[:-1].iteritems(),
                                          data.iloc[1:].iteritems()):
                # idx = 
                # data_out.loc[idx] = np.abs(func(O1, O2)*x2/(x2-x1))
                try:
                    dat = np.abs(func(O1, O2)*x2/(x2-x1))
                    # print('dat', dat)
                except TypeError:
                    dat = np.nan
                data_out.loc[((numparam, x1), str(column)+'_conv')] = dat
        return data_out

    def plot_(self, outfile, logx=False, logy=False, grid=False,
              param_panda=None):
        """ Requires :mod:`numpy` and :mod:`matplotlib`"""
        from runana import matplotlib_managers as mplm
        import numpy as np
        with mplm.plot_manager(outfile=outfile) as pp:
            for numparam, data in self.iterator_outer():
                with mplm.single_ax_manager(pp=pp) as ax:
                    data.plot(ax=ax, alpha=0.8, marker='o')
                    ax.set_xlabel(numparam)
                    ax.legend(loc='best')
                    if grid:
                        ax.grid()
                    if logx:
                        ax.set_xscale('log')
                    if logy:
                        ax.set_yscale('log')
                        # ymin,ymax = ax.get_ylim()
                        ymin = np.nanmin(data.values)
                        ymax = np.nanmax(data.values)
                        ymin = np.power(10, np.floor(np.log10(ymin)))
                        ymax = np.power(10, np.ceil(np.log10(ymax)))
                        if np.isfinite(ymin) and np.isfinite(ymax):
                            ax.set_ylim([ymin, ymax])
                    if param_panda is not None:
                        param_series = param_panda.loc[(numparam)]
                        string = ' '.join(extract_interesting_vars(param_series, numparam))
                        ax.text(-0.1, 1.05, string, transform=ax.transAxes)


def iterate_seqs(seqsnew, varvals):
    for nameval, seq_lists in seqsnew.items():
        for idx, seq_list in enumerate(seq_lists):
            vals = dict((dir_, try_to_float(varvals[nameval][dir_][0]))
                        for dir_ in seq_list)
            for dir_, val in sorted(vals.items(),
                                    key=lambda x: try_to_float(x[1])):
                numparam = is_it_tuple(nameval[0])
                yield ((numparam, val), idx), dir_


# def import_from_double_var(double_var, varvals):
#     """ """
#     whatever_scalar = 0.1
#     double_var_pandas = {}
#     for namevals, seq_lists in double_var.items():
#         for idx, seq_list in enumerate(seq_lists):
#             df = pd.DataFrame()
#             df.index.name = is_it_tuple(namevals[0])
#             df.columns.name = is_it_tuple(namevals[1])
#             vals = dict((dir_, (varvals[namevals][dir_])) for dir_ in seq_list)
#             for dir_, val in sorted(vals.items(), key=lambda x: x[1]):
#                 df.loc[val[0], val[1]] = whatever_scalar
#                 df.loc[val[0], val[1]] = dir_
#             double_var_pandas.setdefault(namevals, []).append(df)
#     return double_var_pandas
def import_from_double_var(double_var, varvals):
    """ """
    whatever_scalar = 0.1
    double_var_pandas = {}
    for namevals, seq_list in double_var_iter(double_var):
        df = pd.DataFrame()
        df.index.name = is_it_tuple(namevals[0])
        df.columns.name = is_it_tuple(namevals[1])
        for val0, val1, dir_ in namevals_iter(namevals, seq_list, varvals):
            df.loc[val0, val1] = whatever_scalar
            df.loc[val0, val1] = dir_
        double_var_pandas.setdefault(namevals, []).append(df)
    return double_var_pandas


def double_var_vectors(double_var, varvals):
    double_var_out = {}
    for namevals, seq_list in double_var_iter(double_var):
        val0, val1, dirs = zip(*namevals_iter(namevals, seq_list, varvals))
        print(val0, val1, dirs)
        double_var_out.setdefault(namevals, []).append((val0, val1, dirs))
    return double_var_out


# def double_var_vectors(double_var, varvals):
#     """ """
#     double_var = {}
#     for namevals, seq_lists in double_var.items():
#         for seq_list in seq_lists:
#             var1 = []
#             var2 = []
#             dirs = []
#             vals = dict((dir_, (varvals[namevals][dir_])) for dir_ in seq_list)
#             for dir_, val in sorted(vals.items(), key=lambda x: x[1]):
#                 var1.append(val[0])
#                 var2.append(val[0])
#                 dirs.append(dir_)
#             double_var.setdefault(namevals, []).append((var1, var2, dirs))
#     return double_var


def double_var_iter(double_var):
    for namevals, seq_lists in double_var.items():
        for seq_list in seq_lists:
            yield namevals, seq_list


def namevals_iter(namevals, seq_list, varvals):
    vals = dict((dir_, (varvals[namevals][dir_])) for dir_ in seq_list)
    for dir_, val in sorted(vals.items(), key=lambda x: try_to_float(x[1])):
        yield val[0], val[1], dir_


def extract_interesting_vars(param_series, numparam):
    for column in param_series:
        paramdicts = param_series[column].dropna()
        if not paramdicts.empty:
            paramdict = paramdicts.iloc[0]
            for param_str in write_paramdict(paramdict, numparam):
                yield ''.join((str(column), ': ', param_str))


def write_paramdict(paramdict, ignore=None, connector='='):
    for field in paramdict:
        # if field != ignore:
        if ignore not in field:
            yield ''.join((str(is_it_tuple(field)), connector,
                           str(paramdict[field])))


def return_dict_element(dict_, error=KeyError):
    """ Returns a function that returns `dict_[arg]`, while ignoring `error`"""
    @ignored(error)
    def return_element(el):
        return dict_[el]
    return return_element


def try_to_float(str_):
    try:
        return float(str_)
    except (ValueError, TypeError):
        return str(str_)


def make_a_seq_panda(dict_w_params):
    """ Convenience function for finding sequences of data, and putting them
 in a Pandas structure """
    seqs, varvals = analyse.groupby_n_var_params(dict_w_params, 1)
    panda_data = SeqsDataFrame().import_from_seq(seqs, varvals)
    return panda_data


def drop_boring_columns(df):
    """ Drops all columns in `df` that has only 1 or less unique values.
Returns a new DataFrame """
    nunique = df.apply(pd.Series.nunique)
    cols_to_drop = nunique[nunique <= 1].index
    return df.drop(cols_to_drop, axis=1)
