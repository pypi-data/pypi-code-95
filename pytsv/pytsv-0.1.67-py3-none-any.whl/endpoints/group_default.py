import concurrent.futures
import csv
import logging
import os
import sys
from collections import defaultdict
from enum import Enum
from typing import List, Dict, Set

import attr
import numpy
import numpy.random
import pandas
import pyanyzip.core
import pylogconf.core
import tqdm
from pytconf import register_endpoint, register_function_group

from pytsv.configs import ConfigInputFiles, ConfigFloatingPoint, ConfigAggregateColumns, ConfigMatchColumns, \
    ConfigOutputFile, ConfigProgress, ConfigParallel, ConfigNumFields, ConfigTsvReader, ConfigColumns, \
    ConfigInputFile, ConfigFixTypes, ConfigColumn, ConfigBucketNumber, ConfigMajority, ConfigCsvToTsv, ConfigJoin, \
    ConfigTree, ConfigSampleByColumnOld, ConfigSampleByTwoColumns, ConfigPattern, \
    ConfigSampleSize, ConfigReplace, ConfigSampleColumn, ConfigWeightValue, ConfigCheckUnique
from pytsv.core import TsvReader, TsvWriter, clean, do_aggregate

GROUP_NAME_DEFAULT = "default"
GROUP_DESCRIPTION_DEFAULT = "all pytsv commands"


def register_group_default():
    register_function_group(
        function_group_name=GROUP_NAME_DEFAULT,
        function_group_description=GROUP_DESCRIPTION_DEFAULT,
    )


@register_endpoint(
    configs=[
        ConfigInputFiles,
        ConfigFloatingPoint,
        ConfigAggregateColumns,
        ConfigMatchColumns,
        ConfigOutputFile,
    ],
    group=GROUP_NAME_DEFAULT,
)
def aggregate() -> None:
    """
    aggregate TSV files
    """
    do_aggregate(
        input_file_names=ConfigInputFiles.input_files,
        match_columns=ConfigMatchColumns.match_columns,
        aggregate_columns=ConfigAggregateColumns.aggregate_columns,
        output_file_name=ConfigOutputFile.output_file,
        floating_point=ConfigFloatingPoint.floating_point,
    )


class ParamsForJob:
    def __init__(self):
        self.input_file = None
        self.num_fields = None
        self.validate_all_lines_same_number_of_fields = None
        self.check_non_ascii = None
        self.progress = None


def check_file(params_for_job: ParamsForJob) -> bool:
    print('checking [{}]...'.format(params_for_job.input_file))
    with TsvReader(filename=params_for_job.input_file,
                   num_fields=params_for_job.num_fields,
                   validate_all_lines_same_number_of_fields=params_for_job.validate_all_lines_same_number_of_fields,
                   check_non_ascii=params_for_job.check_non_ascii) as input_file_handle:
        if params_for_job.progress:
            input_file_handle = tqdm.tqdm(input_file_handle)
        for _ in input_file_handle:
            pass
    return True


@register_endpoint(
    configs=[
        ConfigProgress,
        ConfigParallel,
        ConfigNumFields,
        ConfigInputFiles,
        ConfigTsvReader,
    ],
    group=GROUP_NAME_DEFAULT,
)
def check() -> None:
    """
    check that every file is legal TSV

    TODO:
    - add ability to say how many lines are bad and print their content
    """
    if ConfigParallel.parallel:
        with concurrent.futures.ProcessPoolExecutor(max_workers=ConfigParallel.jobs) as executor:
            job_list = []
            for input_file in iter(ConfigInputFiles.input_files):
                job = ParamsForJob()
                job.progress = ConfigProgress.progress
                job.check_non_ascii = ConfigTsvReader.check_non_ascii
                job.num_fields = ConfigNumFields.num_fields
                job.input_file = input_file
                job.validate_all_lines_same_number_of_fields = ConfigTsvReader.validate_all_lines_same_number_of_fields
                job_list.append(job)
            results = list(executor.map(check_file, job_list))
        print(results)
    for input_file in iter(ConfigInputFiles.input_files):
        with TsvReader(
            filename=input_file,
            num_fields=ConfigNumFields.num_fields,
            validate_all_lines_same_number_of_fields=ConfigTsvReader.validate_all_lines_same_number_of_fields,
            check_non_ascii=ConfigTsvReader.check_non_ascii,
        ) as input_file_handle:
            if ConfigProgress.progress:
                input_file_handle = tqdm.tqdm(input_file_handle, desc=input_file)
            for _ in input_file_handle:
                pass


@register_endpoint(
    configs=[
        ConfigProgress,
        ConfigInputFiles,
        ConfigColumns,
    ],
    group=GROUP_NAME_DEFAULT,
)
def check_columns_unique() -> None:
    """
    checks that for certain columns every value in the files is unique
    """
    dicts = [dict() for _ in range(len(ConfigColumns.columns))]
    errors = False
    for input_file in iter(ConfigInputFiles.input_files):
        with TsvReader(
            filename=input_file,
        ) as input_file_handle:
            if ConfigProgress.progress:
                input_file_handle = tqdm.tqdm(input_file_handle, desc=input_file)
            for line_number, fields in enumerate(input_file_handle):
                for i, column in enumerate(ConfigColumns.columns):
                    value = fields[column]
                    if value in dicts[i]:
                        line = dicts[i][value]
                        print("value [{}] is duplicate on lines [{}, {}]".format(
                            value,
                            line,
                            line_number,
                        ))
                        errors = True
                    else:
                        dicts[i][value] = line_number
    assert errors is False, "found errors"


@register_endpoint(
    configs=[
        ConfigInputFile,
        ConfigOutputFile,
        ConfigProgress,
        ConfigColumns,
    ],
    group=GROUP_NAME_DEFAULT,
)
def clean_by_field_num() -> None:
    """
    remove lines from a TSV file that do not have the right number of columns
    """
    with TsvReader(
        filename=ConfigInputFile.input_file,
        validate_all_lines_same_number_of_fields=False
    ) as input_file_handle:
        with TsvWriter(filename=ConfigOutputFile.output_file) as output_file_handle:
            if ConfigProgress.progress:
                input_file_handle = tqdm.tqdm(input_file_handle, desc=ConfigInputFile.input_file)
            for fields in input_file_handle:
                if len(fields) == ConfigColumns.columns:
                    output_file_handle.write(fields)


@register_endpoint(
    configs=[
        ConfigInputFile,
        ConfigOutputFile,
        ConfigColumns,
        ConfigProgress,
    ],
    group=GROUP_NAME_DEFAULT,
)
def cut() -> None:
    """ cut fields from a TSV file """
    with TsvReader(filename=ConfigInputFile.input_file) as input_file_handle:
        with TsvWriter(filename=ConfigOutputFile.output_file) as output_file_handle:
            if ConfigProgress.progress:
                input_file_handle = tqdm.tqdm(input_file_handle)
            for fields in input_file_handle:
                out_fields = [fields[x] for x in iter(ConfigColumns.columns)]
                output_file_handle.write(out_fields)


@register_endpoint(
    configs=[
        ConfigInputFile,
        ConfigOutputFile,
        ConfigProgress,
        ConfigColumns,
    ],
    group=GROUP_NAME_DEFAULT,
)
def drop_duplicates_by_columns() -> None:
    """
    fix a TSV file assuming that bad characters or tabs have been left in one column of it
    """
    with TsvReader(filename=ConfigInputFile.input_file) as input_file_handle:
        if ConfigProgress.progress:
            input_file_handle = tqdm.tqdm(input_file_handle)
        saw = set()
        with TsvWriter(filename=ConfigOutputFile.output_file) as output_file_handle:
            for fields in input_file_handle:
                match = frozenset([fields[match_column] for match_column in iter(ConfigColumns.columns)])
                if match not in saw:
                    saw.add(match)
                    output_file_handle.write(fields)


@register_endpoint(
    configs=[
        ConfigInputFile,
        ConfigProgress,
        ConfigOutputFile,
        ConfigColumns,
        ConfigTsvReader,
        ConfigFixTypes,
    ],
    group=GROUP_NAME_DEFAULT,
)
def fix_columns() -> None:
    """
    fix a TSV file assuming that bad characters or tabs have been left in one column of it
    """
    # We need to read the input file WITHOUT assuming that it hasn't problems
    with TsvReader(
            filename=ConfigInputFile.input_file,
            check_non_ascii=ConfigTsvReader.check_non_ascii,
    ) as input_file_handle:
        if ConfigProgress.progress:
            input_file_handle = tqdm.tqdm(input_file_handle)
        with TsvWriter(filename=ConfigOutputFile.output_file) as output_file_handle:
            for fields in input_file_handle:
                for fix_column in iter(ConfigColumns.columns):
                    fields[fix_column] = clean(
                        text=fields[fix_column],
                        clean_edges=ConfigFixTypes.clean_edges,
                        sub_trailing=ConfigFixTypes.sub_trailing,
                        remove_non_ascii=ConfigFixTypes.remove_non_ascii,
                        lower_case=ConfigFixTypes.lower_case,
                    )
                output_file_handle.write(fields)


@register_endpoint(
    configs=[
        ConfigInputFile,
        ConfigOutputFile,
        ConfigColumn,
        ConfigBucketNumber,
    ],
    group=GROUP_NAME_DEFAULT,
)
def histogram_by_column() -> None:
    """ Create a histogram from a field in a TSV file """
    a = []
    total = 0
    with TsvReader(ConfigInputFile.input_file) as input_handle:
        for fields in input_handle:
            a.append(float(fields[ConfigColumn.column]))
            total += 1
    count_in_bucket, bucket_edges = numpy.histogram(a, bins=ConfigBucketNumber.bucket_number)
    with TsvWriter(ConfigOutputFile.output_file) as output_handle:
        current_sum = 0
        for i, count in enumerate(count_in_bucket):
            current_sum += count
            edge_from = bucket_edges[i]
            edge_to = bucket_edges[i + 1]
            output_handle.write([
                str(edge_from),
                str(edge_to),
                str(count),
                str(int(100.0 * current_sum / total)),
            ])


@register_endpoint(
    configs=[
        ConfigInputFile,
        ConfigOutputFile,
        ConfigProgress,
        ConfigMajority,
    ],
    group=GROUP_NAME_DEFAULT,
)
def majority() -> None:
    """
    reduce two columns to a majority

    This means that if x1 appears more
    with y2 than any other values in column Y then x1, y2 will be in the output
    and no other entry with x1 will appear
    """
    d: Dict[Dict[str, int]] = defaultdict(dict)
    with TsvReader(filename=ConfigInputFile.input_file) as input_file_handle:
        if ConfigProgress.progress:
            input_file_handle = tqdm.tqdm(input_file_handle)
        for fields in input_file_handle:
            p_first = fields[ConfigMajority.input_first_column]
            p_second = fields[ConfigMajority.input_second_column]
            p_multiplication = int(fields[ConfigMajority.input_multiplication_column])
            if p_second not in d[p_first]:
                d[p_first][p_second] = 0
            d[p_first][p_second] += p_multiplication
    with TsvWriter(filename=ConfigOutputFile.output_file) as output_file_handle:
        for p_first, p_dict in d.items():
            p_second = max(p_dict.keys(), key=lambda x, closure_dict=p_dict: closure_dict[x])
            p_count = p_dict[p_second]
            output_file_handle.write([
                p_first,
                p_second,
                str(p_count),
            ])


@register_endpoint(
    configs=[
        ConfigInputFile,
        ConfigOutputFile,
        ConfigProgress,
        ConfigColumn,
    ],
    group=GROUP_NAME_DEFAULT,
)
def multiply() -> None:
    """ multiply a TSV file according to column """
    with TsvReader(filename=ConfigInputFile.input_file) as input_file_handle:
        with TsvWriter(filename=ConfigOutputFile.output_file) as output_file_handle:
            if ConfigProgress.progress:
                input_file_handle = tqdm.tqdm(input_file_handle)
            for fields in input_file_handle:
                current_number = int(fields[ConfigColumn.column])
                for _ in range(current_number):
                    output_file_handle.write(fields)


@register_endpoint(
    configs=[
        ConfigProgress,
        ConfigInputFiles,
    ],
    group=GROUP_NAME_DEFAULT,
)
def read() -> None:
    """
    read TSV files as plainly as possible
    """
    for input_file in iter(ConfigInputFiles.input_files):
        with TsvReader(filename=input_file) as input_file_handle:
            if ConfigProgress.progress:
                input_file_handle = tqdm.tqdm(input_file_handle, desc=input_file)
            for _ in input_file_handle:
                pass


@register_endpoint(
    configs=[
        ConfigProgress,
        ConfigColumns,
        ConfigInputFile,
        ConfigOutputFile,
    ],
    group=GROUP_NAME_DEFAULT,
)
def remove_quotes() -> None:
    """ removed quotes from fields """
    with TsvReader(filename=ConfigInputFile.input_file) as input_file_handle:
        with TsvWriter(filename=ConfigOutputFile.output_file) as output_file_handle:
            if ConfigProgress.progress:
                input_file_handle = tqdm.tqdm(input_file_handle)
            for fields in input_file_handle:
                for i in iter(ConfigColumns.columns):
                    if fields[i].startswith("\"") and fields[i].endswith("\"") and len(fields[i]) > 1:
                        fields[i] = fields[i][1:-1]
                output_file_handle.write(fields)


@register_endpoint(
    configs=[
        ConfigInputFile,
        ConfigOutputFile,
        ConfigCsvToTsv,
    ],
    group=GROUP_NAME_DEFAULT,
)
def csv_to_tsv() -> None:
    """ convert a CSV to a TSV file """
    if ConfigCsvToTsv.set_max:
        csv.field_size_limit(sys.maxsize)
    with pyanyzip.core.openzip(ConfigInputFile.input_file, "rt") as input_file_handle:
        csv_reader = csv.reader(input_file_handle)
        with TsvWriter(
            filename=ConfigOutputFile.output_file,
            check_num_fields=ConfigCsvToTsv.check_num_fields,
        ) as output_file_handle:
            for row in csv_reader:
                if ConfigCsvToTsv.replace_tabs_with_spaces:
                    for i, _item in enumerate(row):
                        row[i] = row[i].replace("\t", " ")
                output_file_handle.write(row)


class MyEventTypes(Enum):
    key_not_found = 0
    key_found = 1
    unknown_added = 2


@register_endpoint(
    configs=[
        ConfigInputFile,
        ConfigOutputFile,
        ConfigProgress,
        ConfigJoin,
    ],
    group=GROUP_NAME_DEFAULT,
)
def join() -> None:
    """
    join two TSV files by column
    """
    d = dict()
    event_found = 0
    event_unknown_added = 0
    event_discarded = 0
    with TsvReader(ConfigJoin.hash_file) as hash_file_handle:
        if ConfigProgress.progress:
            hash_file_handle = tqdm.tqdm(hash_file_handle, desc="reading hash")
        for fields in hash_file_handle:
            key = fields[ConfigJoin.hash_key_column]
            value = fields[ConfigJoin.hash_value_column]
            d[key] = value
    with TsvReader(ConfigInputFile.input_file) as input_file_handle, \
            TsvWriter(ConfigOutputFile.output_file) as output_file_handle:
        if ConfigProgress.progress:
            input_file_handle = tqdm.tqdm(input_file_handle, desc="reading input and writing output")
        for fields in input_file_handle:
            key = fields[ConfigJoin.input_key_column]
            if key in d:
                event_found += 1
                new_value = d[key]
                fields.insert(ConfigJoin.output_insert_column, new_value)
                output_file_handle.write(fields)
            else:
                if ConfigJoin.output_add_unknown:
                    event_unknown_added += 1
                    fields.insert(ConfigJoin.output_insert_column, "unknown")
                    output_file_handle.write(fields)
                else:
                    event_discarded += 1
    print("event_found {}".format(event_found))
    print("event_unknown_added {}".format(event_unknown_added))
    print("event_discarded {}".format(event_discarded))


@register_endpoint(
    configs=[
        ConfigInputFile,
        ConfigOutputFile,
        ConfigColumns,
        ConfigProgress,
    ],
    group=GROUP_NAME_DEFAULT,
)
def lc() -> None:
    """ lower case some columns """
    with TsvReader(filename=ConfigInputFile.input_file) as input_file_handle:
        with TsvWriter(filename=ConfigOutputFile.output_file) as output_file_handle:
            if ConfigProgress.progress:
                input_file_handle = tqdm.tqdm(input_file_handle)
            for fields in input_file_handle:
                for i in iter(ConfigColumns.columns):
                    fields[i] = fields[i].lower()
                output_file_handle.write(fields)


@register_endpoint(
    configs=[
        ConfigInputFile,
        ConfigColumns,
        ConfigProgress,
    ],
    group=GROUP_NAME_DEFAULT,
)
def sum_columns() -> None:
    """ sum some columns """
    sums = [0] * len(ConfigColumns.columns)
    with TsvReader(filename=ConfigInputFile.input_file) as input_file_handle:
        if ConfigProgress.progress:
            input_file_handle = tqdm.tqdm(input_file_handle)
        for fields in input_file_handle:
            for n, i in enumerate(ConfigColumns.columns):
                sums[n] += float(fields[i])
    print(sums)


@attr.attrs
class JobInfo:
    check_not_ascii: bool = attr.attrib()
    input_file: str = attr.attrib()
    serial: int = attr.attrib()
    progress: bool = attr.attrib()
    pattern: str = attr.attrib()
    columns: List[int] = attr.attrib()


@attr.attrs
class JobReturnValue:
    serial: int = attr.attrib()
    files: Dict[str, str] = attr.attrib()


def process_single_file(job_info: JobInfo) -> JobReturnValue:
    logger = logging.getLogger(__name__)
    tsv_writers_dict = dict()
    results = dict()
    with TsvReader(
            filename=job_info.input_file,
            check_non_ascii=job_info.check_not_ascii
    ) as input_file_handle:
        if job_info.progress:
            logger.info("working on [{job_info.input_file}]")
            input_file_handle = tqdm.tqdm(input_file_handle)
        for fields in input_file_handle:
            key = ",".join([fields[x] for x in job_info.columns])
            if key not in tsv_writers_dict:
                filename = job_info.pattern.format(key=key, i=job_info.serial)
                results[key] = filename
                output_handle = TsvWriter(filename=filename)
                tsv_writers_dict[key] = output_handle
            output_handle = tsv_writers_dict[key]
            output_handle.write(fields)
    for v in tsv_writers_dict.values():
        v.close()
    return JobReturnValue(job_info.serial, results)


@register_endpoint(
    configs=[
        ConfigColumns,
        ConfigProgress,
        ConfigInputFiles,
        ConfigParallel,
        ConfigTsvReader,
        ConfigPattern,
    ],
    group=GROUP_NAME_DEFAULT,
)
def split_by_columns_parallel() -> None:
    """
    split a TSV file into many files according to some of its columns
    """
    pylogconf.core.setup()
    assert len(ConfigColumns.columns) > 0, "must provide --columns"
    job_data = [JobInfo(
        ConfigTsvReader.check_non_ascii,
        input_file,
        i,
        ConfigProgress.progress,
        ConfigPattern.pattern,
        ConfigColumns.columns,
    ) for i, input_file in enumerate(iter(ConfigInputFiles.input_files))]
    with concurrent.futures.ProcessPoolExecutor(max_workers=ConfigParallel.jobs) as executor:
        job_return_values: List[JobReturnValue] = list(executor.map(process_single_file, job_data))
    job_return_values.sort(key=lambda u: u.serial)
    for job_return_value in job_return_values:
        for key, _filename in job_return_value.files.items():
            outfile = ConfigPattern.final_pattern.format(key=key)
            with open(outfile, "wb") as _:
                pass
                # with open(filename, "rb") as _:


@register_endpoint(
    configs=[
        ConfigInputFile,
        ConfigTree,
    ],
    group=GROUP_NAME_DEFAULT,
)
def tree() -> None:
    """
    draw tree by two columns from a TSV file

    You can also see only parts of the tree
    """
    children_dict: Dict[Set] = defaultdict(set)
    parents_dict = defaultdict(set)
    with TsvReader(filename=ConfigInputFile.input_file) as input_file_handle:
        for fields in input_file_handle:
            p_parent = fields[ConfigTree.parent_column]
            p_child = fields[ConfigTree.child_column]
            children_dict[p_parent].add(p_child)
            parents_dict[p_child].add(p_parent)
    # find the roots (parents that have no parents)
    if ConfigTree.roots:
        list_of_roots = ConfigTree.roots
    else:
        list_of_roots = []
        for p_parent in children_dict.keys():
            if len(parents_dict[p_parent]) == 0:
                list_of_roots.append(p_parent)

    list_to_append = []
    first = True
    for root in list_of_roots:
        list_to_append.append((root, 0, first, ""))
        first = False

    stack = []
    stack.extend(list_to_append)
    # lets draw the tree
    while len(stack) > 0:
        name, depth, last, print_list = stack.pop()
        if last:
            special_string = u"└──"
        else:
            special_string = u"├──"
        print("{}{}".format(print_list + special_string, name))
        first = True
        list_to_append = []
        for p_child in children_dict[name]:
            if last:
                special_string = "   "
            else:
                special_string = u"│  "
            list_to_append.append((p_child, depth + 1, first, print_list + special_string))
            first = False
        stack.extend(list(reversed(list_to_append)))


@register_endpoint(
    configs=[
        ConfigInputFile,
        ConfigOutputFile,
    ],
    group=GROUP_NAME_DEFAULT,
)
def tsv_to_csv() -> None:
    """
    convert a TSV file to a CSV file
    """
    with open(ConfigOutputFile.output_file, "wt") as output_file_handle:
        csv_writer = csv.writer(output_file_handle)
        with TsvReader(ConfigInputFile.input_file) as input_file_handle:
            for fields in input_file_handle:
                csv_writer.writerow(fields)


@register_endpoint(
    configs=[
        ConfigInputFile,
        ConfigOutputFile,
        ConfigCheckUnique,
    ],
    group=GROUP_NAME_DEFAULT,
)
def sample_by_column() -> None:
    """
    create a weighted sample from a TSV file

    To run this you must supply a 'value_column' (the column
    which will be sampled) and a 'weight_column' which must
    be convertible to a floating point number.
    """
    logger = logging.getLogger(__name__)
    logger.info("reading the data")
    df = pandas.read_csv(
        ConfigInputFile.input_file,
        sep='\t',
        header=None,
    )
    if ConfigCheckUnique.check_unique:
        logger.info("checking that the values are unique")
        unique_values_count = df[ConfigWeightValue.value_column].nunique()
        if unique_values_count != df.shape[0]:
            logger.error("your data is not unique in the value_column")
            logger.error("unique values {} != number of rows {}".format(unique_values_count, df.shape[0]))
            return
    logger.info("sampling")
    sample = df.sample(
        n=ConfigSampleSize.size,
        replace=ConfigReplace.replace,
        weights=df[ConfigWeightValue.weight_column],
    )
    df_result = sample[ConfigWeightValue.value_column].value_counts()
    logger.info("writing the output")
    df_result.to_csv(
        ConfigOutputFile.output_file,
        sep='\t',
        index=True,
    )


@register_endpoint(
    configs=[
        ConfigInputFile,
        ConfigOutputFile,
        ConfigProgress,
        ConfigSampleByColumnOld,
    ],
    group=GROUP_NAME_DEFAULT,
)
def sample_by_column_old() -> None:
    """
    sample from a TSV file by a sample column
    """
    weights = []
    elements = []
    sum_weights = float(0)
    with TsvReader(ConfigInputFile.input_file) as input_handle:
        if ConfigProgress.progress:
            input_handle = tqdm.tqdm(input_handle)
        for fields in input_handle:
            elements.append(fields)
            weight = float(fields[ConfigSampleColumn.sample_column])
            sum_weights += weight
            weights.append(weight)
    # the following code will only work on python3.6 because the
    # random.choices API was only introduced then
    # from random import choices
    # results = choices(lines, weights, k=size)

    # this is the same code with numpy
    weights = [w / sum_weights for w in weights]
    if ConfigSampleByColumnOld.hits_mode:
        results_dict = defaultdict(int)
        for _ in range(ConfigSampleSize.size):
            current_result = numpy.random.choice(
                a=len(elements),
                replace=ConfigReplace.replace,
                size=1,
                p=weights,
            )
            current_result = current_result[0]
            results_dict[current_result] += 1
        with TsvWriter(ConfigOutputFile.output_file) as output_handle:
            for result, hits in results_dict.items():
                record = list(elements[result])
                record.append(hits)
                output_handle.write(record)
    else:
        results = numpy.random.choice(
            a=len(elements),
            replace=ConfigReplace.replace,
            size=ConfigSampleSize.size,
            p=weights,
        )
        with TsvWriter(ConfigOutputFile.output_file) as output_handle:
            for result in results:
                output_handle.write(elements[result])


@register_endpoint(
    configs=[
        ConfigInputFile,
        ConfigOutputFile,
        ConfigProgress,
        ConfigSampleByTwoColumns,
    ],
    group=GROUP_NAME_DEFAULT,
)
def sample_by_two_columns() -> None:
    """
    sample from a TSV file by two columns
    """
    logger = logging.getLogger(__name__)
    logger.info("reading the data")
    df = pandas.read_csv(
        ConfigInputFile.input_file,
        sep='\t',
        header=None,
    )
    logger.info("checking that the values are unique")
    unique_values_count = df[ConfigWeightValue.value_column].nunique()
    if ConfigCheckUnique.check_unique and unique_values_count != df.shape[0]:
        logger.error("your data is not unique in the value_column")
        logger.error("unique values {} != number of rows {}".format(unique_values_count, df.shape[0]))
        return
    logger.info("finding clusters")
    clusters = df[ConfigSampleByTwoColumns.group_column].unique()
    if ConfigProgress.progress:
        clusters = tqdm.tqdm(clusters)
    if os.path.isfile(ConfigOutputFile.output_file):
        os.unlink(ConfigOutputFile.output_file)
    for cluster in clusters:
        cluster_queries = df[df[ConfigSampleByTwoColumns.group_column] == cluster]
        sample = cluster_queries.sample(
            n=ConfigSampleSize.size,
            replace=ConfigReplace.replace,
            weights=cluster_queries[ConfigWeightValue.weight_column],
        )
        res = sample[sample.columns[ConfigWeightValue.value_column]].value_counts()
        res.to_csv(
            ConfigOutputFile.output_file,
            sep='\t',
            index=False,
            mode='a',
            header=None,
        )


@register_endpoint(
    configs=[
        ConfigColumns,
        ConfigProgress,
        ConfigTsvReader,
        ConfigInputFiles,
        ConfigPattern,
    ],
    group=GROUP_NAME_DEFAULT,
)
def split_by_columns() -> None:
    """
    split a TSV file into many files according to some of its columns
    """
    pylogconf.core.setup()
    logger = logging.getLogger(__name__)
    assert len(ConfigColumns.columns) > 0, "must provide --columns"
    tsv_writers_dict = dict()
    for input_file in iter(ConfigInputFiles.input_files):
        with TsvReader(filename=input_file, check_non_ascii=ConfigTsvReader.check_non_ascii) as input_file_handle:
            if ConfigProgress.progress:
                logger.info(f"working on [{input_file}]")
                input_file_handle = tqdm.tqdm(input_file_handle)
            for fields in input_file_handle:
                key = ",".join([fields[x] for x in iter(ConfigColumns.columns)])
                if key not in tsv_writers_dict:
                    filename = ConfigPattern.pattern.format(key=key)
                    output_handle = TsvWriter(filename=filename)
                    tsv_writers_dict[key] = output_handle
                output_handle = tsv_writers_dict[key]
                output_handle.write(fields)
    # close all writers
    for v in tsv_writers_dict.values():
        v.close()
