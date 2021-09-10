import abc
import datetime

import pandas as pd
from galileodb.factory import create_experiment_database_from_env, create_influxdb_from_env, create_mysql_from_env
from galileodb.influx.db import InfluxExperimentDatabase
from galileodb.sql.adapter import ExperimentSQLDatabase

from galileojp import env


def to_idlist(exp_ids):
    idlist = ', '.join([f'"{i}"' for i in exp_ids])
    return idlist


class ExperimentFrameGateway(abc.ABC):

    def experiments(self) -> pd.DataFrame:
        raise NotImplementedError()

    def nodeinfo(self, *exp_ids):
        raise NotImplementedError()

    def events(self, *exp_ids):
        raise NotImplementedError()

    def telemetry(self, *exp_ids) -> pd.DataFrame:
        raise NotImplementedError()

    def traces(self, *exp_ids) -> pd.DataFrame:
        raise NotImplementedError()

    @staticmethod
    def from_env() -> 'ExperimentFrameGateway':
        raise NotImplementedError()


class MixedExperimentFrameGateway(ExperimentFrameGateway):

    def __init__(self, inflxudb: InfluxExperimentDatabase, sqldb: ExperimentSQLDatabase):
        self.influxdb = inflxudb
        self.sqldb = sqldb

    @property
    def _sql_con(self):
        return self.sqldb.db

    @property
    def _influxdb_client(self):
        return self.influxdb.client

    def experiments(self) -> pd.DataFrame:
        return pd.read_sql(f'SELECT * FROM experiments', con=self._sql_con)

    def nodeinfo(self, *exp_ids):
        if not exp_ids:
            raise ValueError

        idlist = to_idlist(exp_ids)

        df = pd.read_sql(f'SELECT * FROM nodeinfo WHERE exp_id in ({idlist})', con=self._sql_con)
        return df

    def raw_influxdb_query(self, query: str) -> pd.DataFrame:
        return self.influxdb.client.query_api().query_data_frame(org=self.influxdb.org_name, query=query)

    def events(self, *exp_ids):
        return self._get_influxdb_df('events', 'ts', *exp_ids)

    def telemetry(self, *exp_ids) -> pd.DataFrame:
        return self._get_influxdb_df('telemetry', 'ts', *exp_ids)

    def traces(self, *exp_ids) -> pd.DataFrame:
        return self._get_influxdb_df('traces', 'sent', *exp_ids)

    def _get_influxdb_df(self, measurement: str, time_col: str, *exp_ids) -> pd.DataFrame:
        if not exp_ids:
            raise ValueError()

        telemetry_dfs = []
        stop = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        stop = stop.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        for exp_id in exp_ids:
            query = f"""
                     from(bucket: "{exp_id}")
                         |> range(start: 1970-01-01, stop: {stop})
                         |> filter(fn: (r) => r["_measurement"] == "{measurement}")
                    """
            telemetry_dfs.append(self.raw_influxdb_query(query))

        df = pd.concat(telemetry_dfs)
        if len(df) == 0:
            raise ValueError("Empty dataframes")
        df.rename(columns={'_value': 'value'}, inplace=True)
        df.index = pd.DatetimeIndex(pd.to_datetime(df[time_col], unit='s'))
        return df

    @staticmethod
    def from_env() -> 'ExperimentFrameGateway':
        env.load()
        influxdb = create_influxdb_from_env()
        influxdb.open()
        sqldb = create_mysql_from_env()
        sqldb.open()
        return MixedExperimentFrameGateway(influxdb, sqldb)


class SqlExperimentFrameGateway(ExperimentFrameGateway):

    def __init__(self, edb: ExperimentSQLDatabase) -> None:
        super().__init__()
        self.edb = edb

    @property
    def _con(self):
        return self.edb.db.connection

    def experiments(self) -> pd.DataFrame:
        return pd.read_sql(f'SELECT * FROM experiments', con=self._con)

    def nodeinfo(self, *exp_ids):
        if not exp_ids:
            raise ValueError

        idlist = to_idlist(exp_ids)

        df = pd.read_sql(f'SELECT * FROM nodeinfo WHERE exp_id in ({idlist})', con=self._con)
        return df

    def events(self, *exp_ids):
        if not exp_ids:
            raise ValueError

        idlist = to_idlist(exp_ids)

        df = pd.read_sql(f'SELECT * FROM events WHERE exp_id in ({idlist})', con=self._con)
        df.index = pd.DatetimeIndex(pd.to_datetime(df['TIMESTAMP'], unit='s'))
        return df

    def telemetry(self, *exp_ids) -> pd.DataFrame:
        if not exp_ids:
            raise ValueError

        idlist = to_idlist(exp_ids)

        df = pd.read_sql(f'SELECT * FROM telemetry WHERE exp_id in ({idlist})', con=self._con)
        df.index = pd.DatetimeIndex(pd.to_datetime(df['TIMESTAMP'], unit='s'))
        return df

    @staticmethod
    def from_env() -> 'ExperimentFrameGateway':
        env.load()
        return ExperimentFrameGateway(create_experiment_database_from_env())


if __name__ == '__main__':
    gw = MixedExperimentFrameGateway.from_env()
    gw.traces('202109091253-de94')