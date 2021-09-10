"""
@author  : MG
@Time    : 2021/7/12 9:10
@File    : backup.py
@contact : mmmaaaggg@163.com
@desc    : 用于对数据库表进行备份。
"""
import configparser
import logging
import multiprocessing
import os
import zipfile
from multiprocessing import Pool, Manager, Queue
from typing import Dict, List
import datetime
from tqdm import tqdm
from ibats_utils.transfer import date_2_str
from vnpy.trader.setting import get_settings

# get_settings
from vnpy_extra.backtest import CleanupOrcaServerProcessIntermittent


def backup_tables_2_zips(schema_table_names_dic: Dict[str, List[str]],
                         sql_output_cache_folder: str = "output",
                         zip_output_folder: str = "output",
                         mysqldump_file_path=r"c:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe",
                         mysqldump_user_name: str = None, mysqldump_password: str = None,
                         mysqldump_host: str = None, mysqldump_port: str = None,
                         ):
    """
    通过mysqldump对表进行逐表备份，输出到指定目录 sql_output_cache_folder
    zip最高压缩率算法压缩后，删除源文件。输出zip文件到指定目录 zip_output_folder/[schema]_[yyyy-dd-mm]/table_name.zip
    :param schema_table_names_dic: 数据库Schema：[table_name1, table_name2, ...] 字典
    :param sql_output_cache_folder: sql缓存目录
    :param zip_output_folder: zip输出的根目录
    :param mysqldump_file_path: 如果为空则默认使用系统命令。如果不为空则使用指定文件运行
    :param mysqldump_user_name: mysqldump 用户名
    :param mysqldump_password: mysqldump 密码
    :param mysqldump_host: mysqldump host
    :param mysqldump_port: mysqldump port
    :return:
    """
    logging.info("备份开始。")
    # logger = logging.getLogger(__name__)
    # TODO: logic
    # 动态生成 .mysql.cnf 文件内容，程序运行结束，删除该文件：
    # [mysqldump]
    # user="***"
    # password ="***"
    # host = 192.168.1.57
    # port = 3306
    # mysqldump 命令用法
    # "c:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe" --defaults-file='.mysql.cnf' vnpy dbbardata > dump_dbbardata_9999.sql

    # 生成配置文件，最后删除
    cfg = configparser.ConfigParser()
    cfg.add_section('mysqldump')
    if mysqldump_user_name is None or mysqldump_password is None or mysqldump_host is None or mysqldump_port is None:
        database_dic = get_settings('database')
        cfg.set('mysqldump', 'user', database_dic['.user'])
        cfg.set('mysqldump', 'password', database_dic['.password'])
        cfg.set('mysqldump', 'host', database_dic['.host'])
        cfg.set('mysqldump', 'port', str(database_dic['.port']))
    else:
        cfg.set('mysqldump', 'user', mysqldump_user_name)
        cfg.set('mysqldump', 'password', mysqldump_password)
        cfg.set('mysqldump', 'host', mysqldump_host)
        cfg.set('mysqldump', 'port', mysqldump_port)
    cfg.write(open('.mysql.cnf', 'w'))

    # 设置环境变量
    os.environ['WORK_HOME'] = mysqldump_file_path

    # dump
    today_str = date_2_str(datetime.date.today())
    logging.info(f"有 {len(schema_table_names_dic)} schema 将被备份")
    for schema, table_name_list in schema_table_names_dic.items():
        # 配置路径，创建缓存目录
        cache_folder_path = os.path.join(sql_output_cache_folder, schema)
        os.makedirs(cache_folder_path, exist_ok=True)
        total = len(table_name_list)
        logging.info(f"{schema} 有 {total} 个表将被备份")
        for table_name in tqdm(table_name_list, total=total, desc=schema):
            # 缓存文件名称
            sql_output_cache_file = os.path.join(cache_folder_path, f'dump_{schema}_{table_name}.sql')
            # 直接用{mysqldump_file_path}会乱码，可能是因为路径中有空格，要添加环境变量，直接用mysqldump
            # os.system(f'{os.environ.get("WORKON_HOME")} --defaults-file=".mysql.cnf" control_center role > dump_role_9999.sql')
            # os.system(f'mysqldump --defaults-file=".mysql.cnf" control_center role > dump_role_9999.sql')
            cmd_code = os.system(
                f'mysqldump --defaults-file=".mysql.cnf" {schema} {table_name} > {sql_output_cache_file}')
            if cmd_code != 0:
                logging.error(f'{schema} 中的 {table_name} 表dump失败！')

    # 删除环境变量和配置文件
    del os.environ['WORK_HOME']
    os.unlink(".mysql.cnf")
    logging.info("备份结束，压缩开始。")
    # zip
    total_count = 0
    success_count = 0
    fail_count = 0
    zip_file_path_list = []
    for schema in schema_table_names_dic.keys():
        # cache folder path
        cache_folder_path = os.path.join(sql_output_cache_folder, schema)
        sql_cache_files_list = os.listdir(cache_folder_path)
        total_files = len(sql_cache_files_list)
        # zip folder path
        zip_folder_path = os.path.join(zip_output_folder, f"{schema}_{today_str}")
        os.makedirs(zip_folder_path, exist_ok=True)
        for num, sql_cache_file in enumerate(sql_cache_files_list, start=1):
            filename, file_type = os.path.splitext(sql_cache_file)

            if file_type == '.sql':
                sql_cache_file_path = os.path.join(cache_folder_path, sql_cache_file)
                zip_file_path = os.path.join(zip_folder_path, filename + '.zip')
                try:
                    logging.info(f'正在压缩...{zip_file_path}')
                    with zipfile.ZipFile(zip_file_path, 'w', compression=zipfile.ZIP_LZMA, compresslevel=9) as zipped:
                        zipped.write(sql_cache_file_path)
                    total_count += 1
                    success_count += 1
                    logging.info(f'{num}/{total_files}) {zip_file_path} 完成了压缩，共成功 {success_count} 个')
                    os.unlink(sql_cache_file_path)
                    zip_file_path_list.append(zip_file_path)
                except Exception as e:
                    fail_count += 1
                    logging.error(f'{zip_file_path} 压缩失败！失败 {fail_count} 个。异常：{e}')

    zip_dir_files = '\n'.join(zip_file_path_list)
    logging.info(f"压缩结束。成功 {success_count} 个，失败 {fail_count} 个。zip目录列表：\n{zip_dir_files}")


def run_backup_tables_2_zips():
    schema_table_names_dic = {
        'vnpy': [
            "account_strategy_mapping",
            "dbbardata",
            "order_data_model",
            "position_daily_model",
            "position_status_model",
            "strategy_backtest_stats",
            "strategy_backtest_stats_archive",
            "strategy_info",
            "strategy_status",
            "symbols_info",
            "trade_data_model",
            "trade_date_model",
            "user_account_mapping",
            "wind_future_adj_factor",
        ],
    }
    backup_tables_2_zips(
        schema_table_names_dic,
        r'd:\temp\mysql_backup_cache',
        r'f:\mysql_backup')


def prepare_conf(mysqldump_file_path=r"c:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe",
                 mysqldump_user_name: str = None, mysqldump_password: str = None,
                 mysqldump_host: str = None, mysqldump_port: str = None, ):
    """
    :param mysqldump_file_path: 如果为空则默认使用系统命令。如果不为空则使用指定文件运行
    :param mysqldump_user_name: mysqldump 用户名
    :param mysqldump_password: mysqldump 密码
    :param mysqldump_host: mysqldump host
    :param mysqldump_port: mysqldump port"""

    logging.info("生成配置文件。")
    # logger = logging.getLogger(__name__)
    # 动态生成 .mysql.cnf 文件内容，程序运行结束，删除该文件：
    # [mysqldump]
    # user="***"
    # password ="***"
    # host = 192.168.1.57
    # port = 3306
    # mysqldump 命令用法
    # "c:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe" --defaults-file='.mysql.cnf' vnpy dbbardata > dump_dbbardata_9999.sql

    # 生成配置文件，最后删除
    cfg = configparser.ConfigParser()
    cfg.add_section('mysqldump')
    if mysqldump_user_name is None or mysqldump_password is None or mysqldump_host is None or mysqldump_port is None:
        database_dic = get_settings('database')
        cfg.set('mysqldump', 'user', database_dic['.user'])
        cfg.set('mysqldump', 'password', database_dic['.password'])
        cfg.set('mysqldump', 'host', database_dic['.host'])
        cfg.set('mysqldump', 'port', str(database_dic['.port']))
    else:
        cfg.set('mysqldump', 'user', mysqldump_user_name)
        cfg.set('mysqldump', 'password', mysqldump_password)
        cfg.set('mysqldump', 'host', mysqldump_host)
        cfg.set('mysqldump', 'port', mysqldump_port)
    cfg.write(open('.mysql.cnf', 'w'))

    # 设置环境变量
    os.environ['WORK_HOME'] = mysqldump_file_path


def delete_conf():
    """删除环境变量和配置文件"""
    del os.environ['WORK_HOME']
    os.unlink(".mysql.cnf")
    logging.info('删除配置文件')


def process_mysqldump_file(cache_filename_queue: Queue,
                           schema_table_names_dic: Dict[str, List[str]],
                           sql_output_cache_folder: str = "output",
                           customer_num: int = 3):
    """
    通过Queue获取dump的sql文件路径，zip最高压缩率算法压缩后，删除源文件。
    输出zip文件到指定目录 zip_output_folder/[schema]_[yyyy-dd-mm]/table_name.zip
    :param cache_filename_queue: Queue
    :param schema_table_names_dic: 数据库Schema：[table_name1, table_name2, ...] 字典
    :param sql_output_cache_folder: sql缓存目录
    :param customer_num: sql缓存目录
    """
    # dump
    logging.info("备份开始。")
    logging.info(f"有 {len(schema_table_names_dic)} schema 将被备份")
    for schema, table_name_list in schema_table_names_dic.items():
        # 配置路径，创建缓存目录
        cache_folder_path = os.path.join(sql_output_cache_folder, schema)
        os.makedirs(cache_folder_path, exist_ok=True)
        total = len(table_name_list)
        logging.info(f"{schema} 有 {total} 个表将被备份")
        for table_name in tqdm(table_name_list, total=total, desc=schema):
            sql_output_cache_file = os.path.join(cache_folder_path, f'dump_{schema}_{table_name}.sql')
            # 直接用{mysqldump_file_path}会乱码，可能是因为路径中有空格，要添加环境变量，直接用mysqldump
            # os.system(f'{os.environ.get("WORKON_HOME")} --defaults-file=".mysql.cnf" control_center role > dump_role_9999.sql')
            # os.system(f'mysqldump --defaults-file=".mysql.cnf" control_center role > dump_role_9999.sql')
            cmd_code = os.system(
                f'mysqldump --defaults-file=".mysql.cnf" {schema} {table_name} > {sql_output_cache_file}')
            if cmd_code == 0:
                cache_filename_queue.put((schema, sql_output_cache_file))
                logging.info(f'{schema} 中的 {table_name} 表dump成功，发送给queue，路径为\n{sql_output_cache_file}')
            else:
                logging.error(f'{schema} 中的 {table_name} 表dump失败！')
    # 循环完所有的要备份的表后，想zip函数发送停止信号，根据消费者数量发送
    for i in range(customer_num):
        cache_filename_queue.put(('flag', False))


def zip_mysqldump_file(cache_filename_queue: Queue,
                       zip_output_folder: str = "output"):
    """
    通过Queue获取dump的sql文件路径，zip最高压缩率算法压缩后，删除源文件。
    输出zip文件到指定目录 zip_output_folder/[schema]_[yyyy-dd-mm]/table_name.zip
    :param cache_filename_queue: Queue
    :param zip_output_folder: zip输出的根目录
    :return:
    """

    # logging.info("备份结束，压缩开始。")
    flag = True
    while flag:
        # zip

        today_str = date_2_str(datetime.date.today())
        schema, sql_cache_file_path = cache_filename_queue.get()
        # 如果dump完毕将接到停止指令
        if schema == 'flag':
            flag = sql_cache_file_path
            return

        sql_file_path, file_type = os.path.splitext(sql_cache_file_path)
        filename = sql_file_path.split('\\')[-1]

        # zip folder path
        zip_folder_path = os.path.join(zip_output_folder, f"{schema}_{today_str}")
        os.makedirs(zip_folder_path, exist_ok=True)

        if file_type == '.sql':
            zip_file_path = os.path.join(zip_folder_path, filename + '.zip')
            try:
                logging.info(f'正在压缩...{zip_file_path}')
                with zipfile.ZipFile(zip_file_path, 'w', compression=zipfile.ZIP_LZMA, compresslevel=9) as zipped:
                    zipped.write(sql_cache_file_path)
                logging.info(f'{zip_file_path} 完成了压缩')
                os.unlink(sql_cache_file_path)
            except Exception as e:
                logging.error(f'{zip_file_path} 压缩失败！异常：{e}')

        cache_filename_queue.task_done()


def run_multiprocess_zip(multi_process_num: int = -1,
                         sql_output_cache_folder=r'd:\temp\mysql_backup_cache',
                         zip_output_folder=r'f:\mysql_backup',
                         mysqldump_file_path=r"c:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe",
                         mysqldump_user_name: str = None, mysqldump_password: str = None,
                         mysqldump_host: str = None, mysqldump_port: str = None,
                         ):
    """
    :param multi_process_num: 进程数
    :param sql_output_cache_folder: sql缓存目录
    :param zip_output_folder: zip输出的根目录
    :param mysqldump_file_path: 如果为空则默认使用系统命令。如果不为空则使用指定文件运行
    :param mysqldump_user_name: mysqldump 用户名
    :param mysqldump_password: mysqldump 密码
    :param mysqldump_host: mysqldump host
    :param mysqldump_port: mysqldump port
    :return:
    """
    schema_table_names_dic = {
        'vnpy': [
            "account_strategy_mapping",
            "dbbardata",
            "order_data_model",
            "position_daily_model",
            "position_status_model",
            "strategy_backtest_stats",
            "strategy_backtest_stats_archive",
            "strategy_info",
            "strategy_status",
            "symbols_info",
            "trade_data_model",
            "trade_date_model",
            "user_account_mapping",
            "wind_future_adj_factor",
        ],
    }
    # 生成配置文件
    prepare_conf(mysqldump_file_path=mysqldump_file_path,
                 mysqldump_user_name=mysqldump_user_name, mysqldump_password=mysqldump_password,
                 mysqldump_host=mysqldump_host, mysqldump_port=mysqldump_port, )

    if multi_process_num == -1:
        # 默认CPU数量
        multi_process_num = multiprocessing.cpu_count()
    customer_num = multi_process_num - 1

    pool = Pool(processes=multi_process_num)
    manager = Manager()
    cache_filename_queue = manager.Queue(multi_process_num * 2)

    # 建立子进程实例
    def print_error(value):
        logging.info("%s 启动 error: %s" % (name, value))

    # 执行dump的进程
    logging.info("启动子进程 dump_process")
    pool.apply_async(
        process_mysqldump_file,
        args=(cache_filename_queue,
              schema_table_names_dic,
              sql_output_cache_folder,
              customer_num),
        error_callback=print_error
    )

    # 执行zip的进程
    for _ in range(customer_num):
        name = f"zip_process_{_}"
        logging.info("启动子进程 %s" % name)

        pool.apply_async(
            zip_mysqldump_file,
            args=(cache_filename_queue,
                  zip_output_folder),
            error_callback=print_error
        )

    logging.info("等待清空任务队列")
    cache_filename_queue.join()
    logging.info("等待所有进程结束")
    pool.close()
    logging.info("关闭进程池（pool）不再接受新的任务")
    pool.join()
    logging.info("进程池（pool）所有任务结束")
    # 删除配置文件
    delete_conf()


if __name__ == "__main__":
    # run_backup_tables_2_zips()
    run_multiprocess_zip(multi_process_num=-1,
                         sql_output_cache_folder=r'd:\temp\mysql_backup_cache',
                         zip_output_folder=r'f:\mysql_backup',)
