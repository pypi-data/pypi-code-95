#!/usr/bin/env python
# -*- coding: utf-8; -*-

# Copyright (c) 2021 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

"""
Module to facilitate reading file from different format. For most formats,
apache tika might work. There may be formats for which format specific libraries
may be better

Usage
-----

>>> processor = FileProcessorFactory.get_processor("pdf")
>>> content = processor(file_name).read_text()
"""
import io
import logging
import os
import re
import shutil
from typing import Dict, Generator, List, Union

import ads
from ads.text_dataset import backends
from ads.text_dataset.backends import OITCC, Base, PDFPlumber, Tika
from ads.text_dataset.utils import NotSupportedError
from fsspec.core import OpenFile

logger = logging.getLogger('ads.text_dataset')


class FileProcessor:
    """
    Base class for all the file processor.

    Files are opend using fsspec library

    The default implementation in the base class assumes text files
    """
    backend_map = {'base': Base, 'tika': Tika}
    
    def __init__(self, backend: Union[str, backends.Base] = 'base') -> None:
        self.backend(backend)
    
    def backend(self, backend: Union[str, backends.Base]) -> None:
        """Set backend for file processor.

        Parameters
        ----------
        backend : `ads.text_dataset.backends.Base`
            a backend for file processor

        Returns
        -------
        None

        Raises
        ------
        NotSupportedError
            when specified backend is not supported.
        """
        if isinstance(backend, str) and backend in self.backend_map:
            self._backend = self.backend_map[backend]()
        elif isinstance(backend, Base):
            self._backend = backend
        else:
            raise NotSupportedError('backend is not recognized or not a subclass of ads.text_dataset.backends.Base.')
        if isinstance(self._backend, Tika) and (
            "CONDA_PREFIX" not in os.environ or
            not os.path.exists(os.path.join(os.environ.get('CONDA_PREFIX'), 'text-extraction-tools.jar'))
        ):
            raise NotSupportedError(
                "Tika is not supported in this distribution. Please use alternatives such as pdfplumber."
            )
        return self

    def read_line(self, fhandler: OpenFile, **format_reader_kwargs: Dict) -> Generator[Union[str, List[str]], None, None]:
        """Yields lines from a file.

        Parameters
        ----------
        fhandler : `fsspec.core.OpenFile`
            file handler returned by `fsspec`

        Returns
        -------
        Generator
            a generator that yields lines from a file
        """
        return self._backend.read_line(fhandler, **format_reader_kwargs)
        
    def read_text(self, fhandler: OpenFile, **format_reader_kwargs: Dict) -> Generator[Union[str, List[str]], None, None]:
        """Yield contents from the entire file.

        Parameters
        ----------
        fhandler : `fsspec.core.OpenFile`
            a file handler returned by fsspec

        Returns
        -------
        Generator
            a generator that yield text from a file
        """
        return self._backend.read_text(fhandler, **format_reader_kwargs)

    def convert_to_text(self, fhandler: OpenFile, dest: str = None, dirname: str = None, **format_reader_kwargs: Dict) -> str:
        """Convert input file to a text file.

        Parameters
        ----------
        fhandler : `fsspec.core.OpenFile`
            a file handler returned by `fsspec`
        dest : str, optional
            path to destination for output file, by default None
        dirname : str, optional
            path to destination for output folder, by default None

        Returns
        -------
        str
            path to saved output
        """
        return self._backend.convert_to_text(fhandler, dest, dirname, **format_reader_kwargs)

    def get_metadata(self, fhandler: OpenFile) -> Dict:
        """Get metadata of a file.

        Parameters
        ----------
        fhandler : `fsspec.core.OpenFile`
            a file handler returned by fsspec

        Returns
        -------
        dict
            dictionary of metadata
        """
        return self._backend.get_metadata(fhandler)


class PDFProcessor(FileProcessor):
    """
    Extracts text content from PDF
    """
    backend_map = {'tika': Tika, 'oit-cc': OITCC, 'pdfplumber': PDFPlumber}

    def __init__(self, backend='pdfplumber'):
        super().__init__(backend=backend)


class WordProcessor(FileProcessor):
    """
    Extracts text content from doc or docx format
    """
    backend_map = {'tika': Tika, 'oit-cc': OITCC}

    def __init__(self, backend='tika'):
        super().__init__(backend=backend)


class FileProcessorFactory:
    processor_map = {
        "pdf": PDFProcessor,
        "docx": WordProcessor,
        "doc": WordProcessor,
        "txt": FileProcessor
    }

    @staticmethod
    def get_processor(format):
        if format in FileProcessorFactory.processor_map:
            return FileProcessorFactory.processor_map[format]
        else:
            logger.warning(
                f"""
                Format {format} is not supported natively. 
                A generic FileProcessor is returned. 
                You can define a custom backend to pass in.
                """
            )
            return FileProcessor
