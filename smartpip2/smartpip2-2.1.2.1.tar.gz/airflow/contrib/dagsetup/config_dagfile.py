# -*- coding:utf-8 -*-
import_format = '''# -*- coding:utf-8 -*-
import os
import sys
import datetime
pathname = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, pathname)
sys.path.insert(0, os.path.abspath(os.path.join(pathname, '..')))

from common.functions import *
from airflow.models import Variable
dev=''
retry_delay_minutes = 5
'''

param_format = '''
# get your param from airflow web
{param} = Variable.get('{param}')
'''
# 0 -airflow_break_point-
break_point = '''
#airflow_break_point
def S_break_point():
    return 'success'
'''
# 0 - project_name 1 - file name
execute_python_format = '''
def S_{filename}():
    job = ETL_FILE_PATH + '{project_name}/{filename}.py'
    result=os.system('python %s %s'%(job,{param}))
    if result !=0:
        fun_email(f'{project_name}/{filename}出错', 'python error')
        raise Exception('error')
'''
# 0 - project_name, 1 - kettle tranform name, 2 - para string
execute_ktr_format = '''
# execute kettle transform
def S_{filename}():
    job=ETL_FILE_PATH + '{project_name}/{filename}.ktr'
    run_kettle(job,{param_str},dev=dev)
'''

# 0 - project_name, 1 - kettle job name, 2 - para string
execute_kjb_format = '''
# execute kettle job
def S_{filename}():
    job=ETL_FILE_PATH + '{project_name}/{filename}.kjb'
    run_kettle(job,{param_str},dev=dev)
'''

# 0 - project_name, 1 - kettle tranform name, 2 - para string
execute_ktr_r_format = '''
# execute kettle transform
def S_{filename}():
    job=ETL_FILE_PATH_R + '{project_name}/{filename}.ktr'
    run_kettle_remote(job,{param_str},dev=dev)
'''

# 0 - project_name, 1 - kettle job name, 2 - para string
execute_kjb_r_format = '''
# execute kettle job
def S_{filename}():
    job=ETL_FILE_PATH_R + '{project_name}/{filename}.kjb'
    run_kettle_remote(job,{param_str},dev=dev)
'''

execute_hdfs_format = '''
# execute kettle with hdfs job
def S_{filename}():
    job=ETL_FILE_PATH + '{project_name}/{filename}.ktr'
    run_kettle(job,{param_str},dev=dev)
    load_hive(job)
'''

# 0 - project_name, 1 - sql script name,
execute_sql_format = '''
# execute db sql script
def S_{filename}():
    path = ETL_FILE_PATH + '{project_name}/{filename}.sql'
    para_dict = dict(zip('{param}'.split(','),[{param}]))
    run_sql_file(path,'{db}',para_dict,dev=dev)
'''
# remark = sql string
execute_sqlstr_format = '''
# execute db sql script
def S_{filename}():
    para_dict = dict(zip('{param}'.split(','),[{param}]))
    run_sql_str({remark},'{db}',para_dict,dev=dev)
'''

# 0 - sp name, 1 - para string
execute_sp_format = '''
# execute db procedure
def S_{filename}():
    run_sp('{filename}',[{param}],dev=dev)
'''

execute_sqoop_format = '''
# execute sqoop script
def S_{filename}():
    path = ETL_FILE_PATH + '{project_name}/{filename}.sql'
    para_dict = dict(zip('{param}'.split(','),[{param}]))
    run_sqoop(path, para_dict)
'''

execute_sap_format = '''
# execute sap rfc script
def S_{filename}():
    path = ETL_FILE_PATH + '{project_name}/{filename}.json'
    run_rfc(path, {param})
'''

param_str_format = ''' ' "-param:{item_param}={{}}"'.format({item_param}) '''

dag_import_format = '''# -*- coding:utf-8 -*-
import os
import sys
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from airflow import DAG
import airflow
pathname = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, pathname)
sys.path.insert(0, os.path.abspath(os.path.join(pathname, '..')))

# import your jobs from etl_script
from etl_script.{project_name} import *
'''

dag_config_format = '''
# dag config
args = {{
    'owner': '{owner}',
    'start_date': airflow.utils.dates.days_ago({days_ago}),
    'retries': {retries},
    'retry_delay_minutes': retry_delay_minutes,
    {extra_args}
}}
dag = DAG(
    dag_id='{project_name}',
    tags={tags},
    default_args=args,
    schedule_interval='{schedule_interval}',
    catchup=False,
    description = """{description}"""
)
dag.doc_md = """{dag_remark}"""
'''

dag_jobs_format = '''
{filename} = PythonOperator(
    task_id='{filename}',
    python_callable=S_{filename},
    dag=dag
)
{filename}.ui_color = '{color}'
{filename}.driver = '{driver}'
'''

dag_jobs_format_branch = '''
{filename} = BranchPythonOperator(
    task_id='{filename}',
    python_callable=S_{filename},
    dag=dag
)
{filename}.ui_color = '{color}'
{filename}.driver = '{driver}'
'''

dag_jobs_format_trigger = '''
{filename} = TriggerDagRunOperator(
    task_id='{filename}',
    trigger_dag_id=S_{filename},
    dag=dag
)
{filename}.ui_color = '{color}'
{filename}.driver = '{driver}'
'''

dag_jobs_format_queue = '''
{filename}.queue = 'bg'
'''

# breaking_point
execute_point_format = '''
# decide Continue or terminate
def S_{dagname}():
    point_test('{dagname}','{sleeptime}','{maxtime}')
'''

# check data
execute_validate_format = '''
# execute validate script
def S_{filename}():
    path = ETL_FILE_PATH + '{project_name}/{filename}.sql'
    para_dict = dict(zip('{param}'.split(','),[{param}]))
    validate(path,'{db}',para_dict,dev=dev)
'''

# check dataset
execute_dataset_format = '''
# execute dataset script
def S_{filename}():
    dataset('{filename}','{param}','{remark}',{tolist})
'''

refresh_tableau_format = '''
# refresh tableau source script
def S_{filename}():
    refreshTableauSource({sourceID})
'''
