import unittest
import sys
import os
import pandas as pd

base_dir = f'{os.path.dirname(os.path.abspath(""))}/bools'
sys.path.append(base_dir)

from bools.dbc import InfluxDB
from bools.datetime import Datetime, Timedelta


class InfluxDBTest(unittest.TestCase):
    influxdb = InfluxDB(database='bowaer', user='bowaer', password='cb1998827', patch_pandas=True)
    # influxdb.drop_measurement('test')

    def test_init(self):
        print(self.influxdb.version)

    def test_query(self):
        # print(self.influxdb.query('select * from edges'))
        self.influxdb.query('select * from edges', batch_size=50)
        self.influxdb.query('select * from edges', database='abc')
        self.influxdb.query('select * from edges', database='abc')
        # print(self.influxdb.query('abc * from edges', database='abc'))  # test error sql

    @staticmethod
    def test_pandas_read():
        df = pd.read_influxdb('select * from "test","abc"')
        # assert df.shape[0] == 100
        print(df.head())
        print(df.shape)

    def test_action(self):
        self.influxdb.create_database('bowaer')
        self.influxdb.create_database('test')
        self.influxdb.create_database('def')
        self.influxdb.drop_database('def')
        self.influxdb.drop_database('test')
        self.influxdb.drop_measurement('edges')

    def test_write(self):
        # self.influxdb.drop_measurement('test')
        # self.influxdb.write([
        #     f'test,src=test count={i},succ_count={i} {int(Datetime.now().timestamp()+i*60)*1000000000}'
        #     for i in range(50)
        # ], precision='', batch_size=13)
        pass

    def test_pandas_write(self):
        # self.influxdb.drop_measurement('test')
        # pd.DataFrame({
        #     'time': [Datetime.now().timestamp() + i for i in range(100000)],
        #     # 'measurement': ['edges'] * 10,
        #     'src': ['bowaer'] * 100000,
        #     'count': range(100000),
        #     'succ_count': range(100000)
        # }).to_influxdb(measurement='test', time_col='time', tag_cols=['src'])
        pass

    def test_time(self):
        from bools.functools import timeit
        from influxdb import DataFrameClient
        data = pd.DataFrame({
            'time': [(Datetime.now() + Timedelta(minutes=i)).str for i in range(100000)],
            # 'measurement': ['edges'] * 10,
            'src': ['bowaer'] * 100000,
            'count': range(100000),
            'succ_count': range(100000)
        })
        data.index = data.pop('time')
        # influx = DataFrameClient(host='10.0.80.167', port=7076, database='test', username='bowaer',
        #                          password='cb1998827')
        #
        # timeit(lambda: influx.write_points(
        #     data, 'test', tag_columns=['src'], protocol='line'
        # ))()
        timeit(lambda: data.to_influxdb(measurement='test', tag_cols=['src'], batch_size=10000))()
        # pass


if __name__ == '__main__':
    unittest.main()
