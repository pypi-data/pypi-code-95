# Copyright Okera Inc.

from __future__ import absolute_import

import csv
import datetime
import io

from okera._thrift_api import (TTypeId)

def __gen_random_data(t, idx):
    if t.type.type_id == TTypeId.STRING or t.type.type_id == TTypeId.VARCHAR:
        return "string_%d" % idx
    elif t.type.type_id == TTypeId.CHAR:
        return "char_%d" % idx
    elif t.type.type_id == TTypeId.BOOLEAN:
        if idx % 2 == 0:
            return True
        return False
    elif t.type.type_id == TTypeId.TINYINT:
        return idx
    elif t.type.type_id == TTypeId.SMALLINT:
        return idx
    elif t.type.type_id == TTypeId.INT:
        return idx
    elif t.type.type_id == TTypeId.BIGINT:
        return idx
    elif t.type.type_id == TTypeId.FLOAT:
        return idx
    elif t.type.type_id == TTypeId.DOUBLE:
        return idx
    elif t.type.type_id == TTypeId.DATE:
        epoch = datetime.datetime(1970, 1, 1, 0, 0)
        return (epoch + datetime.timedelta(idx)).date()
    elif t.type.type_id == TTypeId.TIMESTAMP_NANOS:
        return datetime.datetime.fromtimestamp(idx)
    elif t.type.type_id == TTypeId.DECIMAL:
      return idx
    else:
        raise RuntimeError(
            "Unsupported type: " + TTypeId._VALUES_TO_NAMES[t.type.type_id])

def gen_random_data(conn, db, name, num_records=10):
    """ Generates random data data that matches the schema for this dataset.

        Parameters
        ----------
        conn : PlannerConnection
            Connection to a planner.

        db : str
            Database containing this dataset.

        name : str
            Name of this dataset.

        num_records : int, optional
            Number of records to generate. Default is 10.

        Returns
        -------
        list(list(object))
            Returns the result as a table.
    """
    datasets = conn.list_datasets(db, name=name)
    if not datasets:
        raise RuntimeError("Invalid dataset: %s.%s" % (db, name))
    schema = datasets[0].schema
    data = []
    for i in range(0, num_records):
        row = []
        for col in schema.cols:
            row.append(__gen_random_data(col, i))
        data.append(row)
    return data

def gen_random_csv(conn, db, name, num_records=10):
    """ Generates random CSV formatted data that matches the schema for this dataset.

        Parameters
        ----------
        conn : PlannerConnection
            Connection to a planner.

        db : str
            Database containing this dataset.

        name : str
            Name of this dataset.

        num_records : int, optional
            Number of records to generate. Default is 10.

        Returns
        -------
        str
            Returns generated CSV.
    """
    data = gen_random_data(conn, db, name, num_records)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows(data)
    return output.getvalue().strip()

