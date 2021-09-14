import os, sys
import logging as logger, pandas as pd, StringIO
import requests
# import pandas as pd
try:
    import findspark
    findspark.init()
    spark_get = findspark.find()
    print(spark_get) #os.environ['SPARK_HOME'])
except:
    # Check if pyspark unavailable
    print('Kindly setup for pyspark')

# In[1]:
try:
    from delta import *

    import pyspark
    from pyspark import SparkContext, SparkConf

    print('pyspark checked!')

except:
    print('pyspark unavailable..')

from pyspark.sql import SQLContext, SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import *

# builder = pyspark.sql.SparkSession.builder.appName("DTL Pipe") \
#     .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
#     .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
#     .getOrCreate()

# # spark = spark = configure_spark_with_delta_pip(builder)
# print('SPARK UI :: ', builder)

# only_one_dat = builder.read.csv("Data/*.csv", header=True).cache()
# builder.registerTemptable("table1")

def main(source, target):
    try:
        etl_run = ETL_Spark('','')
        dataframe = etl_run.read_s3(source)
        etl_run.dataframe_to_s3(dataframe, 'orc', target, 'overwrite', Header='true')
    except Exception as e:
        logger.error(e)

# In[2]:

class ETL_Spark:
    def __init__(self, accessKeyId, secretAccessKey):
        self.conf = SparkConf().set('spark.executor.extraJavaOptions','-Dcom.amazonaws.services.s3.enableV4=true'). \
                        set('spark.driver.extraJavaOptions','-Dcom.amazonaws.services.s3.enableV4=true'). \
                        setAppName('TG_DTL_Pipeline').setMaster('local') # Spark UI
        
        self.sc = SparkContext(conf=self.conf).getOrCreate()
        self.sc.setSystemProperty('com.amazonaws.services.s3.enableV4', 'true')
        
        logger.info('modules imported')
        
        self.hadoopConf = self.sc._jsc.hadoopConfiguration()
        self.hadoopConf.set('fs.s3a.access.key', accessKeyId)
        self.hadoopConf.set('fs.s3a.secret.key', secretAccessKey)
        self.hadoopConf.set('fs.s3a.endpoint', 's3-us-east-2.amazonaws.com')
        self.hadoopConf.set('fs.s3a.impl', 'org.apache.hadoop.fs.s3a.S3AFileSystem')
        
        self.spark = SparkSession(self.sc)
        logger.debug(self.spark)

    ''' Read data from S3 '''
    def read_s3(self, s3_path):
        if s3_path.startswith('s3'):
            if s3_path == r'/*.CSV':
                s3_df = self.spark.read.csv(s3_path , header=True, inferSchema=True)
            elif s3_path == r'/*.JSON':
                s3_df = self.spark.read.json(s3_path)
            elif s3_path == r'/*.TXT':
                s3_df = self.spark.read.text(s3_path)

        elif s3_path.startswith('https') or s3_path.startswith('http'):
            if self.validate_url(s3_path):
                s3_df = self.api_data(s3_path)
        # s3_df.show(5)
        return s3_df

    ''' Upload dataframe to S3 '''
    def dataframe_to_s3(self, df, write_format, s3_path, mode, Header='true'):
        '''
         mode = 'overwrite'  # to update the entitled file with overwrite method
         write_format = 'csv'
         s3_path = 's3a://pysparkcsvs3/pysparks3/emp_csv/emp.csv'
        '''
        if mode.__eq__('overwrite'):
            bool_ack = self.confirm(s3_path)
        
        if df != None:
            if write_format.__eq__('csv'):
                df.write.format(write_format).option('header', Header).save(s3_path, mode = mode)
            elif write_format.__eq__('parquet') or write_format.__eq__('orc'):
                df.write.format(write_format).mode(mode).save(s3_path)
    
    ''' Validate API URL '''
    def confirm(self, path_name):
        ack = input(f'Are you sure to overwrite {path_name}? \nproceed with [y/n]...')
        if ack == 'Y' or ack == 'y':
            return True
        else: return False

    ''' Validate API URL '''
    def validate_url(self, url):
        logger.info(f'check {url} valid or invalid')
        response = requests.get(url)
        status_code = response.status_code
        if status_code == 200:
            return True
        else:
            return False

    ''' Read API Data '''
    def api_data(self, path):
        response = requests.get(path)
        try:
            jdata = response.text
            strdata = StringIO(jdata)
            dataframe = pd.read_csv(strdata, header= None)
    #         df = sprk.createDataFrame(dataframe)
            return dataframe
        except requests.exceptions.Timeout as timeout:
            logger.exception(timeout)
        except requests.exceptions.ConnectionError as connerror:
            logger.exception(connerror)
    
    ''' Simple Clean '''
    def remove_all_null_value(self, df):
        prepared_drop_list = []
        print('Total number of rows: ', df.shape[1])
        for i in range(0, df.shape[1]):
            if i == 0:
                pass
            else:
                ''' columns with fully null value '''
                if df[df.columns[i]].isnull().sum() == len(df):
                    prepared_drop_list.append(df.columns[i])
                # else:
                #     columns_.append(df.columns[i])
        print(prepared_drop_list)
        print('No. of features before removing missing value: ', len(df.columns), '\nProcess removing null value...')
        df = df.drop(prepared_drop_list, axis=1)
        print('...removing DONE!')
        print('No. of features: ', len(df.columns))
        print(df.head(10))
        return df
    
    def convert_sparkframe_to_pandasframe(self, q, sframe):
        # ".select(*)"
        return sframe.select(q).toPandas

# In[3]:

if __name__ == '__main__':
    source = '' # 's3a://pysparkcsvs3/pysparks3/emp_csv/emp.csv'
    target = ''
    main(source=source,target=target)