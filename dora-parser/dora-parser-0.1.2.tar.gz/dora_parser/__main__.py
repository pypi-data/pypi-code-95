# -*- coding: utf-8 -*-
#
# Copyright 2021 Compasso UOL
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Dora Parser Command Line interface"""
import fire
from dora_parser.parser import Parser
from dora_parser.transpiler import Transpiler
from dora_parser.reader import Reader

def cli_translate(from_dialect:str='impala', to_dialect:str='athena', query:str=None, script:str=None, input_dir=None, output_dir=None, summary:bool=False, migration_report:bool=False):
    """ CLI translate class
    :param from_dialect: From SQL dialect
    :param to_dialect: To SQL dialect
    :param query: Query to translate
    :param script: Script to translate
    :param input_dir: Input Directory
    :param output_dir: Optional output Directory
    :param summary: Optional summary of sucesseded and failed queries
    :param migration_report: If true, creates the migration report
    """
    if query is not None:
        transpiler = Transpiler(from_dialect, to_dialect)
        result, errors = transpiler.translate(Parser(query))
        if len(errors) ==0:
            return f"\nResult: {result}"
        return f"\nResult: {result} \nErrors: {errors}\n"
    if script is not None:
        errors_ = []
        reader = Reader(from_dialect, to_dialect)
        result, errors, n_queries = reader.translate_script(script)
        if summary is not False:
            summary_ = reader.create_summary(errors, n_queries)
            print("\nSummary: ",summary_)
        #Remove from the list the elements that are empty, to present a cleaner output
        for error in errors:
            if len(error) != 0: 
                errors_.append(error)
        if len(errors_) ==0:
            return f"\nResult: {result}" 
        return f"\nResult: {result} \nErrors: {errors_} \nNumber of queries: {n_queries}" 
    if input_dir is not None:
        reader = Reader(from_dialect, to_dialect, input_dir, output_dir, migration_report)
        reader.translate_files()
        if summary is not False:
            summary_ = reader.translate_files(summary_dict=True)
            print("\nSummary: ",summary_)
        if output_dir is not None:
            return f"\nTranspiled statements are in {output_dir}Fully Translated/ and {output_dir}Partially Translated/ folders."
        return f"\nTranspiled statements are in {input_dir}Fully Translated/ and {input_dir}Partially Translated/ folders."

if __name__ == '__main__':
    fire.Fire(cli_translate)
