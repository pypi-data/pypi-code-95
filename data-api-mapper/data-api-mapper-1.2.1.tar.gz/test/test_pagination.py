import os
import unittest

import boto3
from dotenv import load_dotenv

from data_api_mapper import DataAPIClient
from functools import reduce

load_dotenv()


class TestPagination(unittest.TestCase):

    data_client = None

    @classmethod
    def setUpClass(cls):
        db_name = os.getenv('DB_NAME')
        db_cluster_arn = os.getenv('DB_CLUSTER_ARN')
        secret_arn = os.getenv('SECRET_ARN')
        rds_client = boto3.client('rds-data')
        data_client = DataAPIClient(rds_client, secret_arn, db_cluster_arn, db_name)
        cls.data_client = data_client

    def test_paginate(self):
        sql = ''' 
                select * from transaction t 
                inner join item i on t.plaid_item_id = i.plaid_item_id 
                where i.circle_id = 59 order by t.date, t.created_at
            '''
        records = self.data_client.query_paginated(sql, page_size=500)
        self.assertEqual('4Xw5YXLm6qfZy439JoVVC7DkKNeba4Tk9JAOA', records[0]['plaid_transaction_id'])
        self.assertEqual('JpL5KpoPR9FDrwaNz6m3iN1LDBZOMDHbjRaK9', records[499]['plaid_transaction_id'])
        self.assertEqual('RXOwaXNvRpfVMAPYOqpJSkDZ6B3PwmuV5YJNm', records[1352]['plaid_transaction_id'])
