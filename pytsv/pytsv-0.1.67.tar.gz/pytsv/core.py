import gzip
import itertools
import logging
import re
from collections import defaultdict
from typing import Iterable, List, Tuple, Dict, IO, Text, Union, Sequence

import pyanyzip.core

from pytsv.configs import SANITIZE, CLEAN_EDGES, SUB_TRAILING, REMOVE_NON_ASCII, LOWER_CASE, CHECK_NUM_FIELDS, \
    CONVERT_TO_STRING, FILENAME_DETECT, DO_GZIP, USE_ANY_FORMAT, SKIP_COMMENTS, \
    CHECK_NON_ASCII, VALIDATE_ALL_LINES_SAME_NUMBER_OF_FIELDS


def clean(
    text: str,
    clean_edges: bool = True,
    sub_trailing: bool = True,
    remove_non_ascii: bool = True,
    lower_case: bool = True,
) -> str:
    if sub_trailing:
        # replace all manner of whitespace (consecutive or not)
        # with s single space
        text = re.sub(r"[\r\t\n\v ]+", " ", text)
    if remove_non_ascii:
        text = text.encode('ascii', errors='ignore').decode()
    if clean_edges:
        # remove space from the left and right
        text = text.strip()
    if lower_case:
        text = text.lower()
    return text


def do_aggregate(
    input_file_names: Iterable[str],
    match_columns: List[int],
    aggregate_columns: List[int],
    output_file_name: str,
    floating_point: bool,
) -> None:
    """
    This function aggregates a bunch of input files by integers.
    :param input_file_names:
    :param match_columns:
    :param aggregate_columns:
    :param output_file_name:
    :param floating_point:
    :return:
    """
    counts: Dict[Tuple[str], List[Union[int, float]]] = {}
    logger = logging.getLogger(__name__)
    for input_file_name in input_file_names:
        logger.debug(f"working on file [{input_file_name}]")
        with TsvReader(filename=input_file_name) as input_handle:
            for fields in input_handle:
                match: Tuple[str] = tuple(fields[i] for i in match_columns)
                if match not in counts:
                    if floating_point:
                        counts[match] = [float(0)] * len(aggregate_columns)
                    else:
                        counts[match] = [int(0)] * len(aggregate_columns)
                for i, aggregate_column in enumerate(aggregate_columns):
                    if floating_point:
                        counts[match][i] += float(fields[aggregate_column])
                    else:
                        counts[match][i] += int(fields[aggregate_column])
    # notice that we create a writer that does not check the number
    # of fields because the check requires a len(fields) to be available
    # and it is not in this case because of itertools.chain
    with TsvWriter(
        filename=output_file_name,
        check_num_fields=False,
        sanitize=False,
    ) as output_file_handle:
        for match, aggregates in counts.items():
            to_write = list(itertools.chain(match, aggregates))
            output_file_handle.write(to_write)


def write_data(data: List[List[str]], output_file_name: str) -> None:
    with TsvWriter(
        filename=output_file_name,
        mode="at",
    ) as output_file_handle:
        for d in data:
            output_file_handle.write(d)


def group_by(
    input_file_names: Iterable[str],
    group_by_columns: List[int],
    collect_columns: List[int],
    output_file_template: str,
) -> List[str]:
    all_data: Dict[str, List[List[str]]] = defaultdict(list)
    limit = 10000
    logger = logging.getLogger(__name__)
    for input_file_name in input_file_names:
        logger.debug(f"working on file [{input_file_name}]")
        with open(input_file_name, 'rt') as file_handle:
            for line in file_handle:
                line = line.rstrip()
                parts: List[str] = line.split("\t")
                match_tup: Tuple[str] = tuple(parts[i] for i in group_by_columns)
                match = "_".join(match_tup)
                data_to_append = [parts[i] for i in collect_columns]
                all_data[match].append(data_to_append)
                if len(all_data[match]) > limit:
                    write_data(all_data[match], output_file_template.format(match=match))
                    all_data[match] = []
    # write the rest for the data
    for match, data in all_data.items():
        write_data(data, output_file_template.format(match=match))
    return [output_file_template.format(match=match) for match in all_data]


def is_ascii(s: str) -> bool:
    return all(ord(c) < 128 for c in s)


class TsvWriter:
    def __init__(
        self,
        filename: str,
        mode: str = "wt",
        throw_exceptions: bool = False,

        sanitize: bool = SANITIZE,
        fields_to_clean: List[int] = None,
        clean_edges: bool = CLEAN_EDGES,
        sub_trailing: bool = SUB_TRAILING,
        remove_non_ascii: bool = REMOVE_NON_ASCII,
        lower_case: bool = LOWER_CASE,

        check_num_fields: bool = CHECK_NUM_FIELDS,
        num_fields: int = None,
        convert_to_string: bool = CONVERT_TO_STRING,

        do_gzip: bool = DO_GZIP,
        filename_detect: bool = FILENAME_DETECT,
    ) -> None:
        if filename_detect:
            found = False
            if filename.endswith(".tsv.gz"):
                self.io: IO[str] = gzip.open(filename, mode=mode)
                found = True
            if filename.endswith(".tsv"):
                # pylint: disable=consider-using-with
                self.io: IO[str] = open(filename, mode=mode)
                found = True
            if not found:
                # treat as tsv
                # pylint: disable=consider-using-with
                self.io: IO[str] = open(filename, mode=mode)
            # old code, be more strict
            # assert found, "file name unknown"
        else:
            if do_gzip:
                self.io: IO[str] = gzip.open(filename, mode=mode)
            else:
                # pylint: disable=consider-using-with
                self.io: IO[str] = open(filename, mode=mode)
        self.throw_exceptions = throw_exceptions

        self.sanitize = sanitize
        self.fields_to_clean = fields_to_clean
        if self.fields_to_clean is None:
            self.fields_to_clean = []
        self.clean_edges = clean_edges
        self.sub_trailing = sub_trailing
        self.remove_non_ascii = remove_non_ascii
        self.lower_case = lower_case

        self.check_num_fields = check_num_fields
        self.num_fields = num_fields
        self.convert_to_string = convert_to_string

    def _sanitize(self, seq: Sequence[str]) -> Sequence[str]:
        if self.sanitize:
            r = list(seq)
            for field in self.fields_to_clean:
                r[field] = clean(
                    text=r[field],
                    clean_edges=self.clean_edges,
                    sub_trailing=self.sub_trailing,
                    remove_non_ascii=self.remove_non_ascii,
                    lower_case=self.lower_case,
                )
            return r
        return seq

    def _convert(self, seq: Sequence[str]) -> Sequence[str]:
        if self.convert_to_string:
            for t in seq:
                if type(t) in (int, float, type(None)):
                    yield str(t)
                else:
                    yield t
        else:
            for x in seq:
                yield x

    def write(self, input_list: Sequence[str]) -> None:
        sanitized_list = self._sanitize(input_list)
        if self.check_num_fields:
            if self.num_fields is None:
                self.num_fields = len(sanitized_list)
            else:
                assert len(sanitized_list) == self.num_fields, "wrong number of fields in {}".format(sanitized_list)
        print("\t".join(self._convert(sanitized_list)), file=self.io)

    def close(self) -> None:
        self.io.close()

    def __enter__(self):
        """ method needed to be a context manager """
        return self

    def __exit__(self, itype, value, traceback):
        """ method needed to be a context manager """
        self.close()


class TsvReader:
    def __init__(
        self,
        filename: str,
        mode: str = "rt",
        use_any_format: bool = USE_ANY_FORMAT,
        validate_all_lines_same_number_of_fields: bool = VALIDATE_ALL_LINES_SAME_NUMBER_OF_FIELDS,
        num_fields: Union[int, None] = None,
        skip_comments: bool = SKIP_COMMENTS,
        check_non_ascii: bool = CHECK_NON_ASCII,
        newline: Union[str, None] = '\n',
    ) -> None:
        if use_any_format:
            self.io = pyanyzip.core.openzip(name=filename, mode=mode, newline=newline)
        else:
            # pylint: disable=consider-using-with
            self.io = open(filename, mode=mode, newline=newline)
        self.validate_all_lines_same_number_of_fields = validate_all_lines_same_number_of_fields
        self.num_fields = num_fields
        self.skip_comments = skip_comments
        self.check_non_ascii = check_non_ascii

        self.line_number = -1

    def next(self):
        return self.__next__()

    def __next__(self) -> List[Text]:
        """ method needed to be an iterator """
        self.line_number += 1
        line = self.io.readline()
        if not line:
            raise StopIteration
        if self.skip_comments:
            while line.startswith("#"):
                self.line_number += 1
                line = self.io.readline()
                if not line:
                    raise StopIteration
        line = line.rstrip('\r\n')
        if self.check_non_ascii:
            assert is_ascii(line), "non ascii characters in line [{}]".format(self.line_number)
        fields = line.split('\t')
        if self.validate_all_lines_same_number_of_fields:
            if self.num_fields is None:
                self.num_fields = len(fields)
            else:
                assert len(fields) == self.num_fields, "wrong number of fields in line number {} {} {}".format(
                    self.line_number,
                    self.num_fields,
                    len(fields),
                )
        if self.check_non_ascii:
            assert is_ascii(line)
        return fields

    def __iter__(self):
        """ method needed to be an iterator """
        return self

    def __enter__(self):
        """ method needed to be a context manager """
        return self

    def __exit__(self, itype, value, traceback):
        """ method needed to be a context manager """
        self.close()

    def close(self) -> None:
        self.io.close()


def write_dict(filename: str = None, d: Dict[str, str] = None) -> None:
    with TsvWriter(filename=filename, num_fields=2, fields_to_clean=[0]) as output_handle:
        for k, v in d.items():
            output_handle.write([k, v])
