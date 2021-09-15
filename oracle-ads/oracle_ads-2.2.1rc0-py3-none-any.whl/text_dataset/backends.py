#!/usr/bin/env python
# -*- coding: utf-8; -*-

# Copyright (c) 2021 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

import distutils.spawn
import io
import json
import os
import shutil
from typing import Dict, Generator, List, Union

import yaml
from ads.text_dataset.utils import PY4JGateway, experimental
from fsspec.core import OpenFile


class Base:
    """Base class for backends.
    """

    def read_line(self, fhandler: OpenFile) -> Generator[Union[str, List[str]], None, None]:
        """Read lines from a file.

        Parameters
        ----------
        fhandler : `fsspec.core.OpenFile`
            a file handler returned by `fsspec`

        Yields
        -------
        Generator
            a generator that yields lines
        """
        with fhandler as f:                                                                                                                          
            for line in f:
                yield line.decode(fhandler.encoding)

    def read_text(self, fhandler: OpenFile) -> Generator[Union[str, List[str]], None, None]:
        """Read entire file into a string.

        Parameters
        ----------
        fhandler : `fsspec.core.OpenFile`
            a file handler returned by `fsspec`

        Yields
        -------
        Generator
            a generator that yields text in the file
        """
        with fhandler as f:
            yield f.read().decode(fhandler.encoding)

    @staticmethod
    def _validate_dest(src, dest: str, dirname: str) -> str:
        if dest is None and dirname is None:
            raise ValueError(f'Either dest or dirname must be provided.')
        if dest is None:
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            dest = os.path.join(dirname, os.path.splitext(os.path.basename(src))[0] + '.txt')
        else:
            if len(os.path.dirname(dest)) > 0 and not os.path.exists(os.path.dirname(dest)):
                os.makedirs(os.path.dirname(dest))
        return dest

    def convert_to_text(self, fhandler: OpenFile, dest: str = None, dirname: str = None) -> str:
        """Convert input file to a text file

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
        dest = self._validate_dest(fhandler.path, dest, dirname)
        shutil.copyfile(fhandler.path, dest)
        return dest

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
        return {}
 

class Tika(Base):

    def read_line(self, fhandler):
        with PY4JGateway() as gateway:
            parser = gateway.jvm.parsers.TikaParser()
            with fhandler as f:
                reader = parser.reader(f.read())
            while True:
                line = reader.readLine()
                if line is not None:
                    yield line
                else:
                    break   

    def read_text(self, fhandler):
        with PY4JGateway() as gateway:
            parser = gateway.jvm.parsers.TikaParser()
            with fhandler as f:
                yield parser.readText(f.read()).decode()

    def convert_to_text(self, fhandler, dest=None, dirname=None) -> str:
        with PY4JGateway() as gateway:
            parser = gateway.jvm.parsers.TikaParser()
            dest = self._validate_dest(fhandler.path, dest, dirname)
            with fhandler as f:
                parser.convertText(f.read(), dest)
        return dest

    def get_metadata(self, fhandler):
        with PY4JGateway() as gateway:
            parser = gateway.jvm.parsers.TikaParser()
            meta = gateway.jvm.org.apache.tika.metadata.Metadata()
            with fhandler as f:
                parser.readText(f.read(), meta)
            return json.loads(parser.getMetadata(meta))

    def detect_encoding(self, fhandler: OpenFile) -> str:
        with PY4JGateway() as gateway:
            with fhandler as f:
                return gateway.jvm.parsers.TikaParser.detectEncoding(f.read())


class PDFPlumber(Base):
    
    def __init__(self):
        try:
            import pdfplumber
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError('pdfplumber must be installed first.')
        super().__init__()

    def read_line(self, fhandler):
        import pdfplumber
        with fhandler as f:
            pdf = pdfplumber.PDF(f)
            for page in pdf.pages:
                reader = io.StringIO(page.extract_text())
                for line in reader:
                    yield line 

    def read_text(self, fhandler):
        import pdfplumber
        with fhandler as f:
            pdf = pdfplumber.PDF(f)
            texts = (page.extract_text() for page in pdf.pages)
            yield "\n".join([text for text in texts if text is not None])

    def convert_to_text(self, fhandler, dest=None, dirname=None):
        import pdfplumber
        dest = self._validate_dest(fhandler.path, dest, dirname)
        with fhandler as f:
            pdf = pdfplumber.PDF(f)
            with open(dest, 'w') as f:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text is not None:
                        f.write(text)
        return dest

    def get_metadata(self, fhandler):
        import pdfplumber
        with fhandler as f:
            pdf = pdfplumber.PDF(f)
            return pdf.metadata


@experimental
class OITCC(Base): #pragma: no cover

    def convert_to_text(self, fhandler, dest=None, dirname=None):
        with PY4JGateway() as gateway:
            parser = gateway.jvm.parsers.CCParser()
            dest = self._validate_dest(fhandler.path, dest, dirname)
            with fhandler as f:
                parser.convertText(f.read(), dest)
            return dest
