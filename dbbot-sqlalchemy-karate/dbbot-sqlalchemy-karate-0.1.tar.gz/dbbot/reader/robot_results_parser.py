#  Copyright 2013-2014 Nokia Solutions and Networks
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import with_statement
from datetime import date, datetime
from hashlib import sha1
from robot import result
from robot.api import ExecutionResult
from sqlalchemy.exc import IntegrityError
import json
from jsonpath_rw_ext import parse


from dbbot import Logger


class RobotResultsParser(object):

    def __init__(self, include_keywords, db, verbose_stream):
        self._verbose = Logger('Parser', verbose_stream)
        self._include_keywords = include_keywords
        self._db = db

    def json_to_db(self, json_file, build_number):
        karateSummary = open(json_file)
        karateResult = json.load(karateSummary)
        karateSummary.close()

        # get statistic result
        featuresPassed = parse('$.featuresPassed').find(karateResult)
        featuresFailed = parse('$.featuresFailed').find(karateResult)
        cntPassed = featuresPassed[0].value
        cntFailed = featuresFailed[0].value
        resultDate = parse('$.resultDate').find(karateResult)
        resultDateParsed = resultDate[0].value
        # get elapsed time
        elapsedTime = parse('$.elapsedTime').find(karateResult)
        elapsedTimeInt = int(elapsedTime[0].value)

        dateTimeStartedAt = datetime.strptime(resultDateParsed, '%Y-%m-%d %H:%M:%S %p')
        hash_string = self._hash(json_file)
        try:
            test_run_id = self._db.insert('test_runs', {
                'hash': hash_string,
                'imported_at': datetime.utcnow(),
                'started_at':dateTimeStartedAt,
                'elapsed': elapsedTimeInt,
                'failed': cntFailed,
                'passed': cntPassed,
                'build_number': build_number
            })
        except IntegrityError:
            test_run_id = self._db.fetch_id('test_runs', {
                'elapsed': elapsedTimeInt,
                'failed': cntFailed,
                'passed': cntPassed,
                'build_number': build_number
            })
        successFeatureFiles = parse('$.featureSummary[?(@.failed == false)]').find(karateResult)
        for successFeature in successFeatureFiles:
            try:
                test_id = self._db.insert('tests', {
                'name': successFeature.value['packageQualifiedName'].split('.')[-1],
                'package_name': successFeature.value['packageQualifiedName'],
                'suite': successFeature.value['packageQualifiedName'].split('.')[-2],
            })
            except IntegrityError:
                test_id = self._db.fetch_id('tests', {
                'name': successFeature.value['packageQualifiedName'].rsplit('.', 1)[-1],
                'package_name': successFeature.value['packageQualifiedName'],
                'suite': successFeature.value['packageQualifiedName'].split('.')[-2],
            })
            self._db.insert_or_ignore('test_status', {
            'test_run_id': test_run_id,
            'test_id': test_id,
            'status': 'PASS',
            'elapsed': successFeature.value['durationMillis']
        })
        failedFeatureFiles = parse('$.featureSummary[?(@.failed == true)]').find(karateResult)
        for failedFeature in failedFeatureFiles:
            try:
                test_id = self._db.insert('tests', {
                'name': failedFeature.value['packageQualifiedName'].rsplit('.', 1)[-1],
                'package_name': failedFeature.value['packageQualifiedName'],
                'suite': failedFeature.value['packageQualifiedName'].split('.')[-2],
            })
            except IntegrityError:
                test_id = self._db.fetch_id('tests', {
                'name': failedFeature.value['packageQualifiedName'].rsplit('.', 1)[-1],
                'package_name': failedFeature.value['packageQualifiedName'],
                'suite': failedFeature.value['packageQualifiedName'].split('.')[-2],
            })
            self._db.insert_or_ignore('test_status', {
            'test_run_id': test_run_id,
            'test_id': test_id,
            'status': 'FAIL',
            'elapsed': failedFeature.value['durationMillis']
        })

    @staticmethod
    def _hash(json_file):
        block_size = 68157440
        hasher = sha1()
        with open(json_file, 'rb') as f:
            chunk = f.read(block_size)
            while len(chunk) > 0:
                hasher.update(chunk)
                chunk = f.read(block_size)
        return hasher.hexdigest()

    @staticmethod
    def _format_robot_timestamp(timestamp):
        return datetime.strptime(timestamp, '%Y%m%d %H:%M:%S.%f') if timestamp else None

    @staticmethod
    def _string_hash(string):
        return sha1(string.encode()).hexdigest() if string else None
