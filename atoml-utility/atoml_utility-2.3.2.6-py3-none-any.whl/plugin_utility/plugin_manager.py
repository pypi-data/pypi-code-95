
import os
import sys
import argparse
import json

from .plugin_object import Plugin_Object, get_timer_from_json, default_params

from general_utility import utils as us
from general_utility.appbase import ab

#########################################################
# 插件框架相关

def load_plugin_runner(config):
    from plugin_utility.plugin_object import Plugin_Runner, default_params
    return Plugin_Runner(config, local_params = default_params)

#######################################################################################
# 核心功能函数

# 加载插件
def load_plugin(file_path):
    from imp import acquire_lock, release_lock, load_module, PY_SOURCE
    from .iplugin import iPlugin

    plugin = None
    try:        
        with open(file_path, 'r', encoding='UTF-8') as openfile:
            acquire_lock()
            mod = load_module("mod", openfile, file_path, ('.py', 'r', PY_SOURCE))
            if hasattr(mod, "__all__"):
                attrs = [getattr(mod, x) for x in mod.__all__]
                for obj in attrs:
                    if not issubclass(obj, iPlugin):
                        continue
                    plugin = obj()
                    print("find plug name: %s" % plugin.name)
    except Exception as e:
        plugin = None
    finally:
        pass
    release_lock()
    return plugin

# 分析插件包，获取相关信息
def plugin_analysis(pulgin_url):
    pulgin_filepath = us.get_filepath_from_url(pulgin_url, None) # 如果是网络地址则先下载到临时目录下再读取
    if (pulgin_filepath == None):
        pulgin_filepath = os.path.join(pulgin_url) # 本地地址

    if (us.path_exists(pulgin_filepath) == False):
        ab.print_log("plugin file is not exists (%s)" % pulgin_filepath, "error")
        return None
    _, _, name, suffix = us.get_path_name_suffix_from_filepath(pulgin_filepath)

    plugin_config_jaon = {}
    if (suffix.lower() == '.zip'):
        config_file_data = us.get_file_from_zipfile(pulgin_filepath, default_params['plugin_config_filename'])
        config_file_data = str(config_file_data, 'utf-8')

        plugin_config_jaon = json.loads(config_file_data)
    elif (suffix.lower() == '.py'):
            plugin_obj = load_plugin(pulgin_filepath)
            if (plugin_obj is not None):
                base = {}
                base['name'] = plugin_obj.name
                base['showname'] = plugin_obj.showname
                base['version'] = plugin_obj.version
                base['description'] = plugin_obj.description
                base['role'] = plugin_obj.role
                plugin_config_jaon['base'] = base

                plugin_config_jaon['params'] = plugin_obj.params
    else:
        plugin_config_jaon = None

    if (plugin_config_jaon is not None):
        ab.print_log("plugin analysis: (name: %s, showname: %s, version: %s, description: %s, role: %s)" % ( \
                    plugin_config_jaon['base']['name'], \
                    plugin_config_jaon['base']['showname'], \
                    plugin_config_jaon['base']['version'], \
                    plugin_config_jaon['base']['description'], \
                    plugin_config_jaon['base']['role'] \
                    ), "info")

    return plugin_config_jaon

# 根据url获取插件项目信息，并生成相关结构返回
def plugin_load(pulgin_url):
    parsed = us.get_parse_from_url(pulgin_url)
    if (parsed.scheme.lower() != 'http'): # 暂时只支持http协议
        return None
    hostaddr = parsed.scheme + '://' + parsed.netloc

    plugin_config_jaon = us.get_json_from_url(pulgin_url)
    if (plugin_config_jaon is None):
        return None
    meta_json_obj = plugin_config_jaon['meta']
    ab.print_log(meta_json_obj)

    plugins_json_obj = plugin_config_jaon['plugins']
    for plugin_info in plugins_json_obj:
        plugin_info_obj = plugins_json_obj[plugin_info]
        download_url = hostaddr + plugin_info_obj['download_url']

        plugin_obj = Plugin_Object(download_url)

        # ab.print_log(plugin_info_obj)

    return plugin_config_jaon

def plugin_test(pulgin_url):
    return plugin_load(pulgin_url)

#######################################################################################

def parse_args():
    """Parse arguments."""
    # Parameters settings
    parser = argparse.ArgumentParser(
        prog="python manage.py", description="-- Worker Service --", epilog="---------------------")
    
    # 环境测试及初始化
    parser.add_argument('-v', '--ver', action='store_true', default=False, help='版本及配置信息')

    # 启动链接
    parser.add_argument('--input', type=str, default='none', help='启动链接')

    # 定时器
    parser.add_argument('--timer', type=str, default='', help='定时器')

   # 压缩打包
    parser.add_argument('-p', '--pack', action='store_true', default=False, help='插件打包')

    # 目录设置
    parser.add_argument('--output', type=str, default='', help='输出设置')

    # parse the arguments
    args = parser.parse_args()

    return args

def add_job_at_timer(scheduler, fun, timer, value):

    import time, datetime

    category = us.check_attribute(timer, 'category')
    periodic = us.check_attribute(timer, 'periodic')
    start_time = us.check_attribute(timer, 'start_time')

    if (periodic.lower() == 'everminute'):
        job = scheduler.add_job(fun, 'interval', minutes=int(start_time), args=[value])
    elif (periodic.lower() == 'everhour'):
        job = scheduler.add_job(fun, 'interval', hours=int(start_time), args=[value])
    else:
        format = us.get_data_format(start_time)
        time = us.datetime_conv(start_time, 
                return_type = datetime.datetime, format = format)

        if (periodic.lower() == 'everday'): # 每天
            job = scheduler.add_job(fun, 'cron', 
                hour=time.hour, minute=time.minute, second=time.second, args=[value])
        elif (periodic.lower() == 'workingday'): # 工作日
            job = scheduler.add_job(fun, 'cron', day_of_week='mon-fri',
                hour=time.hour, minute=time.minute, second=time.second, args=[value])
        elif (periodic.lower() == 'weekend'): # 周末
            job = scheduler.add_job(fun, 'cron', day_of_week='sat,sun',
                hour=time.hour, minute=time.minute, second=time.second, args=[value])
        elif (periodic.lower() in 'mon,tue,wed,thu,fri,sat,sun'): # 周几
            job = scheduler.add_job(fun, 'cron', day_of_week=periodic.lower(),
                hour=time.hour, minute=time.minute, second=time.second, args=[value])

    pass

def run(config):
    ab.print_log('start plugin runner ...')

    # file_list = [__file__]
    # us.send_mail(host="smtp.atoml.com", port=25, username="admin@atoml.com", password="Aa!112233", file_list=file_list, subject="plugins send", body="is test")

    from plugin_utility.plugin_manager import load_plugin_runner

    plugin_runner = load_plugin_runner(config)
    if (plugin_runner is not None):
        plugin_runner.run()

    ab.print_log('finish plugin runner .')

def get_configfile_from_xx(config):
    if not os.path.isfile(config):
        # 不是文件，是应用名称或者目录
        suffix = us.get_suffix_from_filepath(config)
        if (len(suffix) <= 0) or (not us.path_exists(config)):
            if (us.path_exists(os.path.join(config, 'config.json'))):
                config = os.path.join(config, 'config.json')
            else:
                # 合成配置文件
                config = os.path.join(os.getcwd(), 'apps', config, 'config.json')

    if (not us.path_exists(config)):
        ab.print_log('cannot find file %s' % config, level = 'error')
        return None
    return config

def run_at_xx(config, block = True):

    app_type = us.get_type(config)
    if (app_type.lower() == 'http'):
        ab.print_log('download start url to json object from %s' % config)
        try:
            config = us.get_json_from_url(config)
        except Exception as e:
            ab.print_log(e, 'error')
            config = None
            pass

        config_filepath = os.path.join(os.getcwd(), "config.json")
        if (config is None):
            if us.path_exists(config_filepath):
                ab.print_log('load local config file.', 'CRITICAL')
                return run_at_xx(config_filepath)

            ab.print_log('download start url failed!', 'error')
            return False
        else:
            with open(config_filepath, 'w') as file_obj:
                json.dump(config, file_obj)
    else:
        ab.print_log('load start json object from %s' % config)
        config = get_configfile_from_xx(config)
        if (not us.path_exists(config)):
            ab.print_log('config is not exists and exit!')
            return False
        config = json.load(open(config, 'r', encoding='UTF-8'))

        if (config is None):
            ab.print_log('open start json object failed!', 'error')
            return False

    timers = us.check_attribute(config, 'values.timers', None)
    if (timers is not None) and (os.environ.get('DEBUG', 'FALSE').upper() == 'FALSE'):

        timers = get_timer_from_json(timers)

        if (block):
            from apscheduler.schedulers.blocking import BlockingScheduler
            
            scheduler = BlockingScheduler(timezone="Asia/Shanghai")

            for timer in timers:
                add_job_at_timer(scheduler, run, timer, config)

            scheduler.start()
        else:
            from apscheduler.schedulers.background import BackgroundScheduler

            scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
    
            for timer in timers:
                add_job_at_timer(scheduler, run, timer, config)

            scheduler.start()
        pass
    else: 
        run(config)

    return True

def Plugin_Main():
    cwd = os.getcwd()
    app_name = os.environ.get('APP_NAME', '')
    ab.print_log("启动应用: %s" % app_name)
    us.initialize(cwd, app_name)

    args = parse_args()

    if args.ver:
        ab.print_current_env_information()

    # 打包流程
    if args.pack:
        plugins_dir = os.path.join(cwd, 'plugins')
        output_dir = args.output
        if len(output_dir) <= 0:
            output_dir = os.path.join(cwd, 'data', 'plugins')
            us.check_path_exists(output_dir)

        ab.print_log('start packing (%s => %s).!' % (plugins_dir, output_dir))
        us.subdir_pack(plugins_dir, output_dir, '*')
        sys.exit(0)

    ###################################################################################

    config = None
    if (args.input == 'none'):
        config = os.environ.get(args.input, None)
    else:
        config = args.input

    if (config is None):
        ab.print_log('Input parameter error!')
        sys.exit(0)
        
    ab.print_log("start run at %s" % config)
    run_at_xx(config)
