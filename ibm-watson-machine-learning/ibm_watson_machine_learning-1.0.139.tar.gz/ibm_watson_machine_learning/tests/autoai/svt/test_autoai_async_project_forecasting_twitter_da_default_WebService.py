import unittest

import ibm_boto3
from ibm_watson_machine_learning.experiment import AutoAI
from ibm_watson_machine_learning.helpers.connections import DataConnection, S3Location
from ibm_watson_machine_learning.utils.autoai.errors import WMLClientError
from ibm_watson_machine_learning.tests.utils import bucket_exists, create_bucket, is_cp4d
from ibm_watson_machine_learning.tests.autoai.abstract_tests_classes import AbstractTestTSAsync, \
    AbstractTestWebservice

from ibm_watson_machine_learning.utils.autoai.enums import PredictionType, Metrics


class TestAutoAIRemote(AbstractTestTSAsync, AbstractTestWebservice, unittest.TestCase):
    """
    The test can be run on Cloud only
    """

    cos_resource = None
    data_location = './autoai/data/Twitter_volume_AMZN.csv'

    data_cos_path = 'Twitter_volume_AMZN.csv'

    SPACE_ONLY = False

    OPTIMIZER_NAME = "Twitter_volume_AMZN test sdk"

    target_space_id = None

    experiment_info = dict(
        name=OPTIMIZER_NAME,
        prediction_type=PredictionType.FORECASTING,
        prediction_columns=['value'],
        timestamp_column_name='timestamp',
        backtest_num=4,
        lookback_window=5,
        forecast_window=2,
        holdout_size=0.05,
        max_number_of_estimators=1
    )

    def test_00d_prepare_data_asset(self):
        asset_details = self.wml_client.data_assets.create(
            name=self.data_location.split('/')[-1],
            file_path=self.data_location)

        TestAutoAIRemote.asset_id = self.wml_client.data_assets.get_id(asset_details)
        self.assertIsInstance(self.asset_id, str)

    def test_02_data_reference_setup(self):
        TestAutoAIRemote.data_connection = DataConnection(data_asset_id=self.asset_id)
        TestAutoAIRemote.results_connection = None

        self.assertIsNotNone(obj=TestAutoAIRemote.data_connection)
        self.assertIsNone(obj=TestAutoAIRemote.results_connection)

    def test_99_delete_data_asset(self):
        if not self.SPACE_ONLY:
            self.wml_client.set.default_project(self.project_id)

        self.wml_client.data_assets.delete(self.asset_id)

        with self.assertRaises(WMLClientError):
            self.wml_client.data_assets.get_details(self.asset_id)


if __name__ == '__main__':
    unittest.main()
