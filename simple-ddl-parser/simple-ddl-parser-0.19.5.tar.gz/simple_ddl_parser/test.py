from simple_ddl_parser import DDLParser

ddl = """
        CREATE EXTERNAL TABLE test (
        job_id STRING COMMENT 'test'
        )
        STORED AS PARQUET LOCATION 'hdfs://test'
"""
result = DDLParser(ddl).run(group_by_type=True, output_mode='hql')
import pprint

pprint.pprint(result)
