# Copyright 2019 Okera Inc. All Rights Reserved.

# pylint: disable=too-many-lines
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-lines
#
# Tests for Mindsphere API
#
#+-----------------+-------------------------------------------+-----------------+---------+---------+---------+---------+---------+-------+
#|       rpc       |                    name                   |       user      |   mean  |   50%   |   90%   |   99%   |   max   | iters |
#+-----------------+-------------------------------------------+-----------------+---------+---------+---------+---------+---------+-------+
#| authorize_query |               abac redaction              | mindsphere_user |  45.039 |  44.190 |  46.937 |  52.385 |  52.385 |  100  |
#| authorize_query |               abac transform              | mindsphere_user |  81.275 |  81.242 |  83.454 |  96.475 |  96.475 |  100  |
#| authorize_query |                   admin                   |       None      |  0.275  |  0.268  |  0.299  |  0.571  |  0.571  |  100  |
#| authorize_query |                  admin100                 |       None      |  1.754  |  1.715  |  1.789  |  5.130  |  5.130  |  100  |
#| authorize_query |                 admin2000                 |       None      |  31.372 |  30.671 |  33.494 |  40.390 |  41.202 |  300  |
#| authorize_query |                 admin10000                |       None      | 160.864 | 155.674 | 162.530 | 431.138 | 431.138 |  100  |
#| authorize_query |                 admin25000                |       None      | 531.898 | 588.496 | 614.410 | 679.952 | 679.952 |   50  |
#| authorize_query |               all transform               | mindsphere_user |  80.292 |  80.722 |  82.161 |  89.394 |  89.394 |  100  |
#| authorize_query |              column redaction             | mindsphere_user |  8.552  |  8.441  |  8.637  |  11.164 |  11.164 |  100  |
#| authorize_query |              dax name filter              | mindsphere_user |  7.742  |  7.509  |  8.177  |  11.110 |  11.110 |  100  |
#| authorize_query |            filter folding user            | mindsphere_user |  7.819  |  7.724  |  8.046  |  10.470 |  10.470 |  100  |
#| authorize_query |         filter folding compound 1         | mindsphere_user |  7.814  |  7.754  |  7.885  |  10.286 |  10.286 |  100  |
#| authorize_query |         filter folding compound 2         | mindsphere_user |  7.865  |  7.726  |  7.895  |  12.941 |  12.941 |  100  |
#| authorize_query |         filter folding compound 3         | mindsphere_user |  7.992  |  7.858  |  8.068  |  11.502 |  11.502 |  100  |
#| authorize_query |         filter folding compound 4         | mindsphere_user |  8.017  |  7.927  |  8.112  |  10.495 |  10.495 |  100  |
#| authorize_query |              hierarchy filter             | mindsphere_user |  7.917  |  7.885  |  8.081  |  10.597 |  10.597 |  100  |
#| authorize_query |             hierarchy 2 filter            | mindsphere_user |  7.773  |  7.697  |  7.864  |  10.429 |  10.429 |  100  |
#| authorize_query |             hierarchy 0 filter            | mindsphere_user |  7.678  |  7.609  |  7.750  |  10.039 |  10.039 |  100  |
#| authorize_query |          hierarchy partial filter         | mindsphere_user |  7.991  |  7.697  |  8.511  |  12.133 |  12.133 |  100  |
#| authorize_query |           filter: hierarchy.name          | mindsphere_user |  7.471  |  7.424  |  7.516  |  9.897  |  9.897  |  100  |
#| authorize_query |               country filter              | mindsphere_user |  7.888  |  7.827  |  8.056  |  10.880 |  10.880 |  100  |
#| authorize_query |            location filter 100            | mindsphere_user |  10.559 |  10.405 |  10.785 |  14.537 |  14.537 |  100  |
#| authorize_query |              longitude filter             | mindsphere_user |  7.941  |  7.797  |  8.080  |  11.346 |  11.346 |  100  |
#| authorize_query |                name filter                | mindsphere_user |  7.765  |  7.732  |  7.847  |  10.155 |  10.155 |  100  |
#| authorize_query |              name filter 100              | mindsphere_user |  11.600 |  11.176 |  12.090 |  17.925 |  17.925 |  100  |
#| authorize_query |              name filter 2000             | mindsphere_user |  50.589 |  47.711 |  57.690 |  64.125 | 291.683 |  300  |
#| authorize_query |             name filter 10000             | mindsphere_user | 504.834 | 565.154 | 691.847 | 742.235 | 742.235 |  100  |
#| authorize_query |        nested collection redaction        | mindsphere_user |  8.439  |  8.348  |  8.471  |  11.436 |  11.436 |  100  |
#| authorize_query |          nested column redaction          | mindsphere_user |  8.459  |  8.388  |  8.510  |  10.933 |  10.933 |  100  |
#| authorize_query |              siemens filter 1             | mindsphere_user |  7.972  |  7.902  |  8.076  |  10.183 |  10.183 |  100  |
#| authorize_query |              siemens filter 2             | mindsphere_user |  8.080  |  7.945  |  8.110  |  16.536 |  16.536 |  100  |
#| authorize_query |              siemens filter 3             | mindsphere_user |  8.235  |  8.005  |  8.287  |  11.776 |  11.776 |  100  |
#| authorize_query |            hierarchyPath filter           | mindsphere_user |  7.883  |  7.823  |  7.935  |  10.381 |  10.381 |  100  |
#| authorize_query |        hierarchyPath filter partial       | mindsphere_user |  7.947  |  7.879  |  8.029  |  10.556 |  10.556 |  100  |
#| authorize_query | filter: aspects.variable.value = tenantId | mindsphere_user |  7.798  |  7.750  |  7.862  |  10.262 |  10.262 |  100  |
#| authorize_query |   filter: aspects.variable.value = name   | mindsphere_user |  7.755  |  7.704  |  7.812  |  11.013 |  11.013 |  100  |
#+-----------------+-------------------------------------------+-----------------+---------+---------+---------+---------+---------+-------+


import copy
import json
import os
import pytest
import unittest

from okera._thrift_api import TAuthorizeQueryParams
from okera._thrift_api import TAuthorizeQueryClient
from okera._thrift_api import TCompoundOp
from okera._thrift_api import TErrorCode
from okera._thrift_api import TRecordServiceException

from okera.tests import pycerebro_test_common as common

ENABLE_OR = common.get_env_var('ENABLE_OR', bool, False)
PERF = common.PerfResults()

# We don't enable grants into complex types by default. Need to
# turn on server side with flag.
# Need to run: start-cdas-container.sh \
#     -enable-complex-types-tags \
#     -env "CASCADE_NESTED_TYPES_CHECK=true"
COMPLEX_TYPES = common.get_env_var('COMPLEX_TYPES', bool, False)

ASSETS_LOC = 's3://cerebrodata-test/mindsphere/assets/example.json'
TEST_DB = 'mindsphere_test'
TEST_ROLE = 'mindsphere_role'
TEST_USER = 'mindsphere_user'

# FIXME: original record has unicode for streetAddress which gets decoded wrong. This
# is very likely a test issue.
ASSET_FULL_RECORD = {
  "name": "Millenium Falcon",
  "externalId": "SN 123456-123-123456",
  "description": "The ship of Han Solo and Chewbacca",
  "location": {
    "country": "Austria",
    "region": "Tyrol",
    "locality": "Innsbruck",
    "streetAddress": "Industriest 21 A/II",
    "postalCode": "6020",
    "longitude": 53.5125546,
    "latitude": 9.9763411
  },
  "variables": [
    {
      "name": "color",
      "value": "yellow"
    }
  ],
  "aspects": [
    {
      "name": "astroDroid",
      "variables": [
        {
          "name": "color",
          "value": "yellow"
        }
      ]
    }
  ],
  "fileAssignments": [
    {
      "key": "logo_small",
      "fileId": "c27a28b6eb16b507fabc11e75da8b4ce"
    }
  ],
  "typeId": "mdsp.spaceship",
  "parentId": "c27a28b6eb16b507fabc11e75da8b4ce",
  "timezone": "Europe/Berlin",
  "twinType": "performance",
  "tenantId": "mdsp",
  "subTenant": "UnkarPlutt Inc.",
  "t2Tenant": "DEPRECATED: use subTenant instead",
  "assetId": "c27a28b6eb16b507fabc11e75da8b4ce",
  "locks": [
    {
      "id": "c27a28b6eb16b507fabc11e75da8b4ce",
      "service": "AgentManagement",
      "reason": "Agent is onboarded, cannot delete asset until offboard finished",
      "reasonCode": "agentmanagement.agent.onboarded"
    }
  ],
  "deleted": "2020-12-03T06:27:43.126Z",
  "sharing": {
    "modes": [
      "SHARER"
    ]
  },
  "etag": 1,
  "hierarchyPath": [
    {
      "assetId": "c27a28b6eb16b507fabc11e75da8b4ce",
      "name": "Millenium Falcon's parent"
    }
  ]
}

# Make some derived records
ASSET_RECORD_GERMANY = copy.deepcopy(ASSET_FULL_RECORD)
ASSET_RECORD_GERMANY['location']['country'] = 'Germany'
ASSET_RECORD_GERMANY['name'] = 'Millenium Falcon2';
ASSET_RECORD_GERMANY['hierarchyPath'].append({"assetId": "abcd", "name": "p2"})
ASSET_RECORD_GERMANY['aspects'][0]['variables'].append({"name": "k", "value": "mdsp"})
#print(json.dumps(ASSET_RECORD_GERMANY, indent=2))

class MindsphereApiTest(common.TestBase):
    @classmethod
    def tearDownClass(cls):
        PERF.finalize_results()

    @classmethod
    def setUpClass(cls):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl("DROP DATABASE IF EXISTS %s CASCADE" % TEST_DB)
            conn.execute_ddl("CREATE DATABASE %s" % TEST_DB)
            conn.execute_ddl('''
                CREATE EXTERNAL TABLE %s.assets
                LIKE JSON '%s'
                WITH SERDEPROPERTIES('new.line.json'='false') STORED AS JSON
                LOCATION '%s'
                TBLPROPERTIES ('okera.catalog.cache-metadata'='true')
                ''' % (TEST_DB, ASSETS_LOC, ASSETS_LOC))

    def _authorize_query(self, conn, db, tbl, records, user=None,
                        client=TAuthorizeQueryClient.REST_API,
                        return_records=True, skip_result=False,
                        user_filter=None):
        request = TAuthorizeQueryParams()
        request.db = [db]
        request.dataset = tbl
        request.records = records
        request.requesting_user = user
        request.client = client
        request.return_records = return_records
        request.request_filter = user_filter
        result = conn.service.client.AuthorizeQuery(request)
        if not skip_result and result.result_records:
            result_records = []
            for r in result.result_records:
              result_records.append(json.loads(r))
            return result.filter, result_records, result
        else:
            return result.filter, None, result

    def _authorize_sql(self, conn, sql, user=None,
                       user_filter=None,
                       client=TAuthorizeQueryClient.REST_API):
        request = TAuthorizeQueryParams()
        request.sql = sql
        request.requesting_user = user
        request.client = client
        request.request_filter = user_filter
        result = conn.service.client.AuthorizeQuery(request)
        return ' '.join(result.result_sql.split())

    def _authorize_assets(self, label, conn, user, data,
                          user_filter=None, measure=False,
                          client = TAuthorizeQueryClient.REST_API):
        input_records = None
        if data is not None:
            input_records = []
            for r in data:
                input_records.append(json.dumps(r))

        def get():
            return self._authorize_query(conn, TEST_DB, 'assets', input_records,
                                         user=user, user_filter=user_filter,
                                         skip_result=True, client=client)
        if measure or PERF.run_perf():
            print()
            print('---------------------------- %s --------------------------' % label)
            PERF.measure(get, label, user, 'authorize_query')
        return self._authorize_query(conn, TEST_DB, 'assets', input_records, user=user,
                                     user_filter=user_filter, client=client)

    @pytest.mark.perf
    def test_admin(self):
        """ The tests that verify more records spend a lot of time in pytest. """
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            """
            ---------------------------- admin --------------------------
            Iterations 2000
            Mean 0.35735225677490234 ms
            50%: 0.3466606140136719 ms
            90%: 0.3914833068847656 ms
            95%: 0.40459632873535156 ms
            99%: 0.4324913024902344 ms
            99.5%: 0.44798851013183594 ms
            99.9%: 0.5857944488525391 ms
            """
            filter, records, _ = self._authorize_assets(
                "admin", conn, None, [ASSET_FULL_RECORD, ASSET_RECORD_GERMANY])
            self.assertTrue(filter is None)
            self.assertEqual(records, [ASSET_FULL_RECORD, ASSET_RECORD_GERMANY])

            """
            ------------------------------ admin100 ----------------------------
            Iterations 2000
            Mean 1.7077339887619019 ms
            50%: 1.6613006591796875 ms
            90%: 1.7123222351074219 ms
            95%: 1.7268657684326172 ms
            99%: 3.3609867095947266 ms
            99.5%: 4.5528411865234375 ms
            99.9%: 10.724544525146484 ms
            """
            records_100 = []
            for _ in range(0, 100):
                records_100.append(ASSET_FULL_RECORD)
            filter, records, _ = self._authorize_assets(
                "admin100", conn, None, records_100)
            self.assertTrue(filter is None)
            self.assertEqual(records, records_100)

            records_2000 = []
            for _ in range(0, 2000):
                records_2000.append(ASSET_FULL_RECORD)
            filter, records, _ = self._authorize_assets(
                "admin2000", conn, None, records_2000)
            self.assertTrue(filter is None)
            self.assertEqual(records, records_2000)

            records_10000 = []
            for _ in range(0, 10000):
                records_10000.append(ASSET_FULL_RECORD)
            filter, records, _ = self._authorize_assets(
                "admin10000", conn, None, records_10000)
            self.assertTrue(filter is None)
            self.assertEqual(records, records_10000)

            records_25000 = []
            for _ in range(0, 25000):
                records_25000.append(ASSET_FULL_RECORD)
            filter, records, _ = self._authorize_assets(
                "admin25000", conn, None, records_25000)
            self.assertTrue(filter is None)
            self.assertEqual(records, records_25000)

            # Get the authorized SQL query
            sql = self._authorize_sql(conn,
                "SELECT name FROM %s.assets" % TEST_DB)
            self.assertEqual(sql,
                "SELECT name FROM mindsphere_test.assets")

    @pytest.mark.perf
    def test_name_filter(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self._recreate_test_role(conn, TEST_ROLE, [TEST_USER])
            conn.execute_ddl(
                "GRANT SELECT ON TABLE %s.assets WHERE %s TO ROLE %s" %\
                (TEST_DB, "name = 'Millenium Falcon'", TEST_ROLE))

            """
            ------------------------------ name filter ----------------------------
            Iterations 2000
            Mean 0.781161904335022 ms
            50%: 0.7805824279785156 ms
            90%: 0.8177757263183594 ms
            95%: 0.8411407470703125 ms
            99%: 1.1434555053710938 ms
            99.5%: 1.1930465698242188 ms
            99.9%: 3.467082977294922 ms
            """
            filter, records, res = self._authorize_assets(
                "name filter", conn, TEST_USER,
                [ASSET_FULL_RECORD, ASSET_RECORD_GERMANY])
            self.assertEqual(filter, "name = 'Millenium Falcon'")
            self.assertEqual(records, [ASSET_FULL_RECORD])
            self.assertTrue(res.column_access is None)
            self.assertEqual(len(res.filters.filters), 1)
            self.assertEqual(res.filters.filters[0], "name = 'Millenium Falcon'")
            self.assertEqual(res.filters.op, TCompoundOp.OR)

            """
            ------------------------------ name filter 100 ----------------------------
            Iterations 2000
            Mean 3.7372668981552124 ms
            50%: 3.6094188690185547 ms
            90%: 3.6880970001220703 ms
            95%: 5.043506622314453 ms
            99%: 5.868673324584961 ms
            99.5%: 8.349895477294922 ms
            99.9%: 12.394905090332031 ms
            """
            records_100 = []
            for _ in range(0, 100):
                records_100.append(ASSET_FULL_RECORD)
            filter, records, _ = self._authorize_assets(
                "name filter 100", conn, TEST_USER, records_100)
            self.assertEqual(filter, "name = 'Millenium Falcon'")
            self.assertEqual(records, records_100)

            records_2000 = []
            for _ in range(0, 2000):
                records_2000.append(ASSET_RECORD_GERMANY)
            filter, records, _ = self._authorize_assets(
                "name filter 2000", conn, TEST_USER, records_2000)
            self.assertEqual(filter, "name = 'Millenium Falcon'")
            self.assertTrue(records is None)

            records_10000 = []
            for _ in range(0, 5000):
                records_10000.append(ASSET_FULL_RECORD)
                records_10000.append(ASSET_RECORD_GERMANY)
            filter, records, _ = self._authorize_assets(
                "name filter 10000", conn, TEST_USER, records_10000)
            self.assertEqual(filter, "name = 'Millenium Falcon'")
            self.assertEqual(len(records), 5000)

            # FIXME: broken, likely a batching issue
            #records_25000 = []
            #for _ in range(0, 5000):
            #    records_10000.append(ASSET_FULL_RECORD)
            #    records_10000.append(ASSET_RECORD_GERMANY)
            #    records_10000.append(ASSET_RECORD_GERMANY)
            #    records_10000.append(ASSET_RECORD_GERMANY)
            #    records_10000.append(ASSET_RECORD_GERMANY)
            #filter, records, _ = self._authorize_assets(
            #    "name filter 25000", conn, TEST_USER, records_25000)
            #self.assertEqual(filter, "name = 'Millenium Falcon'")
            #self.assertEqual(len(records), 5000)

            # Get the authorized SQL query
            sql = self._authorize_sql(conn,
                "SELECT name FROM %s.assets" % TEST_DB, user=TEST_USER)
            self.assertEqual(sql,
                "SELECT name FROM mindsphere_test.assets WHERE name = 'Millenium Falcon'")

    @pytest.mark.perf
    def test_location_filter(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self._recreate_test_role(conn, TEST_ROLE, [TEST_USER])
            conn.execute_ddl(
                "GRANT SELECT ON TABLE %s.assets WHERE %s TO ROLE %s" %\
                (TEST_DB, "`location`.country = 'Austria'", TEST_ROLE))

            """
            ------------------------------ country filter ----------------------------
            Iterations 2000
            Mean 0.8221160173416138 ms
            50%: 0.7987022399902344 ms
            90%: 0.8695125579833984 ms
            95%: 0.9033679962158203 ms
            99%: 1.220703125 ms
            99.5%: 1.2383460998535156 ms
            99.9%: 3.914356231689453 ms
            """
            filter, records, res = self._authorize_assets(
                "country filter", conn, TEST_USER,
                [ASSET_FULL_RECORD, ASSET_RECORD_GERMANY])
            self.assertEqual(filter, "`location`.country = 'Austria'")
            self.assertEqual(records, [ASSET_FULL_RECORD])
            self.assertTrue(res.column_access is None)
            self.assertEqual(len(res.filters.filters), 1)
            self.assertEqual(res.filters.filters[0], "`location`.country = 'Austria'")
            self.assertEqual(res.filters.op, TCompoundOp.OR)

            """
            ---------------------------- location filter 100 --------------------------
            Iterations 2000
            Mean 3.0230764150619507 ms
            50%: 2.9752254486083984 ms
            90%: 3.0531883239746094 ms
            95%: 3.080129623413086 ms
            99%: 4.962682723999023 ms
            99.5%: 5.261659622192383 ms
            99.9%: 9.050607681274414 ms
            """
            records_100 = []
            for _ in range(0, 50):
                records_100.append(ASSET_FULL_RECORD)
                records_100.append(ASSET_RECORD_GERMANY)
            filter, records, _ = self._authorize_assets(
                "location filter 100", conn, TEST_USER, records_100)
            self.assertEqual(filter, "`location`.country = 'Austria'")
            self.assertTrue(len(records), 50)

            # Get the authorized SQL query
            sql = self._authorize_sql(conn,
                "SELECT name FROM %s.assets" % TEST_DB, user=TEST_USER)
            self.assertEqual(sql,
                "SELECT name FROM mindsphere_test.assets WHERE " +
                "`location`.country = 'Austria'")

    def test_dax_filter(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self._recreate_test_role(conn, TEST_ROLE, [TEST_USER])
            conn.execute_ddl(
                "GRANT SELECT ON TABLE %s.assets WHERE %s TO ROLE %s" %\
                (TEST_DB, "name = 'Millenium Falcon'", TEST_ROLE))

            _, _, res = self._authorize_assets(
                "dax name filter", conn, TEST_USER, [], client=TAuthorizeQueryClient.DAX)
            self.assertEqual(len(res.filters.filters), 1)
            self.assertEqual(res.filters.filters[0], '[name] = "Millenium Falcon"')
            self.assertEqual(res.filters.op, TCompoundOp.OR)

    def test_longitude_filter(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self._recreate_test_role(conn, TEST_ROLE, [TEST_USER])
            conn.execute_ddl(
                "GRANT SELECT ON TABLE %s.assets WHERE %s TO ROLE %s" %\
                (TEST_DB, "`location`.longitude > 50", TEST_ROLE))
            """
            ---------------------------- longitude filter --------------------------
            Iterations 2000
            Mean 0.8221020698547363 ms
            50%: 0.8089542388916016 ms
            90%: 0.8618831634521484 ms
            95%: 0.9002685546875 ms
            99%: 0.980377197265625 ms
            99.5%: 1.0075569152832031 ms
            99.9%: 2.923727035522461 ms
            """
            filter, records, _ = self._authorize_assets(
                "longitude filter", conn, TEST_USER,
                [ASSET_FULL_RECORD, ASSET_RECORD_GERMANY])
            self.assertEqual(filter, "`location`.longitude > 50")
            self.assertEqual(records, [ASSET_FULL_RECORD, ASSET_RECORD_GERMANY])

            # Get the authorized SQL query
            sql = self._authorize_sql(conn,
                "SELECT name FROM %s.assets" % TEST_DB, user=TEST_USER)
            self.assertEqual(sql,
                "SELECT name FROM mindsphere_test.assets WHERE " +
                "`location`.longitude > 50")

    @pytest.mark.perf
    def test_hierarchy_filter(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self._recreate_test_role(conn, TEST_ROLE, [TEST_USER])
            conn.execute_ddl(
                "GRANT SELECT ON TABLE %s.assets WHERE %s TO ROLE %s" %\
                (TEST_DB, "hierarchyPath.assetId = 'c27a28b6eb16b507fabc11e75da8b4ce'",
                 TEST_ROLE))

            # Filter passes
            """
            ------------------------------ hierarchy filter ----------------------------
            Iterations 2000
            Mean 0.7893334627151489 ms
            50%: 0.7739067077636719 ms
            90%: 0.8084774017333984 ms
            95%: 0.8203983306884766 ms
            99%: 0.8497238159179688 ms
            99.5%: 0.8871555328369141 ms
            99.9%: 2.8867721557617188 ms
            """
            filter, records, _ = self._authorize_assets(
                "hierarchy filter", conn, TEST_USER,
                [ASSET_FULL_RECORD])
            self.assertEqual(filter,
                             "hierarchypath.assetid = 'c27a28b6eb16b507fabc11e75da8b4ce'")
            self.assertEqual(records, [ASSET_FULL_RECORD])

            # Filter passes both records
            """
            ------------------------------ hierarchy 2 filter ----------------------------
            Iterations 2000
            Mean 0.8403977155685425 ms
            50%: 0.8394718170166016 ms
            90%: 0.8664131164550781 ms
            95%: 0.8797645568847656 ms
            99%: 0.8983612060546875 ms
            99.5%: 0.9114742279052734 ms
            99.9%: 3.549337387084961 ms
            """
            filter, records, _ = self._authorize_assets(
                "hierarchy 2 filter", conn, TEST_USER,
                [ASSET_FULL_RECORD, ASSET_RECORD_GERMANY])
            self.assertEqual(records, [ASSET_FULL_RECORD, ASSET_RECORD_GERMANY])

            # Filter just on the second record
            self._recreate_test_role(conn, TEST_ROLE, [TEST_USER])
            conn.execute_ddl(
                "GRANT SELECT ON TABLE %s.assets WHERE %s TO ROLE %s" %\
                (TEST_DB, "hierarchyPath.assetId = 'abcd'",
                 TEST_ROLE))

            # Filter fails
            """
            ------------------------------ hierarchy 0 filter ----------------------------
            Iterations 2000
            Mean 0.7549749612808228 ms
            50%: 0.7441043853759766 ms
            90%: 0.8380413055419922 ms
            95%: 0.8676052093505859 ms
            99%: 0.9095668792724609 ms
            99.5%: 0.9407997131347656 ms
            99.9%: 2.610445022583008 ms
            """
            filter, records, _ = self._authorize_assets(
                "hierarchy 0 filter", conn, TEST_USER,
                [ASSET_FULL_RECORD])
            self.assertEqual(filter, "hierarchypath.assetid = 'abcd'")
            self.assertTrue(records is None)

            # Filter only passes one record
            """
            ----------------------- hierarchy partial filter ----------------------------
            Iterations 2000
            Mean 0.7380911111831665 ms
            50%: 0.7183551788330078 ms
            90%: 0.7965564727783203 ms
            95%: 0.8089542388916016 ms
            99%: 0.8356571197509766 ms
            99.5%: 0.8456707000732422 ms
            99.9%: 2.641439437866211 ms
            """
            filter, records, _ = self._authorize_assets(
                "hierarchy partial filter", conn, TEST_USER,
                [ASSET_FULL_RECORD, ASSET_RECORD_GERMANY])
            self.assertEqual(records, [ASSET_RECORD_GERMANY])

            # Get the authorized SQL query
            sql = self._authorize_sql(conn,
                "SELECT name FROM %s.assets" % TEST_DB, user=TEST_USER)
            self.assertEqual(sql,
                "SELECT name FROM mindsphere_test.assets " +
                "WHERE hierarchypath.assetid = 'abcd'")

    @pytest.mark.perf
    def test_variables_filter(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self._recreate_test_role(conn, TEST_ROLE, [TEST_USER])
            conn.execute_ddl(
                "GRANT SELECT ON TABLE %s.assets WHERE %s TO ROLE %s" %\
                (TEST_DB, "aspects.variables.name = 'color' " +\
                 "AND aspects.variables.value = 'yellow'", TEST_ROLE))

            # Filter should pass
            """
            --------------------------- hierarchyPath filter --------------------------
            Iterations 2000
            Mean 0.8147140741348267 ms
            50%: 0.7791519165039062 ms
            90%: 0.8702278137207031 ms
            95%: 0.8976459503173828 ms
            99%: 0.9670257568359375 ms
            99.5%: 1.1227130889892578 ms
            99.9%: 6.104707717895508 ms
            """
            filter, records, _ = self._authorize_assets(
                "hierarchyPath filter", conn, TEST_USER,
                [ASSET_FULL_RECORD])
            self.assertEqual(filter,
                             "aspects.variables.name = 'color' AND " +\
                             "aspects.variables.value = 'yellow'")
            self.assertEqual(records, [ASSET_FULL_RECORD])

            """
            ------------------ hierarchyPath filter partial --------------------------
            Iterations 2000
            Mean 0.8471413850784302 ms
            50%: 0.8230209350585938 ms
            90%: 0.9124279022216797 ms
            95%: 0.9305477142333984 ms
            99%: 0.9970664978027344 ms
            99.5%: 1.0478496551513672 ms
            99.9%: 3.6346912384033203 ms
            """
            filter, records, _ = self._authorize_assets(
                "hierarchyPath filter partial", conn, TEST_USER,
                [ASSET_FULL_RECORD, ASSET_RECORD_GERMANY])
            self.assertEqual(records, [ASSET_FULL_RECORD, ASSET_RECORD_GERMANY])

            # Test some filters that mix collection types and not. This, if naively
            # constructed as a table would be jagged (collection types are longer).
            """
            ---------------- filter: aspects.variable.value = tenantId ----------------
            Iterations 2000
            Mean 0.8313227891921997 ms
            50%: 0.8170604705810547 ms
            90%: 0.8463859558105469 ms
            95%: 0.8561611175537109 ms
            99%: 0.8795261383056641 ms
            99.5%: 0.90789794921875 ms
            99.9%: 3.557920455932617 ms
            """
            self._recreate_test_role(conn, TEST_ROLE, [TEST_USER])
            conn.execute_ddl(
                "GRANT SELECT ON TABLE %s.assets WHERE %s TO ROLE %s" %\
                (TEST_DB, "aspects.variables.value = tenantId", TEST_ROLE))
            filter, records, _ = self._authorize_assets(
                "filter: aspects.variable.value = tenantId", conn, TEST_USER,
                [ASSET_FULL_RECORD, ASSET_RECORD_GERMANY])
            self.assertEqual(filter, "aspects.variables.value = tenantid")
            self.assertEqual(records, [ASSET_RECORD_GERMANY])

            """
            Iterations 2000
            Mean 0.8139365911483765 ms
            50%: 0.7936954498291016 ms
            90%: 0.8418560028076172 ms
            95%: 0.8752346038818359 ms
            99%: 0.9112358093261719 ms
            99.5%: 0.9334087371826172 ms
            99.9%: 3.436565399169922 ms
            """
            self._recreate_test_role(conn, TEST_ROLE, [TEST_USER])
            conn.execute_ddl(
                "GRANT SELECT ON TABLE %s.assets WHERE %s TO ROLE %s" %\
                (TEST_DB, "aspects.variables.value = name", TEST_ROLE))
            filter, records, _ = self._authorize_assets(
                "filter: aspects.variable.value = name", conn, TEST_USER,
                [ASSET_FULL_RECORD, ASSET_RECORD_GERMANY])
            self.assertEqual(filter, "aspects.variables.value = name")
            self.assertTrue(records is None)

            # Get the authorized SQL query
            sql = self._authorize_sql(conn,
                "SELECT name FROM %s.assets" % TEST_DB, user=TEST_USER)
            self.assertEqual(sql,
                "SELECT name FROM mindsphere_test.assets WHERE " +
                "aspects.variables.value = name")

    @pytest.mark.perf
    def test_filter_folding(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self._recreate_test_role(conn, TEST_ROLE, [TEST_USER])
            conn.execute_ddl(
                "GRANT SELECT ON TABLE %s.assets WHERE %s TO ROLE %s" %\
                (TEST_DB, "user() = name", TEST_ROLE))

            """
            ---------------------------- filter folding user --------------------------
            Iterations 2000
            Mean 0.8202756643295288 ms
            50%: 0.7958412170410156 ms
            90%: 0.8568763732910156 ms
            95%: 0.8816719055175781 ms
            99%: 0.99945068359375 ms
            99.5%: 1.0437965393066406 ms
            99.9%: 3.7946701049804688 ms
            """
            filter, records, res = self._authorize_assets(
                "filter folding user", conn, TEST_USER,
                [ASSET_FULL_RECORD, ASSET_RECORD_GERMANY])
            self.assertEqual(filter, "name = 'mindsphere_user'")
            self.assertEqual(len(res.filters.filters), 1)
            self.assertEqual(res.filters.filters[0], "name = 'mindsphere_user'")
            self.assertEqual(res.filters.op, TCompoundOp.OR)
            self.assertTrue(records is None)

            # Get the authorized SQL query
            sql = self._authorize_sql(conn,
                "SELECT name FROM %s.assets" % TEST_DB, user=TEST_USER)
            self.assertEqual(sql,
                "SELECT name FROM mindsphere_test.assets WHERE " +
                "name = 'mindsphere_user'")

            #  Test constant folding to false
            """
            ------------------------ filter folding compound 1 ------------------------
            Iterations 2000
            Mean 0.8916885852813721 ms
            50%: 0.8323192596435547 ms
            90%: 1.0120868682861328 ms
            95%: 1.2159347534179688 ms
            99%: 1.2848377227783203 ms
            99.5%: 1.329660415649414 ms
            99.9%: 2.9823780059814453 ms
            """
            self._recreate_test_role(conn, TEST_ROLE, [TEST_USER])
            conn.execute_ddl(
                "GRANT SELECT ON TABLE %s.assets WHERE %s TO ROLE %s" %\
                (TEST_DB, "name = 'test' AND user() = 'not-a-user'", TEST_ROLE))
            filter, records, res = self._authorize_assets(
                "filter folding compound 1", conn, TEST_USER,
                [ASSET_FULL_RECORD, ASSET_RECORD_GERMANY])
            self.assertEqual(filter, "FALSE")
            self.assertEqual(len(res.filters.filters), 1)
            self.assertEqual(res.filters.filters[0], "FALSE")
            self.assertEqual(res.filters.op, TCompoundOp.OR)

            # Get the authorized SQL query
            with self.assertRaises(TRecordServiceException) as ex_ctx:
                self._authorize_sql(conn,
                    "SELECT name FROM %s.assets" % TEST_DB, user=TEST_USER)
            self.assertTrue('Access to this dataset' in str(ex_ctx.exception))

            # Test constant folding to false
            """
            --------------------- filter folding compound 2 ------------------------
            Iterations 2000
            Mean 0.7768501043319702 ms
            50%: 0.7646083831787109 ms
            90%: 0.7910728454589844 ms
            95%: 0.8072853088378906 ms
            99%: 0.8356571197509766 ms
            99.5%: 0.8499622344970703 ms
            99.9%: 2.7077198028564453 ms
            """
            self._recreate_test_role(conn, TEST_ROLE, [TEST_USER])
            conn.execute_ddl(
                "GRANT SELECT ON TABLE %s.assets WHERE %s TO ROLE %s" %\
                (TEST_DB, "user() = 'not-a-user'", TEST_ROLE))
            filter, records, res = self._authorize_assets(
                "filter folding compound 2", conn, TEST_USER,
                [ASSET_FULL_RECORD, ASSET_RECORD_GERMANY])
            self.assertEqual(filter, "FALSE")
            self.assertEqual(len(res.filters.filters), 1)
            self.assertEqual(res.filters.filters[0], "FALSE")
            self.assertEqual(res.filters.op, TCompoundOp.OR)

            # Get the authorized SQL query
            with self.assertRaises(TRecordServiceException) as ex_ctx:
                self._authorize_sql(conn,
                    "SELECT name FROM %s.assets" % TEST_DB, user=TEST_USER)
            self.assertTrue('Access to this dataset' in str(ex_ctx.exception))

            # Test constant folding to true
            """
            ---------------------- filter folding compound 3 -----------------------
            Iterations 2000
            Mean 0.8791671991348267 ms
            50%: 0.8692741394042969 ms
            90%: 0.9055137634277344 ms
            95%: 0.9191036224365234 ms
            99%: 0.9796619415283203 ms
            99.5%: 1.0118484497070312 ms
            99.9%: 2.900362014770508 ms
            """
            self._recreate_test_role(conn, TEST_ROLE, [TEST_USER])
            conn.execute_ddl(
                "GRANT SELECT ON TABLE %s.assets WHERE %s TO ROLE %s" %\
                (TEST_DB, "name = 'test' AND user() IS NOT NULL", TEST_ROLE))
            filter, records, res = self._authorize_assets(
                "filter folding compound 3", conn, TEST_USER,
                [ASSET_FULL_RECORD, ASSET_RECORD_GERMANY])
            self.assertEqual(filter, "name = 'test'")
            self.assertEqual(len(res.filters.filters), 1)
            self.assertEqual(res.filters.filters[0], "name = 'test'")
            self.assertEqual(res.filters.op, TCompoundOp.OR)

            # Get the authorized SQL query
            sql = self._authorize_sql(conn,
                "SELECT name FROM %s.assets" % TEST_DB, user=TEST_USER)
            self.assertEqual(sql,
                "SELECT name FROM mindsphere_test.assets WHERE " +
                "name = 'test'")

            # Try one with now(), should always be true
            """
            --------------------- filter folding compound 4 -----------------------
            Iterations 2000
            Mean 0.8819392919540405 ms
            50%: 0.8478164672851562 ms
            90%: 0.9102821350097656 ms
            95%: 0.9627342224121094 ms
            99%: 1.3670921325683594 ms
            99.5%: 1.4171600341796875 ms
            99.9%: 3.5381317138671875 ms
            """
            # TODO: test fails in jenkins
            self._recreate_test_role(conn, TEST_ROLE, [TEST_USER])
            conn.execute_ddl(
                "GRANT SELECT ON TABLE %s.assets WHERE %s TO ROLE %s" %\
                (TEST_DB, "hour(now()) <= 24", TEST_ROLE))
            filter, records, res = self._authorize_assets(
                "filter folding compound 4", conn, TEST_USER,
                [ASSET_FULL_RECORD, ASSET_RECORD_GERMANY])
            #self.assertTrue(filter is None)
            #self.assertTrue(res.filters is None)

            # Get the authorized SQL query
            sql = self._authorize_sql(conn,
                "SELECT name FROM %s.assets" % TEST_DB, user=TEST_USER)
            self.assertEqual(sql,
                "SELECT name FROM mindsphere_test.assets")

    @pytest.mark.perf
    def test_siemens_filters(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self._recreate_test_role(conn, TEST_ROLE, [TEST_USER])
            perm = """
            `location`.`name` = '866a64ff-d9a4-4744-af13-0483edd8ddb8' AND
            name IN ('f9bf301b-d15c-4185-b4d6-8dbe20b30430',
                     'a8ccc735-c536-49cc-9d56-811fcb100162',
                     '57d423b0-efc9-449f-bdd8-b4047ea24bf4',
                     '489ca6b1-13c8-4386-9425-3da1c677b692')
            OR (
              file.assignments = '75276c8f-cb82-4630-97f7-a42a352550a9'
              AND dayname(now()) != 'anyday')
            """
            conn.execute_ddl(
                "GRANT SELECT ON TABLE %s.assets WHERE %s TO ROLE %s" %\
                (TEST_DB, perm, TEST_ROLE))

            # dayname should be folded out
            _, _, res = self._authorize_assets(
                "siemens filter 1", conn, TEST_USER, [])
            self.assertEqual(len(res.filters.filters), 1)
            self.assertEqual(res.filters.filters[0], ' '.join(
                '''
                  `location`.name = '866a64ff-d9a4-4744-af13-0483edd8ddb8' AND
                  name IN ('f9bf301b-d15c-4185-b4d6-8dbe20b30430',
                            'a8ccc735-c536-49cc-9d56-811fcb100162',
                            '57d423b0-efc9-449f-bdd8-b4047ea24bf4',
                            '489ca6b1-13c8-4386-9425-3da1c677b692')
                  OR
                  file.assignments = '75276c8f-cb82-4630-97f7-a42a352550a9'
                '''.split()))

            # lots of folding
            _, _, res = self._authorize_assets(
                "siemens filter 2", conn, TEST_USER, [], user_filter="name='not-there'")
            self.assertEqual(len(res.filters.filters), 1)
            self.assertEqual(res.filters.filters[0], ' '.join(
                '''
                file.assignments = '75276c8f-cb82-4630-97f7-a42a352550a9' AND
                name = 'not-there'
                '''.split()))

            # lots of folding
            _, _, res = self._authorize_assets(
                "siemens filter 3", conn, TEST_USER, [],
                user_filter="name='f9bf301b-d15c-4185-b4d6-8dbe20b30430'")
            self.assertEqual(len(res.filters.filters), 1)
            self.assertEqual(res.filters.filters[0], ' '.join(
                '''
                `location`.name = '866a64ff-d9a4-4744-af13-0483edd8ddb8' AND
                name = 'f9bf301b-d15c-4185-b4d6-8dbe20b30430'
                OR
                file.assignments = '75276c8f-cb82-4630-97f7-a42a352550a9' AND
                name = 'f9bf301b-d15c-4185-b4d6-8dbe20b30430'
                '''.split()))

    @unittest.skipIf(not ENABLE_OR, "Skipping as this requires flag to enable")
    @pytest.mark.perf
    def test_multi_grants_or(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            # France OR Austria
            self._recreate_test_role(conn, TEST_ROLE, [TEST_USER])
            conn.execute_ddl(
                "GRANT SELECT ON TABLE %s.assets WHERE %s TO ROLE %s" %\
                (TEST_DB, "`location`.country = 'Austria'", TEST_ROLE))
            conn.execute_ddl(
                "GRANT SELECT ON TABLE %s.assets WHERE %s TO ROLE %s" %\
                (TEST_DB, "`location`.country = 'France'", TEST_ROLE))
            filter, records, res = self._authorize_assets(
                "filter folding compound", conn, TEST_USER,
                [ASSET_FULL_RECORD, ASSET_RECORD_GERMANY])
            self.assertEqual(len(res.filters.filters), 2)
            self.assertEqual(res.filters.filters[0], "`location`.country = 'Austria'")
            self.assertEqual(res.filters.filters[1], "`location`.country = 'France'")
            self.assertEqual(res.filters.op, TCompoundOp.OR)
            # Get the authorized SQL query
            sql = self._authorize_sql(conn,
                "SELECT name FROM %s.assets" % TEST_DB, user=TEST_USER)
            self.assertEqual(sql,
                "SELECT name FROM mindsphere_test.assets WHERE " +
                "`location`.country IN ('Austria', 'France')")

            # Add user filter: True, no-op
            filter, records, res = self._authorize_assets(
                "filter folding compound", conn, TEST_USER, None, user_filter='True')
            self.assertEqual(len(res.filters.filters), 2)
            self.assertEqual(res.filters.filters[0], "`location`.country = 'Austria'")
            self.assertEqual(res.filters.filters[1], "`location`.country = 'France'")
            self.assertEqual(res.filters.op, TCompoundOp.OR)
            # Get the authorized SQL query
            sql = self._authorize_sql(conn,
                "SELECT name FROM %s.assets" % TEST_DB, user=TEST_USER)
            self.assertEqual(sql,
                "SELECT name FROM mindsphere_test.assets WHERE " +
                "`location`.country IN ('Austria', 'France')")

            # Add user filter: False, overrides everything else (AND semantics)
            filter, records, res = self._authorize_assets(
                "filter folding compound", conn, TEST_USER, None, user_filter='False')
            self.assertEqual(len(res.filters.filters), 1)
            self.assertEqual(res.filters.filters[0], "FALSE")
            self.assertEqual(res.filters.op, TCompoundOp.OR)
            # Get the authorized SQL query
            sql = self._authorize_sql(conn,
                "SELECT name FROM %s.assets" % TEST_DB,
                user=TEST_USER, user_filter='False')
            # FIXME
            #self.assertEqual(sql,
            #    "SELECT name FROM mindsphere_test.assets WHERE FALSE")

            # Add user filter for France, this should remove the other in clause
            filter, records, res = self._authorize_assets(
                "filter folding compound", conn, TEST_USER, None,
                user_filter="`location`.country = 'France'")
            self.assertEqual(len(res.filters.filters), 1)
            self.assertEqual(res.filters.filters[0], "`location`.country = 'France'")
            self.assertEqual(res.filters.op, TCompoundOp.OR)

            # Add user filter for UK, this should become false
            filter, records, res = self._authorize_assets(
                "filter folding compound", conn, TEST_USER, None,
                user_filter="`location`.country = 'UK'")
            self.assertEqual(len(res.filters.filters), 1)
            self.assertEqual(res.filters.filters[0], "FALSE")
            self.assertEqual(res.filters.op, TCompoundOp.OR)
            # Get the authorized SQL query

            # Add user filter for France or Austria
            filter, records, res = self._authorize_assets(
                "filter folding compound", conn, TEST_USER, None,
                user_filter="`location`.country IN ('France', 'Austria')")
            self.assertEqual(len(res.filters.filters), 2)
            self.assertEqual(res.filters.filters[0], "`location`.country = 'Austria'")
            self.assertEqual(res.filters.filters[1], "`location`.country = 'France'")
            self.assertEqual(res.filters.op, TCompoundOp.OR)

            # Add user filter for France or UK, should be intersection
            filter, records, res = self._authorize_assets(
                "filter folding compound", conn, TEST_USER, None,
                user_filter="`location`.country IN ('France', 'UK')")
            self.assertEqual(len(res.filters.filters), 1)
            self.assertEqual(res.filters.filters[0], "`location`.country = 'France'")
            self.assertEqual(res.filters.op, TCompoundOp.OR)

            # Grant something that's always false, should just be dropped
            conn.execute_ddl(
                "GRANT SELECT ON TABLE %s.assets WHERE %s TO ROLE %s" %\
                (TEST_DB, "user() = 'no-a-user'", TEST_ROLE))
            filter, records, res = self._authorize_assets(
                "filter folding compound", conn, TEST_USER,
                [ASSET_FULL_RECORD, ASSET_RECORD_GERMANY])
            self.assertEqual(len(res.filters.filters), 2)
            self.assertEqual(res.filters.filters[0], "`location`.country = 'Austria'")
            self.assertEqual(res.filters.filters[1], "`location`.country = 'France'")
            self.assertEqual(res.filters.op, TCompoundOp.OR)
            # Get the authorized SQL query
            sql = self._authorize_sql(conn,
                "SELECT name FROM %s.assets" % TEST_DB, user=TEST_USER)
            self.assertEqual(sql,
                "SELECT name FROM mindsphere_test.assets WHERE " +
                "`location`.country IN ('Austria', 'France')")

            # Grant something that's always true, no more filters
            conn.execute_ddl(
                "GRANT SELECT ON TABLE %s.assets WHERE %s TO ROLE %s" %\
                (TEST_DB, "user() is not null", TEST_ROLE))
            filter, records, res = self._authorize_assets(
                "filter folding compound", conn, TEST_USER,
                [ASSET_FULL_RECORD, ASSET_RECORD_GERMANY])
            self.assertTrue(res.filters is None)
            # Get the authorized SQL query
            sql = self._authorize_sql(conn,
                "SELECT name FROM %s.assets" % TEST_DB, user=TEST_USER)
            self.assertEqual(sql,
                "SELECT name FROM mindsphere_test.assets")

    @pytest.mark.perf
    def test_invalid_filter(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self._recreate_test_role(conn, TEST_ROLE, [TEST_USER])
            # Not a path in the schema
            conn.execute_ddl(
                "GRANT SELECT ON TABLE %s.assets WHERE %s TO ROLE %s" %\
                (TEST_DB, "hierarchy.name is null", TEST_ROLE))
            with self.assertRaises(TRecordServiceException) as ex_ctx:
                self._authorize_assets(
                    "filter: hierarchy.name", conn, TEST_USER,
                    [ASSET_FULL_RECORD, ASSET_RECORD_GERMANY])
            self.assertTrue('Could not resolve' in str(ex_ctx.exception))

            """
            ------------------------- filter: hierarchy.name ------------------------
            Iterations 2000
            Mean 0.568452000617981 ms
            50%: 0.5667209625244141 ms
            90%: 0.5910396575927734 ms
            95%: 0.6008148193359375 ms
            99%: 0.6263256072998047 ms
            99.5%: 0.6392002105712891 ms
            99.9%: 0.7848739624023438 ms
            """
            filter, _, res = self._authorize_assets(
                "filter: hierarchy.name", conn, TEST_USER, None)
            self.assertEqual(filter, 'hierarchy.name IS NULL')
            self.assertEqual(res.filters.filters[0], 'hierarchy.name IS NULL')
            self.assertEqual(res.filters.op, TCompoundOp.OR)

            # Get the authorized SQL query
            with self.assertRaises(TRecordServiceException) as ex_ctx:
                self._authorize_sql(conn,
                    "SELECT name FROM %s.assets" % TEST_DB, user=TEST_USER)
            self.assertTrue('references a column' in str(ex_ctx.exception))

    @pytest.mark.perf
    def test_invalid_collection_filter(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            # Array equality
            self._recreate_test_role(conn, TEST_ROLE, [TEST_USER])
            conn.execute_ddl(
                "GRANT SELECT ON TABLE %s.assets WHERE %s TO ROLE %s" %\
                (TEST_DB, "aspects.variables = variables", TEST_ROLE))
            with self.assertRaises(TRecordServiceException) as ex_ctx:
                self._authorize_assets(
                    "list filter", conn, TEST_USER,
                    [ASSET_FULL_RECORD])
            self.assertTrue('are not comparable' in str(ex_ctx.exception))

            # References two collections that don't have the same path, this is not
            # supported now.
            self._recreate_test_role(conn, TEST_ROLE, [TEST_USER])
            conn.execute_ddl(
                "GRANT SELECT ON TABLE %s.assets WHERE %s TO ROLE %s" %\
                (TEST_DB, "aspects.variables.name = variables.value", TEST_ROLE))
            with self.assertRaises(TRecordServiceException) as ex_ctx:
                self._authorize_assets(
                    "independent collection filter", conn, TEST_USER,
                    [ASSET_FULL_RECORD])
            self.assertTrue('Filter references two independent' in str(ex_ctx.exception))

            # Get the authorized SQL query
            sql = self._authorize_sql(conn,
                "SELECT name FROM %s.assets" % TEST_DB, user=TEST_USER)
            self.assertEqual(sql,
                "SELECT name FROM mindsphere_test.assets WHERE " +
                "aspects.variables.name = variables.value")

    @pytest.mark.perf
    def test_column_redaction(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self._recreate_test_role(conn, TEST_ROLE, [TEST_USER])
            conn.execute_ddl(
                ("GRANT SELECT(name, description, timezone, `location`)" +
                "ON TABLE %s.assets TO ROLE %s") %
                (TEST_DB, TEST_ROLE))

            expected = {
                "name": "Millenium Falcon",
                "description": "The ship of Han Solo and Chewbacca",
                "location": {
                  "country": "Austria",
                  "region": "Tyrol",
                  "locality": "Innsbruck",
                  "streetAddress": "Industriest 21 A/II",
                  "postalCode": "6020",
                  "longitude": 53.5125546,
                  "latitude": 9.9763411
                },
                "timezone": "Europe/Berlin"
            }

            """
            ------------------------------ column redaction ----------------------------
            Iterations 2000
            Mean 0.8975216150283813 ms
            50%: 0.9009838104248047 ms
            90%: 0.9360313415527344 ms
            95%: 0.9505748748779297 ms
            99%: 1.0018348693847656 ms
            99.5%: 1.0476112365722656 ms
            99.9%: 20.092010498046875 ms
            """
            filter, records, res = self._authorize_assets(
                "column redaction", conn, TEST_USER,
                [ASSET_FULL_RECORD])
            self.assertTrue(filter is None)
            self.assertEqual(records, [expected])
            self.assertTrue(res.filter is None)
            self.assertEqual(len(res.column_access), 34)
            self.assertTrue(res.column_access['name'].accessible)
            # TODO: maintain case
            self.assertFalse(res.column_access['typeid'].accessible)

            # Get the authorized SQL query
            sql = self._authorize_sql(conn,
                "SELECT * FROM %s.assets" % TEST_DB, user=TEST_USER)
            self.assertEqual(sql,
                "SELECT name, description, `location` as location, timezone " +
                "FROM mindsphere_test.assets")

    @pytest.mark.perf
    def test_abac_policy(self):
        """ Test both column pruning and filtering """
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self._recreate_test_role(conn, TEST_ROLE, [TEST_USER])
            conn.delete_attribute('mindsphere_test', 'v')
            conn.create_attribute('mindsphere_test', 'v')
            conn.assign_attribute('mindsphere_test', 'v', TEST_DB, 'assets', 'name')
            conn.assign_attribute(
                'mindsphere_test', 'v', TEST_DB, 'assets', 'description')
            conn.execute_ddl(
                ("GRANT SELECT " +
                "ON TABLE %s.assets HAVING ATTRIBUTE mindsphere_test.v " +
                "WHERE %s " +
                "TO ROLE %s") %
                (TEST_DB, "name = 'Millenium Falcon'", TEST_ROLE))

            expected = {
                "name": "Millenium Falcon",
                "description": "The ship of Han Solo and Chewbacca"
            }

            """
            ---------------------------- abac redaction --------------------------
            Iterations 2000
            Mean 1.3247164487838745 ms
            50%: 1.2581348419189453 ms
            90%: 1.3637542724609375 ms
            95%: 1.7092227935791016 ms
            99%: 1.9984245300292969 ms
            99.5%: 2.070188522338867 ms
            99.9%: 5.983114242553711 ms
            """
            filter, records, res = self._authorize_assets(
                "abac redaction", conn, TEST_USER,
                [ASSET_FULL_RECORD, ASSET_RECORD_GERMANY])
            self.assertEqual(records, [expected])
            self.assertEqual(len(res.filters.filters), 1)
            self.assertEqual(res.filters.filters[0], "name = 'Millenium Falcon'")
            self.assertEqual(res.filters.op, TCompoundOp.OR)
            self.assertEqual(len(res.column_access), 34)
            self.assertTrue(res.column_access['name'].accessible)
            self.assertTrue(res.column_access['description'].accessible)
            self.assertFalse(res.column_access['subtenant'].accessible)

            # Get the authorized SQL query
            sql = self._authorize_sql(conn,
                "SELECT * FROM %s.assets" % TEST_DB, user=TEST_USER)
            self.assertEqual(sql,
                "SELECT name, description FROM mindsphere_test.assets " +
                "WHERE name = 'Millenium Falcon'")

    @pytest.mark.perf
    def test_abac_transform(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self._recreate_test_role(conn, TEST_ROLE, [TEST_USER])
            conn.delete_attribute('mindsphere_test', 'v')
            conn.create_attribute('mindsphere_test', 'v')
            conn.delete_attribute('mindsphere_test', 'v2')
            conn.create_attribute('mindsphere_test', 'v2')
            conn.assign_attribute('mindsphere_test', 'v', TEST_DB, 'assets', 'name')
            conn.assign_attribute('mindsphere_test', 'v2', TEST_DB, 'assets', 'deleted')
            conn.assign_attribute(
                'mindsphere_test', 'v', TEST_DB, 'assets', 'description')
            conn.execute_ddl(
                ("GRANT SELECT " +
                "ON TABLE %s.assets HAVING ATTRIBUTE mindsphere_test.v " +
                "TRANSFORM mindsphere_test.v WITH upper() " +
                "TO ROLE %s") %
                (TEST_DB, TEST_ROLE))

            expected = [
                {
                    "name": "MILLENIUM FALCON",
                    "description": "THE SHIP OF HAN SOLO AND CHEWBACCA"
                },
                {
                    "name": "MILLENIUM FALCON2",
                    "description": "THE SHIP OF HAN SOLO AND CHEWBACCA"
                }]

            filter, records, res = self._authorize_assets(
                "abac transform", conn, TEST_USER,
                [ASSET_FULL_RECORD, ASSET_RECORD_GERMANY])
            self.assertEqual(records, expected)
            self.assertTrue(res.filters is None)
            self.assertFalse(res.column_access['name'].accessible)
            self.assertFalse(res.column_access['description'].accessible)

            # Get the authorized SQL query
            sql = self._authorize_sql(conn,
                "SELECT * FROM %s.assets" % TEST_DB, user=TEST_USER)
            self.assertEqual(sql,
                "SELECT upper(name) as name, upper(description) as description " +
                "FROM mindsphere_test.assets")

            # Transform on date column
            conn.execute_ddl(
                ("GRANT SELECT " +
                "ON TABLE %s.assets HAVING ATTRIBUTE mindsphere_test.v2 " +
                "TRANSFORM mindsphere_test.v2 WITH tokenize() " +
                "TO ROLE %s") %
                (TEST_DB, TEST_ROLE))

            filter, records, res = self._authorize_assets(
                "abac transform date", conn, TEST_USER,
                [ASSET_FULL_RECORD, ASSET_RECORD_GERMANY])
            print(records)
            expected = [
                {
                    "name": "MILLENIUM FALCON",
                    "description": "THE SHIP OF HAN SOLO AND CHEWBACCA",
                    "deleted": "2003-09-17 18:00:29"
                },
                {
                    "name": "MILLENIUM FALCON2",
                    "description": "THE SHIP OF HAN SOLO AND CHEWBACCA",
                    "deleted": "2003-09-17 18:00:29"
                }]
            self.assertEqual(records, expected)

    @pytest.mark.perf
    def test_all_transform(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self._recreate_test_role(conn, TEST_ROLE, [TEST_USER])
            conn.delete_attribute('mindsphere_test', 'v')
            conn.create_attribute('mindsphere_test', 'v')
            conn.assign_attribute(
                'mindsphere_test', 'v', TEST_DB, 'assets', 'name')
            conn.assign_attribute(
                'mindsphere_test', 'v', TEST_DB, 'assets', 'location.region')
            conn.assign_attribute(
                'mindsphere_test', 'v', TEST_DB, 'assets', 'location.latitude')
            conn.assign_attribute(
                'mindsphere_test', 'v', TEST_DB, 'assets', 'variables.value')
            conn.assign_attribute(
                'mindsphere_test', 'v', TEST_DB, 'assets', 'aspects.variables.name')
            conn.assign_attribute(
                'mindsphere_test', 'v', TEST_DB, 'assets', 'hierarchy.name')
            conn.execute_ddl(
                ("GRANT SELECT " +
                "ON TABLE %s.assets HAVING ATTRIBUTE mindsphere_test.v " +
                "TRANSFORM mindsphere_test.v WITH tokenize() " +
                "TO ROLE %s") %
                (TEST_DB, TEST_ROLE))

            expected = [
                {
                  "aspects": [
                    { "variables": [ { "name": "kjquw" } ] }
                  ],
                  "name": "Mkoykyajx Mzqhfu",
                  "location": {
                    "latitude": 0.2897330143551365,
                    "region": "Jjaei"
                  },
                  "variables": [ { "value": "otcoed" } ]
                },
                {
                  "aspects": [
                    {
                      "variables": [
                        { "name": "kjquw" },
                        { "name": "o" }
                      ]
                    }
                  ],
                  "name": "Kiusuotqo Gyefiu3",
                  "location": {
                    "latitude": 0.2897330143551365,
                    "region": "Jjaei"
                  },
                  "variables": [
                    { "value": "otcoed" }
                  ]
                }
              ]

            """
            ---------------------------- all transform --------------------------
            Iterations 2000
            Mean 2.1513285636901855 ms
            50%: 1.9679069519042969 ms
            90%: 2.796173095703125 ms
            95%: 3.0193328857421875 ms
            99%: 3.673553466796875 ms
            99.5%: 3.9212703704833984 ms
            99.9%: 7.477521896362305 ms
            """
            filter, records, _ = self._authorize_assets(
                "all transform", conn, TEST_USER,
                [ASSET_FULL_RECORD, ASSET_RECORD_GERMANY])
            if COMPLEX_TYPES:
              self.assertEqual(records, expected)
              # Get the authorized SQL query
              sql = self._authorize_sql(conn,
                  "SELECT * FROM %s.assets" % TEST_DB, user=TEST_USER)
              self.assertEqual(sql,
                  "SELECT tokenize(name) as name FROM mindsphere_test.assets")

    @pytest.mark.perf
    def test_nested_column_redaction(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self._recreate_test_role(conn, TEST_ROLE, [TEST_USER])
            conn.execute_ddl(
                ("GRANT SELECT(name, description, timezone, `location`.country)" +
                "ON TABLE %s.assets TO ROLE %s") %
                (TEST_DB, TEST_ROLE))

            expected1 = {
                "name": "Millenium Falcon",
                "description": "The ship of Han Solo and Chewbacca",
                "location": {
                  "country": "Austria"
                },
                "timezone": "Europe/Berlin"
            }
            expected2 = {
                "name": "Millenium Falcon2",
                "description": "The ship of Han Solo and Chewbacca",
                "location": {
                  "country": "Germany"
                },
                "timezone": "Europe/Berlin"
            }

            """
            ------------------------- nested column redaction ------------------------
            Iterations 2000
            Mean 0.9464281797409058 ms
            50%: 0.9407997131347656 ms
            90%: 0.9677410125732422 ms
            95%: 0.9849071502685547 ms
            99%: 1.0006427764892578 ms
            99.5%: 1.0123252868652344 ms
            99.9%: 5.828619003295898 ms
            """
            filter, records, _ = self._authorize_assets(
                "nested column redaction", conn, TEST_USER,
                [ASSET_FULL_RECORD, ASSET_RECORD_GERMANY])
            if COMPLEX_TYPES:
                self.assertEqual(records, [expected1, expected2])

            # Not enabled by default
            #sql = self._authorize_sql(conn,
            #    "SELECT * FROM %s.assets" % TEST_DB, user=TEST_USER)
            #self.assertEqual(sql,
            #    "SELECT upper(name) as name, upper(description) as description " +
            #    "FROM mindsphere_test.assets")

    @pytest.mark.perf
    def test_nested_collection_redaction(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self._recreate_test_role(conn, TEST_ROLE, [TEST_USER])
            conn.execute_ddl(
                ("GRANT SELECT(name, `location`.country, aspects.variables.name)" +
                "ON TABLE %s.assets TO ROLE %s") %
                (TEST_DB, TEST_ROLE))

            expected1 = {
                "name": "Millenium Falcon",
                "location": {
                  "country": "Austria"
                },
                "aspects": [{
                  "variables": [
                    {"name": "color"}
                  ]
                }]
            }
            expected2 = {
                "name": "Millenium Falcon2",
                "location": {
                  "country": "Germany"
                },
                "aspects": [{
                  "variables": [
                    {"name": "color"},
                    {"name": "k"},
                  ]
                }]
            }

            """
            --------------------- nested collection redaction -----------------------
            Iterations 2000
            Mean 0.9543460607528687 ms
            50%: 0.9477138519287109 ms
            90%: 0.9794235229492188 ms
            95%: 0.9908676147460938 ms
            99%: 1.008749008178711 ms
            99.5%: 1.0216236114501953 ms
            99.9%: 7.871389389038086 ms
            """
            filter, records, _ = self._authorize_assets(
                "nested collection redaction", conn, TEST_USER,
                [ASSET_FULL_RECORD, ASSET_RECORD_GERMANY])
            if COMPLEX_TYPES:
                self.assertEqual(records, [expected1, expected2])
                sql = self._authorize_sql(conn,
                    "SELECT * FROM %s.assets" % TEST_DB, user=TEST_USER)
                # FIXME: this is not right
                self.assertEqual(sql,
                    "SELECT name FROM mindsphere_test.assets")

if __name__ == "__main__":
    unittest.main()
