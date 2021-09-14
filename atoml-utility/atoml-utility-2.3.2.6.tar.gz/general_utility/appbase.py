import os
import sys
import datetime
import json

from . import utils as us

from . import logger as logger

NAME = "atoml-utility"
DESCRIPTION = "atoml ct system utility."
URL = "https://atoml.com/"
EMAIL = "caijun@atoml.com"
AUTHOR = "caijun"
REQUIRES_PYTHON = ">=3.6.0"
VERSION = "2.3.2.6"

#######################################################################################

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

def get_timer_from_json(values):
    result = []
    if (isinstance(values, dict)):
        name = us.check_attribute(values, 'name', '')
        timers = us.check_attribute(values, 'timer', None)
        if (timers is None):
            return None
        for timer in timers:
            result.append(timer)
            ab.print_log('add timer: %s, %s, %s, %s' % (name,
                            timer['category'],
                            timer['periodic'],
                            timer['start_time']))
    elif (isinstance(values, list) and len(values) > 0):
        for value in values:
            result.extend(get_timer_from_json(value))

    return result

def get_timer_from_url(url):
    job_config = us.get_json_from_url(url)
    if (job_config is None):
        return None

    timer_entry = us.check_attribute(job_config, 'values.entry.timers', 'timers')
    values = us.check_attribute(job_config, ('values.%s' % timer_entry), 'now')
    if (isinstance(values, str)):
        return values

    return get_timer_from_json(values)

def get_timer_from_urls(url):
    job_config = us.get_json_from_url(url)
    if (job_config is None):
        return None
    timers = []
    items = us.check_attribute(job_config, 'items', [])
    for item in items:
        detail_url = us.check_attribute(item, 'meta.detail_url', None)
        if (detail_url is not None):
            timer = get_timer_from_url(detail_url)
            if (timer is not None):
                timers.append(timer)
    pass

#######################################################################################

class AppBase:

    class cmdobj:
        def __init__(self, cmd, time):
            self.cmd = cmd
            self.time = time

    def haslog(self):
        return us.obj_hasattr(self, "log")
    
    def print_log(self, log, level = "info"):
        if (self.haslog()):
            return self.log.output(log, level)

        print(log)

    def __init__(self, log_name = None,  level = "info", logconsole = True):

        if log_name is None:
            return

        self.set_loger(log_name, level = level, logconsole = logconsole)

    def set_loger(self, log_name = "", level = "info", logconsole = True):
        self.remove_loger()

        # init log obj
        self.log_path = os.getenv('LOGS_PATH', os.path.join(os.getcwd(), 'logs'))
        us.mkdir(self.log_path)

        if (len(log_name) <= 0):
            self.log_file = os.getenv('LOG_FILE', os.path.join(self.log_path, ('${PID}_${TIME}.log')))
        else:
            self.log_file = os.path.join(self.log_path, log_name + '.log')

        pID = str(os.getppid())
        self.log_file = self.log_file.replace("${PID}", pID)

        nowTime = datetime.datetime.now().strftime('%Y-%m-%d-%H')
        self.log_file = self.log_file.replace("${TIME}", nowTime)

        self.log = logger.logger(logfilename = self.log_file, appname = __name__, level = level, logconsole = logconsole)

    def remove_loger(self):
        if (self.haslog()):
            self.log.remove_filehandle()

    local_infos_static = [ # 静态字段，一次运行只取一次
            'localtime',
            'cpu_count',
            'users_count',
            'users_list',
            'hostname',
            'local_ip',
            'remote_ip',
            'mac',
        ]

    def is_update(self, field, fields):
        result = None
        if (field in fields) or (field.lower() == '*'): # 白名单
            if (field in self.local_infos_static) and (us.obj_hasattr(self, 'local_infos')): # 如果是静态的变量则返回之前保存的值
                result = us.check_attribute(self.local_infos, field, "")
            return True, result
        return False, result

    def get_local_infos(self, fields = "*"):
        
        import time
        import psutil
        
        result = us.check_attribute(self, 'local_infos', {})

        ####################################################

        b, v = self.is_update('localtime', fields)
        if (b): # 需要返回的字段
            if (v is None): # 需要取值的字段
                v = time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime(time.time()))
            result['localtime'] = v

        b, v = self.is_update('cpu_count', fields)
        if (b): # 需要返回的字段
            if (v is None): # 需要取值的字段
                v = ("%d:%d" % (psutil.cpu_count(logical=False), psutil.cpu_count(logical=True)))
            result['cpu_count'] = v

        b, v = self.is_update('cpu_utilization', fields)
        if (b): # 需要返回的字段
            if (v is None): # 需要取值的字段
                v = (str(psutil.cpu_percent(1))) + '%'
            result['cpu_utilization'] = v

        b, v = self.is_update('users_count', fields)
        if (b): # 需要返回的字段
            if (v is None): # 需要取值的字段
                v = len(psutil.users())
            result['users_count'] = v

        b, v = self.is_update('users_list', fields)
        if (b): # 需要返回的字段
            if (v is None): # 需要取值的字段
                v = ",".join([u.name for u in psutil.users()])
            result['users_list'] = v

        ####################################################

        b, v = self.is_update('virtual_memory', fields)
        if (b): # 需要返回的字段
            if (v is None): # 需要取值的字段
                free = str(round(psutil.virtual_memory().free / (1024.0 * 1024.0 * 1024.0), 2))
                total = str(round(psutil.virtual_memory().total / (1024.0 * 1024.0 * 1024.0), 2))
                memory = int(psutil.virtual_memory().total - psutil.virtual_memory().free) / float(psutil.virtual_memory().total)
                v = ("%s/%s %.3f" % (free, total, memory))
            result['virtual_memory'] = v

        b, v = self.is_update('swap_memory', fields)
        if (b): # 需要返回的字段
            if (v is None): # 需要取值的字段
                swap_free = str(round(psutil.swap_memory().free / (1024.0 * 1024.0 * 1024.0), 2))
                swap_total = str(round(psutil.swap_memory().total / (1024.0 * 1024.0 * 1024.0), 2))
                swap_memory = int(psutil.swap_memory().total - psutil.swap_memory().free) / float(psutil.swap_memory().total) 
                v = ("%s/%s %.3f" % (swap_free, swap_total, swap_memory))
            result['swap_memory'] = v

        ####################################################

        b, v = self.is_update('hostname', fields)
        if (b): # 需要返回的字段
            if (v is None): # 需要取值的字段
                import socket
                v = socket.gethostname() #获取本机主机名
            result['hostname'] = v

        b, v = self.is_update('local_ip', fields)
        if (b): # 需要返回的字段
            if (v is None): # 需要取值的字段
                v = us.get_local_ip() #获取本机ip地址
            result['local_ip'] = v

        b, v = self.is_update('remote_ip', fields)
        if (b): # 需要返回的字段
            if (v is None): # 需要取值的字段
                v = us.get_remote_ip() #获取本机ip地址
            result['remote_ip'] = v

        b, v = self.is_update('mac', fields)
        if (b): # 需要返回的字段
            if (v is None): # 需要取值的字段
                import uuid
                v = uuid.UUID(int=uuid.getnode()).hex[-12:]
            result['mac'] = v

        ####################################################

        b, v = self.is_update('net_io', fields)
        if (b): # 需要返回的字段
            if (v is None): # 需要取值的字段
                net = psutil.net_io_counters()
                bytes_sent = '{0:.2f} Mb'.format(net.bytes_sent / 1024 / 1024)
                bytes_recv = '{0:.2f} Mb'.format(net.bytes_recv / 1024 / 1024)
                v = ("%s / %s" % (bytes_sent, bytes_recv))
            result['net_io'] = v

        b, v = self.is_update('disk', fields)
        if (b): # 需要返回的字段
            if (v is None): # 需要取值的字段
                io = psutil.disk_partitions()
                o = psutil.disk_usage("/")
                ioo=psutil.disk_io_counters()

                free = int(o.free / (1024.0 * 1024.0 * 1024.0))
                total = int(o.total / (1024.0 * 1024.0 * 1024.0))

                v = ("%d G / %d G" % (free, total))
            result['disk'] = v

        b, v = self.is_update('process', fields)
        if (b): # 需要返回的字段
            if (v is None): # 需要取值的字段
                v = {}
                v['process'] = {'count': len(psutil.pids())}
                for pnum in psutil.pids():
                    v['process'][pnum] = psutil.Process(pnum)
            result['process'] = v['process']

        ####################################################

        if (result is not None) and (len(result) > 0):
            if (us.obj_hasattr(self, 'local_infos')):
                self.local_infos = us.dict_merged(self.local_infos, result)
            else:
                self.local_infos = result

        ####################################################

        return result

    def print_current_env_information(self):
        us.TestPlatform()
        print("-----------------------------")
        print(DESCRIPTION)
        print(VERSION)

        if (us.obj_hasattr(self, "schedules") != False):
            print("schedule count:", str(len(self.schedules)))

            for index in range(0, len(self.schedules)):
                item = self.schedules[index]
                print('schedule', index, ":")
                print(" cmd:", item['cmd'])
                print("  at:", item['at'])
                
        print("-----------------------------")

ab = AppBase(None)
