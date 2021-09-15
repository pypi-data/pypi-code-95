# -*- coding:utf-8 -*-
'''
A function sample for you to DIY
you can contact htts://www.smartchart.cn to get full package
'''
import os
import sys
import logging
import pymysql
import requests
import time
import json

pathname = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, pathname)
sys.path.insert(0, os.path.abspath(os.path.join(pathname, '..')))

ETL_FILE_PATH = '/home/airflow/etl_kettle/'
MAIL_LIST_API = 'https://www.smartchart.cn/api'
KETTLE_HOME = '/kettle/data-integration/'
AIRFLOW_URL = 'http://local:8080/'
DATASET_URL ='https://xxxx.com/echart/dataset_api/?token=xxx&visitor=Airflow&type='

def fun_email(sub, content, to_list=None, flag='plain'):  # 邮件标题，文本，收件人，邮件类型文本
    pass

def monitor_mail(sub,title,sql,head=None,to_list=None,flag='html'):
    pass

def oracle_mail(sub,title,sql,head=None,to_list=None,flag='html'):
    pass

class connect_db_execute():
    pass

def log_writer(statue, log_name='orphan', msg=''):
    """
    日志记录器，用于记录日志。
    :param statue: (str) 记录器状态，可选值为"init"和"record"
    :param log_name: (str) 日志的url，当status为"init"时传入
    :param msg: (str) 要记录的信息，当status不为"init"时传入
    :return: None
    """
    if statue == 'init':
        logging.basicConfig(level=logging.INFO,
                            format='[%(asctime)s] %(levelname)s {%(message)s}',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            filename='/home/airflow/airflow/logs/{}.log'.format(log_name),
                            filemode='a')
    elif statue == 'info':
        logging.info(msg)
    elif statue == 'error':
        logging.exception(msg)
    elif statue == 'warn':
        logging.warning(msg)


def log_writer_pro(which_logger=__name__, log_name='orphan'):
    """
    新版日志记录器，用于记录日志。
    :param which_logger: (str)记录器名。当脚本中只涉及一个记录器时，可以不填。
    :param log_name: (str)日志文件的名字
    :return: (obj)日志记录器对象
    """
    logger = logging.getLogger(which_logger)
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s {%(message)s}', '%Y-%m-%d %H:%M:%S')
    file_handler = logging.FileHandler('/home/airflow/airflow/logs/{}.log'.format(log_name))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)
    return logger


class Notktrfile_Error(Exception):
    """非ktr错误"""
    def __init__(self, err='不是后缀为ktr的文件'):
        Exception.__init__(self, err)

def readSqlFile(patch_str,para_dict=None):
    if patch_str.find('.sql') < 0:
        return 'file type error'
    with open(patch_str,'r',encoding='utf-8') as file_temp:
        sql_data = file_temp.read()
    sql_list = readSqlstr(sql_data,para_dict)
    return sql_list


def readSqlstr(sql_data,para_dict=None):
    import re
    sql_str = re.sub(r"(\/\*(.|\n)*?\*\/)|--.*",'',sql_data.strip())
    if para_dict:
        for k,v in para_dict.items():
            sql_str = sql_str.replace('$' + k,v)
    sql_list = sql_str.split(';')
    return sql_list


def run_sql_file(sql_file,db_connect='oracle',para_dict=None,dev=False):
    try:
        sql_list = readSqlFile(sql_file,para_dict)
        connect_db_execute(dev).execute_sql_list(sql_list,db_connect)
    except Exception as e:
        fun_email('{}执行出错'.format(sql_file.split('/')[-1]),str(e.args))
        raise e

def run_sql_str(sql_data,db_connect='oracle',para_dict=None,dev=False):
    try:
        sql_list = readSqlstr(sql_data,para_dict)
        connect_db_execute(dev).execute_sql_list(sql_list,db_connect)
    except Exception as e:
        fun_email('SQL执行出错',sql_data +str(e.args))
        raise e

def run_sp(sp_name,sp_para=None,dev=False):
    try:
        connect_db_execute(dev).excute_proc(sp_name,sp_para)
    except Exception as e:
        fun_email('{}执行出错'.format(sp_name),str(e.args))
        raise e

# 执行kettle job
def run_kettle(job,para_str='',dev=False):
    log_writer('init', log_name=job.split('/')[-1].split('.')[0])
    log_writer('info',msg='kettle job start')
    # The logging level (Basic, Detailed, Debug, Rowlevel, Error, Minimal, Nothing)
    if '.ktr' in job:
        job_str = f'{KETTLE_HOME}/pan.sh -level=Basic -file={job}{para_str}'
    else:
        job_str= f'{KETTLE_HOME}/kitchen.sh -level=Basic -file={job}{para_str}'
    print(job_str)
    out_put = os.popen(job_str)
    result_log = out_put.read()
    print(result_log)
    if result_log.find('ended successfully')>0 or result_log.find('result=[true]')>0:
        log_writer('info',msg='{} 完成数据抽取'.format(str(job)))
    else:
        log_writer('error',msg='{}  错误信息：{}'.format(job,str(result_log)))
        fun_email('{}执行出错'.format(job.split('/')[-1]),str(result_log))
        raise Exception('invalid kettle!')


def point_test(dagname, sleeptime='', maxtime=''):
    if sleeptime:
        sleeptime = int(sleeptime)
        sleeptime = sleeptime if sleeptime > 60 else 60
    if maxtime:
        maxtime = int(maxtime)
        maxtime = maxtime if maxtime < 60*60*2 else 60*60*2
    else:
        maxtime = 0
    conn = pymysql.connect(
                user=AIRFLOW_URL['user'],
                password=AIRFLOW_URL['password'],
                host=AIRFLOW_URL['host'],
                port=AIRFLOW_URL['port'],
                database=AIRFLOW_URL['db'],
                autocommit=True
    )
    try:
        cur = conn.cursor()
        sql = f"select start_date,state from dag_run where dag_id ='{dagname}' ORDER BY id desc LIMIT 1"
        while True:
            cur.execute(sql)
            status = cur.fetchall()
            if status[0][1] != 'success':
                if maxtime > 0 and status[0][1] != 'failed':
                    print('waiting...' + status[0][1])
                    time.sleep(sleeptime)
                    maxtime = maxtime - sleeptime
                else:
                    start_time = status[0][0].strftime("%Y-%m-%d %H:%M:%S")
                    response = '所依赖的dag:' + dagname + ',状态为' + status[0][1] + '.其最新的执行时间为' + start_time
                    fun_email(response,'前置DAG任务未成功')
                    print(response)
                    raise Exception(response)
            else:
                print('success...')
                break
    except Exception as e:
        raise e
    finally:
        conn.close()

def validate(sql_file,db_connect='oracle',para_dict=None,dev=False):
    try:
        sql_list = readSqlFile(sql_file,para_dict)
        result = connect_db_execute(dev).execute_sql_list(sql_list,db_connect)
        if result:
            raise Exception('校验出错:'+ str(result))
    except Exception as e:
        fun_email('{}执行校验出错'.format(sql_file.split('/')[-1]),str(e.args))
        raise e

def dataset(jobname,para_str,remark,tolist=None):
    '''

    :param jobname:
    :param remark: info-仅打印结果, e1-有值报错, e2-有值邮件通知, e3/每15分钟重试最多2小时,无值报错,默认无值报错
    :param para_str:
    :return:
    '''
    sleeptime = 60*15
    maxtime = 3600*2
    try:
        while True:
            result=requests.get(DATASET_URL+para_str,verify=False)
            result=result.json()
            status = result['result']
            result=result['data']
            if status=='error':
                raise Exception(f'{result}')
            result_str=',\n'.join([str(item) for item in result])
            print(f'Dataset: {result_str} ')
            if remark == 'e3':
                if len(result)<2:
                    if maxtime <= 0:
                        raise Exception('超时且数据为空')
                    else:
                        time.sleep(sleeptime)
                        maxtime = maxtime - sleeptime
                else:
                    break
            else:
                if len(result)>1:
                    if remark=='e1':
                        raise Exception('有异常数据')
                    elif remark=='e2':
                        fun_email(f'{jobname}-Dataset Status',result_str,to_list=tolist)
                else:
                    if remark != 'info':
                        result_str='数据为空'
                        raise Exception(result_str)
                break
    except Exception as e:
        fun_email(f'{jobname}-执行Dataset校验出错',result_str,to_list=tolist)
        raise e

if __name__ == '__main__':
    pass

