#!/usr/bin/env python
# -*- coding: utf-8; -*-

# Copyright (c) 2021 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

import itertools
import os
import pathlib
import re
from collections import defaultdict
from typing import Any, Callable, Dict, Generator, List, Tuple, Union

import ads
import ads.text_dataset.extractor as te
import dask
import fsspec
import pandas as pd
from ads.text_dataset import backends
from ads.text_dataset.extractor import FileProcessor
from ads.text_dataset.options import OptionFactory, Options
from ads.text_dataset.udfs import UDF
from ads.text_dataset.utils import NotSupportedError


class DataLoader:
    """
    DataLoader binds engine, FileProcessor and File handler(in this case it is fsspec)
    to build TextDataset.

    This class is expected to be used mainly from TextDatasetFactory class

    Usage
    -----
    >> import pandas as pd
    >> dl = DataLoader(engine=pd).processor(te.FileProcessorFactory.get_processor("pdf"))
    >> lines = dl.read_line('/etc/passwd', columns=['c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7'],
                line_matcher="(.*)\.(.*)\.(.*)\.(.*)\.(.*)\.(.*)\.(.*)")
    """

    def __init__(self, engine: str = None) -> None:
        """
        The engine can come from some global settings.
        Eg engine -
        >> import pandas as pd
        >> engine = pd

        eg2 -
        >> import modin.pandas as pd
        >> engine = pd

        >> import cudf
        >> engine = cudf
        """
        self.engine(engine)
        self.filemanager = fsspec
        self.processor = te.FileProcessorFactory.get_processor("txt")
        self.options = []
        self._data = None

    def with_processor(self, processor_type: str) -> None:
        """Set file processor.

        Parameters
        ----------
        processor_type : str
            type of processor, which corresponds to format of the file

        Returns
        -------
        None
        """
        self.processor = te.FileProcessorFactory.get_processor(processor_type)()
        return self
    
    def engine(self, eng: str) -> None:
        """Set engine for dataloader. Can be pandas or cudf.

        Parameters
        ----------
        eng : str
            name of engine

        Returns
        -------
        Nonq

        Raises
        ------
        NotSupportedError
            raises error if engine passed in is not supported
        """
        if eng is None:
            self._engine = None
            self._format_output = lambda *args, **kwargs: args[0]
            return self
        if eng not in ['pandas', 'cudf']:
            raise NotSupportedError('Only pandas and cudf currently.')
        else:
            if eng == 'pandas':
                import pandas
                self._engine = pandas
                self._format_output = pandas.DataFrame
            else:
                import cudf
                self._engine = cudf
                self._format_output = lambda data, **kwargs: cudf.DataFrame([row for row in data], **kwargs) # cuDF cannot be initialized with a generator
        return self

    def backend(self, backend: Union[str, backends.Base]) -> None:
        """Set backend used for extracting text from files.

        Parameters
        ----------
        backend : (str | `ads.text_dataset.backends.Base`)
            backend for extracting text from raw files.

        Returns
        -------
        None
        """
        self.processor.backend(backend)
        return self

    def option(self, opt: Options, value: Any = None) -> None:
        """Set options.

        Parameters
        ----------
        opt : `ads.text_dataset.options.Options`
            an option defined in `ads.text_dataset.options.Options`
        value : Any, optional
            value for the option, by default None

        Returns
        -------
        None
        """
        self.options.append((OptionFactory.option_handler(opt), value))
        return self

    def __load_data__(
        self,
        reader: Callable,
        path: str,
        udf: Union[str, Callable] = None,
        storage_options: Dict = None,
        encoding: str = 'utf-8',
        n_rows_per_file: int = None,
        total_rows: int = None,
    ) -> Generator[Union[str, List[str]], None, None]:
        storage_options = storage_options if storage_options is not None else {}
        fhs =  self.filemanager.open_files(path, mode='rb', encoding=encoding, **storage_options) 
        if udf is not None:
            if isinstance(udf, str):
                fn = UDF.from_regex(udf)
            else:
                fn = udf
        else:
            fn = lambda x: x
        
        total_line_count = [0]
        # function to apply to each element
        def func(fh, reader):
            out = [option(self).handle(fh, value) for option, value in self.options]
            line_count = 0
            for text in reader(fh):
                if total_rows is None or total_line_count[0] < total_rows:
                    if n_rows_per_file is None or line_count < n_rows_per_file:
                        content = fn(text)
                        if content is not None:
                            yield out + list(content) if (isinstance(content, list) or isinstance(content, tuple)) else out + [content]
                            line_count += 1
                            total_line_count[0] += 1

        return itertools.chain.from_iterable((func(fh, reader) for fh in fhs))

    def read_line(
        self,
        path: str,
        udf: Union[str, Callable] = None, 
        n_lines_per_file: int = None, 
        total_lines: int = None, 
        df_args: Dict = None, 
        storage_options: Dict = None, 
        encoding: str = 'utf-8'
    ) -> Union[Generator[Union[str, List[str]], None, None], pd.DataFrame]:
        """Read each file into lines. If path matches multiple files, will combine lines from all files.

        Parameters
        ----------
        path : str
            path to data files. can have glob pattern.
        udf : (callable | str), optional
            user defined function for processing each line, can be a callable or regex, by default None
        n_lines_per_file : int, optional
            max number of lines read from each file, by default None
        total_lines : int, optional
            max number of lines read from all files, by default None
        df_args : dict, optional
            arguments passed to dataframe engine (e.g. pandas), by default None
        storage_options : dict, optional
            storage options for cloud storage, by default None
        encoding : str, optional
            encoding of files, by default 'utf-8'

        Returns
        -------
        `ads.text_dataset.dataset.TextDataset`
            a `TextDataset` object.
        """
        df_args = df_args if df_args is not None else {}
        self._data = self.__load_data__(self.processor.read_line, path, udf, storage_options, encoding, n_lines_per_file, total_lines)
        return self._format_output(self._data, **df_args)
    
    def read_text(
        self,
        path: str, 
        udf: Union[str, Callable] = None, 
        total_files: int = None, 
        storage_options: Dict = None, 
        df_args: Dict = None, 
        encoding: str = 'utf-8'
    ) -> Union[Generator[Union[str, List[str]], None, None], pd.DataFrame]:
        """Read each file into a text string.

        Parameters
        ----------
        path : str
            path to data files. can have glob pattern.
        udf : (callable | str), optional
            user defined function for processing each line, can be a callable or regex, by default None
        total_files : int, optional
            max number of files to read, by default None
        df_args : dict, optional
            arguments passed to dataframe engine (e.g. pandas), by default None
        storage_options : dict, optional
            storage options for cloud storage, by default None
        encoding : str, optional
            encoding of files, by default 'utf-8'

        Returns
        -------
        `ads.text_dataset.dataset.TextDataset`
            a `TextDataset` object.
        """
        df_args = df_args if df_args is not None else {}
        self._data = self.__load_data__(self.processor.read_text, path, udf, storage_options, encoding, 1, total_files)
        return self._format_output(self._data, **df_args)
 
    # ----- not currently used, but in case we want to consider chaining in the future -----
    def _transform(self, udf, udf_type='fn'): #pragma: no cover
        if udf_type == 'fn':
            func = UDF.from_lambda(udf)
        elif udf_type == 'regex':
            func = UDF.from_regex(udf)
        else:
            raise NotImplementedError('Other types of UDF not yet supported.')
        
        # convert df into iterator
        if isinstance(self._data, pd.DataFrame) or isinstance(self._data, pd.Series):
            self._data = (row.values if len(row.values) > 1 else row.values[0] for i, row in self._data.iterrows())
        
        self._data = (func(row) for row in self._data)
        self._data = (row for row in self._data if row is not None)
        return self
    

class TextDatasetFactory:

    """
    Usage:
    -----
    1. Using format().read option
    >> textds = TextDatasetFactory.format("pdf").read_text("oci://devbucket/test")
    >> assert isinstance(textds, ads.dataset.TextDataset)

    2. Using familiar form_<format> option of pands
    >> textds = TextDatasetFactory.from_pdf()
    >> textds = TextDatasetFactory.format("pdf").read_text("oci://devbucket/test")
    """
    
    @staticmethod
    def format(format_name: str) -> DataLoader:
        """Instantiates DataLoader class and seeds it with the right kind of FileProcessor.
        Eg. PDFProcessor for pdf. The FileProcessorFactory returns the processor based
        on the format Type.

        Parameters
        ----------
        format_name : str
            name of format

        Returns
        -------
        `ads.text_dataset.dataset.DataLoader`
            a `DataLoader` object.
        """
        dl = DataLoader()
        return dl.with_processor(format_name)

