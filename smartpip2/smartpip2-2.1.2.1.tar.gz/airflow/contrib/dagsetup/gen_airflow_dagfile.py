# -*- coding:utf-8 -*-
# author: John Yan  last update on 2020-06-29
# function: generate the airflow etl_script and dag file

from airflow.contrib.dagsetup.config_dagfile import *
from airflow.settings import AIRFLOW_HOME, ETL_FILE_PATH
import re
import os
import logging


def gen_airflow_dag(*args, **kwargs):
    """
    generate the airflow etl_script and dag file
    :param owner: 负责人
    :param project_name: 项目名,将用于DAG的唯一标识
    :param schedule_interval: cron 模式 * * * * * *
    :param schedule_rate: 每天/每周/每月
    :param job_list: 可以是数组[[]] 或 string
    :param dag_remark: 备注信息
    :param dag_sequence: airflow 格式的执行顺序,可以为空
    :return: None
    #sp|sp_name|oracle|para2_name,para3_name||
    """
    owner = kwargs['owner']
    project_name = kwargs['project_name']
    description = kwargs.get('description', '')
    schedule_interval = kwargs['schedule_interval']
    schedule_rate = kwargs['schedule_rate']
    job_list = kwargs['job_list']
    dag_remark = kwargs.get('dag_remark', '')
    dag_sequence = kwargs.get('dag_sequence', '')
    retries = kwargs.get('retries', 0)
    mail = kwargs.get('mail', '')
    tags = kwargs.get('tags')
    tags = tags.split(',') if tags else []
    extra_args = ''
    if mail:
        extra_args = f''''email': '{mail}',
    'email_on_failure': True,
    'email_on_retry': True,'''

    DRIVES = {
        'sql_file': {'color': '#b46ade'},
        'sql_str': {'color': '#b0f07c'},
        'sp': {'color': '#cdaaed'},
        'ktr': {'color': '#f9c915'},
        'kjb': {'color': '#e9ffdb'},
        'ktr_r': {'color': '#f4a460'},
        'kjb_r': {'color': '#f4a460'},
        'py': {'color': '#ffefeb'},
        'link': {'color': '#70586d'},
        'validate': {'color': '#f0e4ec'},
        'dataset': {'color': '#f9c915'},
        'refresh_tableau': {'color': '#f4a460'},
        'impala_sql': {'color': '#835bf0'},
        'hive_sql': {'color': '#9486ba'},
        'gp_sql': {'color': '#cecadb'},
        'mysql_sql': {'color': '#74946e'},
        'sqoop': {'color': '#665908'},
        'sap': {'color': '#f4a460'},
        'trigger': {'color': '#9cbaba'},
        'branch': {'color': '#3d7373'},
        'diy': {'color': '#c46c6c'},
        'hdfs': {'color': '#4675bf'},
    }
    # -----------------transfer job str to job list---------------------
    user_define = ''
    if isinstance(job_list, str):
        items = job_list.split('#')
        # 第一行预留给写自定义参数或代码
        user_define = items[0].strip()
        job_list = []
        # 过滤每一个
        for item in items[1:]:
            item = item.strip().split('--')[0]
            if item:
                item_lst = item.split('|')
                if len(item_lst) < 2:
                    item_lst = re.split('\s+', item)
                item_lst = list(map(lambda x: x.strip(), item_lst))
                color = DRIVES.get(item_lst[0].lower())
                if not color:
                    # 将非合法的driver当成备注
                    user_define = user_define + '\n#--' + item
                    continue
                item_lst.extend([''] * (7 - len(item_lst)))
                item_lst[-2] = item_lst[0]
                item_lst[-1] = color.get('color')
                job_list.append(item_lst)
    # 扩展job_list
    for i in range(len(job_list)):
        if job_list[i][0].endswith('_sql'):
            job_list[i][4] = job_list[i][0].replace('_sql', '')
            job_list[i][0] = 'sql_file'
    print(job_list)

    # -------------------gen job file-----------------------
    dag_str = ''
    etl_str = import_format
    # extract the parameter list and construct the get variable of airflow
    # 如果用户有定义, 不采用默认取参方式
    if user_define:
        etl_str = etl_str + user_define
    # 自动不好, 取消
    # else:
    #     param_str = ''
    #     for item in job_list:
    #         param_str = param_str + ','+ item[2]
    #     param_list = set(param_str.split(','))
    #     for item in param_list:
    #         if item:
    #             etl_str = etl_str + param_format.format(param=item)

    # loop to construct jobs
    for item in job_list:
        param_str = ''
        item_param_list = item[2].split(',')
        for item_param in item_param_list:
            if item_param:
                param_str = param_str + '+' + param_str_format.format(item_param=item_param)
        if param_str:
            param_str = param_str[1:]
        else:
            param_str = "''"

        driver = item[0].lower()
        # 文件类型0,文件命名1,参数2,备注3,执行数据库4
        # driver 0, filename 1, param 2, remark 3,db 4
        if driver == 'sql_file':
            etl_str = etl_str + execute_sql_format.format(project_name=project_name, filename=item[1], db=item[4],
                                                          param=item[2])
        elif driver == 'sqoop':
            etl_str = etl_str + execute_sqoop_format.format(project_name=project_name, filename=item[1], param=item[2])
        elif driver == 'sap':
            etl_str = etl_str + execute_sap_format.format(project_name=project_name, filename=item[1], param=item[2])
        elif driver == 'validate':
            etl_str = etl_str + execute_validate_format.format(project_name=project_name, filename=item[1], db=item[4],
                                                               param=item[2])
        elif driver == 'sql_str':
            etl_str = etl_str + execute_sqlstr_format.format(filename=item[1], remark=item[3], db=item[4],
                                                             param=item[2])
        elif driver == 'sp':
            etl_str = etl_str + execute_sp_format.format(filename=item[1], param=item[2])
        elif driver == 'ktr':
            etl_str = etl_str + execute_ktr_format.format(project_name=project_name, filename=item[1],
                                                          param_str=param_str)
        elif driver == 'hdfs':
            etl_str = etl_str + execute_hdfs_format.format(project_name=project_name, filename=item[1],
                                                           param_str=param_str)
        elif driver == 'kjb':
            etl_str = etl_str + execute_kjb_format.format(project_name=project_name, filename=item[1],
                                                          param_str=param_str)
        elif driver == 'ktr_r':
            etl_str = etl_str + execute_ktr_r_format.format(project_name=project_name, filename=item[1],
                                                            param_str=param_str)
        elif driver == 'kjb_r':
            etl_str = etl_str + execute_kjb_r_format.format(project_name=project_name, filename=item[1],
                                                            param_str=param_str)
        elif driver == 'py':
            if not item[2] or ' ' in item[2]:
                item[2] = f"'{item[2]}'"
            etl_str = etl_str + execute_python_format.format(project_name=project_name, filename=item[1], param=item[2])
        elif driver == 'link':
            etl_str = etl_str + execute_point_format.format(dagname=item[1], sleeptime=item[2], maxtime=item[3])
        elif driver == 'refresh_tableau':
            etl_str = etl_str + refresh_tableau_format.format(filename=item[1], sourceID=item[2])
        elif driver == 'dataset':
            if '@' in item[4]: item[4] = f'"{item[4]}"'
            etl_str = etl_str + execute_dataset_format.format(filename=item[1], param=item[2], remark=item[3],
                                                              tolist=item[4])
        elif driver == 'trigger':
            etl_str = f"{etl_str}\nS_{item[1]}='{item[2]}'\n"
        dag_str = dag_str + item[1] + ' >> '
    # save the script py
    o_fileanme = AIRFLOW_HOME + '/etl_script/' + project_name + '.py'
    with open(o_fileanme, 'w', encoding='utf-8') as fo:
        fo.write(etl_str)

    # ----------------------gen dag file----------------------------------
    days_ago = 1
    if schedule_rate == 'daily':
        days_ago = 1
    elif schedule_rate == 'weekly':
        days_ago = 13
    elif schedule_rate == 'monthly':
        days_ago = 59

    etl_str = dag_import_format.format(project_name=project_name)
    etl_str = etl_str + dag_config_format.format(owner=owner, days_ago=days_ago, retries=retries, tags=tags,
                                                 project_name=project_name, extra_args=extra_args,
                                                 schedule_interval=schedule_interval, dag_remark=dag_remark,
                                                 description=description)
    # construct the dag list
    for item in job_list:
        driver = item[0].lower()
        if driver == 'trigger':
            etl_str = etl_str + dag_jobs_format_trigger.format(filename=item[1], color=item[-1], driver=item[-2])
        elif driver == 'branch':
            etl_str = etl_str + dag_jobs_format_branch.format(filename=item[1], color=item[-1], driver=item[-2])
        else:
            etl_str = etl_str + dag_jobs_format.format(filename=item[1], color=item[-1], driver=item[-2])
        if driver == 'hdfs':
            etl_str = etl_str + dag_jobs_format_queue.format(filename=item[1])
    # dag sequence
    if dag_sequence.strip():
        etl_str += dag_sequence
    else:
        etl_str += dag_str[:-4]

    # save the dag py
    o_fileanme = AIRFLOW_HOME + '/dags/dag_' + project_name + '.py'
    with open(o_fileanme, 'w', encoding='utf-8') as fo:
        fo.write(etl_str)


def rm_airflow_dag(project_name):
    try:
        o_fileanme = AIRFLOW_HOME + '/dags/dag_' + project_name + '.py'
        if os.path.exists(o_fileanme):
            os.remove(o_fileanme)

        o_fileanme = AIRFLOW_HOME + '/etl_script/' + project_name + '.py'
        if os.path.exists(o_fileanme):
            os.remove(o_fileanme)

    except Exception as e:
        logging.info(o_fileanme + 'is required to delete, but not found, may be it is not active yet')


def gen_airflow_config(project_name):
    import time
    job_str = ''
    dag_str = ''
    file_list = os.listdir(os.path.join(ETL_FILE_PATH, project_name))
    if file_list:
        file_list.sort()
        print(file_list)
    for num, file in enumerate(file_list):
        modified_date = time.strftime("%Y-%m-%d %H:%M",
                                      time.localtime(os.path.getmtime(os.path.join(ETL_FILE_PATH, project_name, file))))
        file = file.split('.')
        if len(file) != 2:
            continue
        if file[1] == 'ktr':
            job_str = job_str + '#ktr        ' + file[0] + '              --' + modified_date + '\n'
            dag_str = dag_str + file[0] + ' >> '
        elif file[1] == 'kjb':
            job_str = job_str + '#kjb        ' + file[0] + '              --' + modified_date + '\n'
            dag_str = dag_str + file[0] + ' >> '
        elif file[1] == 'sql':
            job_str = job_str + '#impala_sql  ' + file[0] + '              --' + modified_date + '\n'
            dag_str = dag_str + file[0] + ' >> '
        elif file[1] == 'py':
            job_str = job_str + '#py         ' + file[0] + '              --' + modified_date + '\n'
            dag_str = dag_str + file[0] + ' >> '
        if (num + 1) % 3 == 0:
            dag_str = dag_str + '\n'
    return job_str + '\n\n///////////////\n\n' + dag_str


if __name__ == '__main__':
    owner = 'john'
    schedule_interval = '10 08 * * *'
    # schedule_interval = '@once'
    schedule_rate = 'day'  # 每周,每月
    project_name = 'P2'  # which is used as id and file name
    # the job will execute in dag by sequence as listed, first item is to use what driver to execute
    # 数据库及文件类型,文件命名,参数
    job_list = '''
    #hive_sql predict para1,para2
    #impala_sql center
    #hive_sql huli
    #impala_sql test1
    #ktr test para3
    #/diy diy1
    #trigger trigger2  targetdag2
    #/branch  branch1
    #hdfs abcc
    '''
    dag_sequence = '''
center >> test1 >> trigger2
test
    '''
    retries = 5
    dag_remark = 'finance'
    kwargs = {
        'owner': owner,
        'project_name': project_name,
        'schedule_interval': schedule_interval,
        'schedule_rate': schedule_rate,
        'job_list': job_list,
        'tags': 'test1,test2',
        'dag_sequence': dag_sequence,
        'dag_remark': '##dag_remark',
        'description': 'description'
    }
    # gen_airflow_dag(**kwargs)
    import requests
    import json
    # url = 'http://0.0.0.0:8080/api/experimental/create_dagfile?token=jzbuxdr!wkh1_dhknzxhpo1t7no_bw*ar!t$pb5wqncrr4_k3y'
    # response = requests.post(url,data=json.dumps(kwargs),headers={'Content-Type': 'application/json'})

    import base64

    url = 'http://0.0.0.0:8080/api/v1/create_dagfile'
    # url = 'http://10.10.1.184:8080/api/v1/create_dagfile'
    name = 'admin'
    pwd = 'admin'
    auth = str(base64.b64encode(f'{name}:{pwd}'.encode('utf-8')), 'utf-8')
    header = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {auth}'
    }
    response = requests.post(url, data=json.dumps(kwargs), headers=header)
    print(response.text)
