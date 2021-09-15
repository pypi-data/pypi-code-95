#
# Delegated Accessor Attributes for DataFrames
#
import pandas as pd
from ._util import rgetattr, get_summary
from ._accessor_series import GeosSeriesAccessor

__all__ = [
    'get_DataFrameExpandedProperty',
    'get_DataFrameExpandedMethodUnary',
]


def get_DataFrameExpandedProperty(name, expansion):
    """
    Create a property that calls the :class:`pgpd.GeosSeriesAccessor` property
    on each geos column and groups the result.

    Args:
        name (str): Name of the propery in the :class:`pgpd.GeosSeriesAccessor`.
        expansion (int): Type of dataframe expansion
    """
    func_summary = get_summary(rgetattr(GeosSeriesAccessor, f'{name}.__doc__', None))

    def delegated1(self, inplace=False):
        """
        {summary}

        Applies :attr:`pgpd.GeosSeriesAccessor.{func}` to each column of "geos" dtype
        and aggregates the results in a DataFrame.

        Args:
            inplace (bool, optional): Whether to perform the modifications inplace; Default **False**.

        Returns:
            pandas.DataFrame or None:
                DataFrame where each "geos" column from the original is transformed or None if ``inplace=True``.
        """
        result = {}
        for column, dtype in self._obj.dtypes.iteritems():
            if pd.api.types.pandas_dtype('geos') == dtype:
                result[column] = getattr(self._obj[column].geos, name)

        if not inplace:
            return pd.DataFrame.from_dict(result)
        else:
            for column, values in result.items():
                self._obj[column] = values

    def delegated2(self):
        """
        {summary}

        Applies :attr:`pgpd.GeosSeriesAccessor.{func}` to each column of "geos" dtype
        and aggregates the results in a DataFrame.

        Returns:
            pandas.DataFrame: DataFrame where each "geos" column from the original is transformed.
        """
        result = {}
        for column, dtype in self._obj.dtypes.iteritems():
            if pd.api.types.pandas_dtype('geos') == dtype:
                result[column] = getattr(self._obj[column].geos, name)

        return pd.DataFrame.from_dict(result)

    if expansion == 1:
        delegated1.__doc__ = delegated1.__doc__.format(func=name, summary=func_summary).strip()
        return delegated1
    else:
        delegated2.__doc__ = delegated2.__doc__.format(func=name, summary=func_summary).strip()
        return property(delegated2)


def get_DataFrameExpandedMethodUnary(name, expansion):
    """
    Create a unary method that calls the :class:`pgpd.GeosSeriesAccessor` method
    on each geos column and aggregates the result.

    Args:
        name (str): Name of the method in the :class:`pgpd.GeosSeriesAccessor`.
        expansion (int): Type of dataframe expansion
    """
    func_summary = get_summary(rgetattr(GeosSeriesAccessor, f'{name}.__doc__', None))

    def delegated1(self, *args, inplace=False, **kwargs):
        """
        {summary}

        Applies :func:`pgpd.GeosSeriesAccessor.{func}` to each column of "geos" dtype
        and aggregates the results in a DataFrame.

        Args:
            args: Arguments passed to :func:`~pgpd.GeosSeriesAccessor.{func}` after the first argument.
            inplace (bool, optional): Whether to perform the modifications inplace; Default **False**.
            kwargs: Keyword arguments passed to :func:`~pgpd.GeosSeriesAccessor.{func}`.

        Returns:
            pandas.DataFrame or None:
                DataFrame where each "geos" column from the original is transformed or None if ``inplace=True``.
        """
        result = {}
        for column, dtype in self._obj.dtypes.iteritems():
            if pd.api.types.pandas_dtype('geos') == dtype:
                result[column] = getattr(self._obj[column].geos, name)(*args, **kwargs)

        if not inplace:
            return pd.DataFrame.from_dict(result)
        else:
            for column, values in result.items():
                self._obj[column] = values

    def delegated2(self, *args, **kwargs):
        """
        {summary}

        Applies :func:`pgpd.GeosSeriesAccessor.{func}` to each column of "geos" dtype
        and aggregates the results in a DataFrame.

        Args:
            args: Arguments passed to :func:`~pgpd.GeosSeriesAccessor.{func}` after the first argument.
            kwargs: Keyword arguments passed to :func:`~pgpd.GeosSeriesAccessor.{func}`.

        Returns:
            pandas.DataFrame or None:
                DataFrame where each "geos" column from the original is transformed or None if ``inplace=True``.
        """
        result = {}
        for column, dtype in self._obj.dtypes.iteritems():
            if pd.api.types.pandas_dtype('geos') == dtype:
                result[column] = getattr(self._obj[column].geos, name)(*args, **kwargs)

        return pd.DataFrame.from_dict(result)

    if expansion == 1:
        delegated1.__doc__ = delegated1.__doc__.format(func=name, summary=func_summary)
        return delegated1
    else:
        delegated2.__doc__ = delegated2.__doc__.format(func=name, summary=func_summary)
        return delegated2
