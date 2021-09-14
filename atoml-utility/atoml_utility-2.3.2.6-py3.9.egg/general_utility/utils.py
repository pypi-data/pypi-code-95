
import os
import sys
import string
import time
import datetime
import platform
import multiprocessing
import subprocess

def obj_hasattr(obj, name): 
    return hasattr(obj, name)

def obj_getattr(obj, name): 
    return getattr(obj, name)

def obj_callable(obj, name): 
    return callable(getattr(obj, name))

def TestPlatform():
    print ("--------------Operation System-----------------------")
    #Windows will be : (32bit, WindowsPE)
    #Linux will be : (32bit, ELF)
    print(platform.architecture())

    #Windows will be : Windows-XP-5.1.2600-SP3 or Windows-post2008Server-6.1.7600
    #Linux will be : Linux-2.6.18-128.el5-i686-with-redhat-5.3-Final
    print(platform.platform())

    #Windows will be : Windows
    #Linux will be : Linux
    print(platform.system())

    print ("--------------Python Version-------------------------")
    #Windows and Linux will be : 3.1.1 or 3.1.3
    print(platform.python_version())

def UsePlatform():
    sysstr = platform.system()
    return sysstr

#########################################################
# 其它工具

supported_protocols = {
    'http',
    'mysql',
    'redis',
    'minio'
}

def get_type(param):
    if param is None:
        return 'unknown'

    if isinstance(param, str):
        if (os.path.isdir(param)):
            return 'dir'
        elif (os.path.isfile(param)):
            return 'file'
        else:
            scheme = get_scheme_from_url(param)
            if scheme is None:
                return 'unknown'
            if (scheme.lower() in supported_protocols):
                return scheme.lower()
    elif isinstance(param, dict):
        return check_attribute(param, 'type', 'dict')
    return 'unknown'

#########################################################
# 文件路径等工具

 # 当前文件的父目录绝对路径
def get_parent_dir(filename = sys.argv[0]): 
    parent_dir = os.path.dirname(filename)
    if (parent_dir[-1] != "/"):
        parent_dir = parent_dir + "/"
    return parent_dir

# 获取当前路径
def get_cur_dir():
    cur_dir = os.path.abspath(os.curdir)
    if (cur_dir[-1] != "/"):
        cur_dir = cur_dir + "/"
    return cur_dir

# 从路径中获取所在路径
def get_dir_from_filepath(filepath):
    return os.path.dirname(filepath)

# 从路径中获取文件名
def get_filename_from_filepath(filepath):
    return os.path.basename(filepath)

# 获取文件路径和扩展名
def get_path_suffix_from_filepath(filepath):
    return os.path.splitext(filepath)[0], os.path.splitext(filepath)[1]

# 获取文件名和扩展名
def get_name_suffix_from_filepath(filepath):
    path, filename = os.path.split(filepath)
    return os.path.splitext(filename)

# 获取文件扩展名
def get_suffix_from_filepath(filepath):
    return os.path.splitext(filepath)[1]

# 文件路径全拆解
def get_path_name_suffix_from_filepath(filepath):
    path, filename = os.path.split(filepath)
    name, suffix = get_path_suffix_from_filepath(filename)
    return path, filename, name, suffix

# 整合路径，并且末尾加 /
def path_join(filepath1, filepath2):
    path = os.path.join(filepath1, filepath2)
    if (path[-1] != "/"):
        path = path + "/"
    return path

# 检查路径是否存在，如果不存在则创建
def check_path_exists(filepath):
    suffix = get_suffix_from_filepath(filepath)
    
    path = filepath
    if (suffix is not None) and (len(suffix) > 0):
        path = os.path.dirname(filepath)
    if not path_exists(path):
        if (mkdir(path) == False):
            return None

    # if (path[-1] != "/"):
    #     path = path + "/"
    return path

# 判断路径是否存在
def path_exists(path):
    if isinstance(path, str):
        return os.path.exists(path)
    else:
        return False

# 递归目录
def rm_dir(dir):
    for root, dirs, files in os.walk(dir, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))

def get_first_exists_path(filename, search_path_list):
    for path in search_path_list:
        filepath = os.path.join(path, filename)
        if path_exists(filepath):
            return filepath

    return None

def get_dirname(path, level = 1):
    for i in range(level):
        path = os.path.dirname(path)

    return path

def move_file(srcfile, dstdir):
    import shutil
    if not os.path.isfile(srcfile):
        print("%s not exist!" % srcfile)
        return None

    fpath, fname = os.path.split(srcfile)

    mkdir(dstdir)

    if (dstdir[-1] != "/"):
        dstdir = dstdir + "/"
    dstfile = dstdir + fname
    shutil.move(srcfile, dstfile)
    print("move %s -> %s" % (srcfile, dstfile))
    return dstfile

def copy_file(srcfile, dstfile):
    import shutil
    if not os.path.isfile(srcfile):
        print("%s not exist!" % srcfile)
        return None

    if (dstfile[-1] == "/"):
        _, filename, _, _ = get_path_name_suffix_from_filepath(srcfile)
        dstfile = dstfile + filename
    else:
        path, _, _, _ = get_path_name_suffix_from_filepath(dstfile)
        mkdir(path)

    shutil.copyfile(srcfile, dstfile)
    return dstfile

# 创建一个目录
def mkdir(path):
    path = path.strip() # 去除首位空格
    path = path.rstrip("\\") # 去除尾部 \ 符号
    # 判断结果
    if not path_exists(path):
        os.makedirs(path) # 如果不存在则创建目录

# 获取文件修改时间
def getfiletime(path):
    timestamp = os.path.getmtime(path)
    return timestamp, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))

# 获取一个随机字符串
def get_random_string(length=12,
                      allowed_chars='abcdefghijklmnopqrstuvwxyz'
                                    'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    import secrets
    return ''.join(secrets.choice(allowed_chars) for i in range(length))
    
# 如果文件已经存在则从新生成一个随机文件名返回
def get_alternative_name(filepath):
    # if not path_exists(filepath):
    #     return filepath
    path, filename, name, suffix = get_path_name_suffix_from_filepath(filepath)

    filename = '%s_%s%s' % (name, get_random_string(7), suffix)
    return os.path.join(path, filename)

#########################################################
# 字典，列表等

# 判断一个字典或者一个列表里是否有某属性
def check_attribute(params, att, default = None):
    result = default
    
    if params is None:
        return result
        
    if (att.find('.') > 0):
        att = params_split(att, '.')
        for item in att:
            result = check_attribute(params, item, default)
            break
    elif isinstance(params, dict) and (att in params):
        result = params[att]
    elif isinstance(params, list):
        for item in params:
            if (att in item):
                result = check_attribute(item, att, default)
                break

    return make_param(result, params)

def att_isin(params, att):
    if isinstance(params, list) or isinstance(params, dict):
        return (att in params)
    return False

# 一维参数分割
def params_split(params, flag = ':'):
    params = params.split(flag)
    for i in range(len(params)):
        params[i] = params[i].strip()
    return params

# 键值分离
def key_value_split(params, default_key = ''):
    key = default_key
    start = params.find(':')
    if (start >= 0):
        key = params[:start]
        value = params[start + 1:]
    else:
        value = params
    return key, value

# 二维参数分割，返回一个字典
def str_to_dict(params, flag1 = ',', flag2 = ":"):
    if (params == ""):
        return None

    param_dict = {}
    params = params_split(params, flag = flag1)
    for param in params:
        item = params_split(param, flag = flag2)
        param_dict[item[0]] = item[1]
    return param_dict

# 字典依据某一个Key进行排序
def dict_sorted(data, by, ascending = True):
    if (data == None):
        return None

    result = data
    for i in range(0, len(result) - 1):
        j = i + 1
        while j > 0:
            if (((ascending) and (result[j][by] < result[j - 1][by])) or 
                ((ascending == False) and (result[j][by] > result[j - 1][by]))):
                tmp = result[j - 1]
                result[j - 1] = result[j]
                result[j] = tmp
            j = j - 1

    return result

def get_var(data):
    result = []
    start_tag = '${'
    end_tag = '}'
    i = 0
    while i < len(data):
        start = data[i:].find(start_tag)
        if (start < 0): break
        end = data[i + start:].find(end_tag)
        if (end < 0): break
        source = data[(i + start + len(start_tag)):(i + start + end)]
        source = source.upper() # 参数替换，注意：en这里只认大写
        result.append(source)

        i = i + len(start_tag + source + end_tag)
        
    if (len(result) == 1):
        result = result[0]
    return result

# 参数通配符替换，如${source}，替换为参数字典里的值
def item_place(data, param_dict):
    start_tag = '${'
    end_tag = '}'
    i = 0
    while i < len(data):
        start = data[i:].find(start_tag)
        if (start < 0): break
        end = data[i + start:].find(end_tag)
        if (end < 0): break
        source = data[(i + start + len(start_tag)):(i + start + end)]
        source = source.upper() # 参数替换，注意：这里只认大写

        if (param_dict == None):
            dest = os.getenv(source, None)
        else:
            dest = param_dict.get(source)

        if (dest is None):
            i = i + len(start_tag + source + end_tag)
        else:
            if isinstance(dest, str):
                i = i + start
                data = data.replace(start_tag + source + end_tag, dest)
                i = i + len(dest)
            else:
                # 非字符串时的对象处理流程，只在单字段赋值时使用
                if ((start + end + 1) >= len(data)):
                    data = param_dict[source]
                    break

    return data

# 字典通配符替换
def dict_place(data_dict, param_dict):
    for (key, value) in  data_dict.items():
        if isinstance(value, str):
            data_dict[key] = item_place(value, param_dict)
        elif isinstance(value, dict):
            value = dict_place(value, param_dict)
    return data_dict

# 列表通配符替换
def list_place(data_dict, param_dict):
    for index in range(0, len(data_dict)):
        if isinstance(data_dict[index], str):
            data_dict[index] = item_place(data_dict[index], param_dict)
    return data_dict

# 通配符替换自动适配，唉，牛逼坏了
def make_param(data, param_dict = None):
    if (isinstance(param_dict, dict) or (param_dict is None)):
        if isinstance(data, dict):
            data = dict_place(data, param_dict)
        elif isinstance(data, list):
            data = list_place(data, param_dict)
        elif isinstance(data, str):
            data = item_place(data, param_dict)

    return data

def str_to_fields(str, split_flag = ',', add_flag = '`'):
    result = ''
    strs = params_split(str, split_flag)
    for item in strs:
        if (len(result) > 0):
            result = '%s%s%s%s%s' % (result, split_flag, add_flag, item, add_flag)
        else:
            result = '%s%s%s' % (add_flag, item, add_flag)
    return result
    
# 字典合并
def dict_merged(dict1, dict2):
    if (dict1 is None) and (dict2 is None):
        return None
    if (dict1 is None) or (len(dict1) <= 0):
        return dict2
    if (dict2 is None) or (len(dict2) <= 0):
        return dict1
        
    return dict(dict1, **dict2)

# 字典合并，另一种方式
def merge_dict(x, y):
    for k, v in x.items():
        if k in y.keys():
            y[k] += v
        else:
            y[k] = v

# 字典拷贝
def dict_copy(data, keys = "*", default = ""):
    if isinstance(keys, str) and (keys != "*"):
        keys = params_split(keys, ',')

    if not isinstance(keys, list) and (keys != '*'):
        return None

    if not isinstance(data, dict):
        return None
    
    result = {}
    try:
        for key in data:
            if (key in keys) or (keys == '*'):
                result[key] = check_attribute(data, key, default)
    finally:
        pass

    return result

#########################################################
# 应用初始化

def sub_process(cmd):
    print(cmd)
    import subprocess
    try:
        return_info = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while True:
            next_line = return_info.stdout.readline()
            return_line = next_line.decode("utf-8", "ignore")
            if return_line == '' and return_info.poll() != None:
                break
            print(return_line)
        returncode = return_info.wait()
        if returncode:
            raise subprocess.CalledProcessError(returncode, return_info)
        return True
    except Exception as e:
        print(e)
        return False

def initialize(path, prefix = ''):
    PIP_MIRRORS_URL = os.getenv("PIP_MIRRORS_URL", None)

    initialize_file = os.path.join(path, ('%s.initialize' % prefix))
    
    if path_exists(initialize_file):
        return True

    sysstr = UsePlatform()

    init_filename = 'initialize.bat'
    if (sysstr.lower() == 'linux') or (sysstr.lower() == 'darwin'):
        init_filename = 'initialize.sh'
    init_filename = os.path.join(path, init_filename)
    if (path_exists(init_filename) == True):
        if (sysstr.lower() == 'linux') or (sysstr.lower() == 'darwin'):
            sub_process("chmod +x %s" % init_filename)

        if (sub_process(init_filename) == False):
            return False

    if (path_exists(os.path.join(path, 'requirements.txt')) == True):
        filename = os.path.join(path, 'requirements.txt')
        cmd = ("pip install -r %s" % filename)
        if (PIP_MIRRORS_URL is not None):
            cmd = ("%s -i %s" % (cmd, PIP_MIRRORS_URL))
        if (sub_process(cmd) == False):
            return False

    with open(initialize_file, "w") as f:
        f.write("initialize succeed.")

#########################################################
# 日期，时间等

def get_data_format(time_d):
    format_list = [
        "%H:%M",
        "%H:%M:%S",
        "%Y%m%d",
        "%Y-%m-%d",
        "%Y%m%d %H:%M",
        "%Y-%m-%d %H:%M",
        "%Y%m%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
    ]

    for format in format_list:
        try:
            datetime.datetime.strptime(time_d, format)
            return format
        except:
            continue
            pass

    return None 

def datetime_conv(time_d, return_type = str, format = "%Y%m%d"):
    if (format is None):
        format = get_data_format(time_d)

    if isinstance(time_d, str) and (return_type == str):
        time_d = datetime.datetime.strptime(time_d, get_data_format(time_d))
        return time_d.strftime(format)

    if isinstance(time_d, str) and (return_type == datetime.datetime):
        return datetime.datetime.strptime(time_d, format)

    if (isinstance(time_d, datetime.datetime) or isinstance(time_d, datetime.date) or isinstance(time_d, datetime.time)):
        if (return_type == str):
            return time_d.strftime(format)
        elif (return_type == datetime.datetime):
            return time_d
    return None

def datetimestr_conv(time_d, src = "%Y%m%d", dest = "%Y-%m-%d"):
    time_d = datetime_conv(time_d, datetime.datetime, format = src)
    return datetime_conv(time_d, str, format = dest)

def datetime_compare(time_a, time_b, format_a = "%Y-%m-%d", format_b = "%Y-%m-%d"):
    time_a = datetime_conv(time_a, datetime.datetime, format_a)
    time_b = datetime_conv(time_b, datetime.datetime, format_b)
    if (time_a > time_b):
        return 1
    if (time_a < time_b):
        return -1
    if (time_a == time_b):
        return 0

def datetime_Isinside(time_a, time_0, time_1, format = "%Y-%m-%d"):
    time_a = datetime_conv(time_a, datetime.datetime, format)
    time_0 = datetime_conv(time_0, datetime.datetime, format)
    time_1 = datetime_conv(time_1, datetime.datetime, format)
    if (time_a <= time_0):
        return -1
    if (time_a >= time_1):
        return 1
    if (time_a > time_0) and (time_a < time_1):
        return 0

def datetime_tomorrow(time, format = None):
    delta = datetime.timedelta(days=1)
    time = datetime_conv(time, datetime.datetime, format) + delta

    if (format is not None):
        time = time.strftime(format)
    return time

def datetime_yesterday(time, format = None):
    delta = datetime.timedelta(days=1)
    time = datetime_conv(time, datetime.datetime, format) - delta

    if (format is not None):
        time = time.strftime(format)
    return time

def datetime_timedelta_n(time, n, format = None):
    delta = datetime.timedelta(days=n)
    time = datetime_conv(time, datetime.datetime, format) - delta

    if (format is not None):
        time = time.strftime(format)
    return time

def now(format = None):
    time = datetime.datetime.now()

    if (format is not None):
        time = time.strftime(format)
    return time


def tomorrow(format = None):
    time = datetime_tomorrow(datetime.datetime.now())

    if (format is not None):
        time = time.strftime(format)
    return time

def yesterday(format = None):
    time = datetime_yesterday(datetime.datetime.now())

    if (format is not None):
        time = time.strftime(format)
    return time

def check_date(date, format = None):
    if (date is None):
        date = "yesterday" # 默认为昨天

    import datetime
    if isinstance(date, str):
        if (date.lower() == "now") or (date.lower() == "null") or (date.lower() == "none"):
            date = now() # 截止到今天日期
        elif (date.lower() == "tomorrow"):
            date = datetime_tomorrow(now())
        elif (date.lower() == "yesterday"):
            date = datetime_yesterday(now())

    if (format is not None):
        date = datetime_conv(date, return_type = str, format = format)
    return date

#########################################################
# 字符串等

def str_clear(src):
    src = src.replace('\r', '')
    src = src.replace('\n', '')
    src = src.replace(' ', '')

    return src

def str_to_JSON(src):
    src = str_clear(src)
    result = None
    try:
        import json
        result = json.loads(src)
    except Exception as e:
        print("e: ", e)
    return result

def file_to_JSON(file):
    obj = None
    with open(file, 'r') as f:
        try:
            import json
            obj = json.load(f)
        except Exception as e:
            print("e: ", e)
    f.close
    return obj

def str_to_bool(str):
    return True if str.lower() == 'true' else False

def isint(num):
    try:
        num = int(str(num))
        return isinstance(num, int)
    except:
        return False

def get_str_md5(v): 
    import hashlib
    # Message Digest Algorithm MD5（中文名为消息摘要算法第五版）为计算机安全领域广泛使用的一种散列函数，用以提供消息的完整性保护
    md5 = hashlib.md5()   #md5对象，md5不能反解，但是加密是固定的，就是关系是一一对应，所以有缺陷，可以被对撞出来
 
    ## update需要一个bytes格式参数
    md5.update(v.encode('utf-8'))  #要对哪个字符串进行加密，就放这里
    value = md5.hexdigest()  #拿到加密字符串
 
    return value

def get_file_hash2(file): # 随机获取文件hash
    if (path_exists(file) == False):
        return None

    import hashlib
    hash = hashlib.sha1()
    
    read_size = 1024 * 1024 * 2

    size = os.path.getsize(file)
    pos = 0
    pos2 = int(size / 2)
    pos3 = int(size - read_size)

    with open(file,'rb') as f:
        data = f.read(read_size)
        if data:
            hash.update(data)

        if (pos2 > 0):
            f.seek(pos2)
            data = f.read(read_size)
            if data:
                hash.update(data)

        if (pos3 > 0):
            f.seek(pos2)
            data = f.read(read_size)
            if data:
                hash.update(data)
        f.close()

    return hash.hexdigest()

def get_file_hash(file, count = -1): # count为0时计算全部文件的hash，小于0时抽取样本计算hash
    import hashlib

    if (path_exists(file) == False):
        return None

    size = 0
    hash = hashlib.sha1()

    if (count < 0):
        hash.update(file.encode('utf-8'))
        count = 1024 * 1024 * 5

    read_size = 1024
    with open(file,'rb') as f:
        while True:
            if (size >= count): # 读完了退出
                break

            data = f.read(read_size)
            if not data:
                break

            size = size + len(data)
            hash.update(data)
    return hash.hexdigest()

def get_file_md5(file):
    import hashlib

    if (path_exists(file) == False):
        return None

    md5 = hashlib.md5()
    with open(file,'rb') as f:
        while True:
            data = f.read(1024)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()

def get_file_line_count(file):
    count = 0
    for index, line in enumerate(open(file, 'r', encoding='utf-8')):
        count += 1

    return count

def get_filelist_from_path(dirname, filter = '*'):
    result = [] #所有的文件
    for maindir, subdir, file_name_list in os.walk(dirname):
        # print("1:",maindir) #当前主目录
        # print("2:",subdir) #当前主目录下的所有目录
        # print("3:",file_name_list)  #当前主目录下的所有文件
        for filename in file_name_list:
            apath = os.path.join(maindir, filename)#合并成一个完整路径
            ext = os.path.splitext(apath)[1]  # 获取文件后缀 [0]获取的是除了文件名以外的内容
            if (ext != '') and ((ext in filter) or (filter == '*')):
                result.append(apath)
    return result

def prepared_clean(df, type='dropna'):
    import pandas as pd
    # 清除NaN值
    if type == 'dropna':
        df = df.dropna(axis=0, how='any', inplace=False)  # 删除为空的行
    elif type == 'pad':
        df = df.fillna(method='pad')
    elif type == 'bfill':
        df = df.fillna(method='bfill')
    else:
        df = df.fillna(value=type)
    #
    return df

def prepared_clean_on(df, conditional):
    import pandas as pd
    return df.drop(df[conditional].index)

def print_sys_info():
    lists = sys.argv  # 传递给Python脚本的命令行参数列表 => python p.py -> ['p.py'] / python p.py a 1 -> ['p.py', 'a', '1'] / 程序内执行 -> ['']
    strs = sys.getdefaultencoding()  # 默认字符集名称
    strs = sys.getfilesystemencoding()  # 系统文件名字符集名称
    num = sys.getrefcount(object)  # 返回object的引用计数(比实际多1个)
    dicts = sys.modules  # 已加载的模块, 可修改, 但不能通过修改返回的字典进行修改
    lists = sys.path  # 模块搜索路径
    sys.path.append(".")  # 动态添加模块搜索路径
    strs = sys.platform  # 平台标识符(系统身份进行详细的检查,推荐使用) Linux:'linux' / Windows:'win32' / Cygwin:'cygwin' / Mac OS X:'darwin'
    strs = sys.version  # python解释器版本
    lists = sys.thread_info  # 线程信息
    num = sys.api_version  # 解释器C API版本

#########################################################
# 压缩解压等

def get_file_from_zipfile(zip_path, filename):
    '''
    获取压缩包里面的一个文件
    '''
    import zipfile
    zfile = zipfile.ZipFile(zip_path)
    data = zfile.read(filename)
    zfile.close()
    return data

def extract_file(zip_path, out_path):
    '''
    解压缩文件到指定目录
    '''
    import zipfile
    zfile = zipfile.ZipFile(zip_path)
    filecount = len(zfile.namelist())
    for f in zfile.namelist():

        zfile.extract(f, out_path)

        # # 防止中文乱码
        # try:
        #     f1 = f.encode('cp437').decode('gbk')
        # except Exception as e:
        #     f1 = f.encode('utf-8').decode('utf-8')
        # os.chdir(out_path)  #切换到目标目录
        # os.rename(f, f1)
    zfile.close()
    return filecount

def zip_file(dir, zipfilepath = None, zipfilename = None):
    if (dir[-1] == "/"):
        dir = dir[:-1]

    filelist = get_filelist_from_path(dir, "*")

    path, dirname, name, suffix = get_path_name_suffix_from_filepath(dir)

    if (zipfilepath is None):
        zipfilepath = path

    if (zipfilename is None):
        zipfilename = name + '.zip'

    zipfilepath = os.path.join(zipfilepath, zipfilename)

    check_path_exists(zipfilepath)

    import zipfile
    f = zipfile.ZipFile(zipfilepath, 'w', zipfile.ZIP_DEFLATED)
    for filepath in filelist:
        filename = os.path.relpath(filepath, dir)
        f.write(filepath, filename, compress_type = zipfile.ZIP_DEFLATED)
    f.close()

    return zipfilepath

def subdir_pack(search_dir, output_path, filter = '*'):
    if (path_exists(search_dir) == False):
        print("plugin dir is not exists (%s)" % search_dir, "error")

    for root, dirs, _ in os.walk(search_dir):
        if (root == search_dir): # 此处只遍历一级子目录
            for dir in dirs:
                if dir[0] == '_' or dir[0] == '.':
                    continue
                if (filter == '*') or (filter in dir):
                    source_dir = os.path.join(root, dir)
                    filename = None
                    config = os.path.join(source_dir, 'plugin_config.json')
                    if (path_exists(config)):
                        import json
                        json_obj = json.load(open(config, 'r', encoding='UTF-8'))
                        base = check_attribute(json_obj, 'base')
                        name = check_attribute(base, 'name')
                        version = check_attribute(base, 'version').replace('.', '_')

                        filename = ('%s_%s.zip' % (name, version))

                    zipfilepath = zip_file(source_dir, zipfilepath = output_path, zipfilename = filename)
    return
    
#########################################################
# 上传 相关

def upload_file_to_url(source, url):
    url = get_parse_from_url(url)

    scheme = url.scheme
    path = url.path
    addr = url.hostname + ':' + str(url.port)
    username = url.username
    password = url.password

    # 系统变量替换
    path = make_param(path, None)

    if (scheme == None):
        return False, None

    start = time.perf_counter() # python3.8不支持clock方法了，这不是无聊么

    dir, filename, name, suffix = get_path_name_suffix_from_filepath(source)
    key = get_file_hash2(source)
    filesize = os.path.getsize(source)
    fileid = filename
    link_url = "" # 可访问链接

    # 用户名密码
    if (username is None):
        username = 'admin'
    if (password is None):
        password = '112233'

    if (scheme.lower() in 'http') or (scheme.lower() in 'os'):

        # 如果是对象存储，先取bucket名称
        path = params_split(path, '/')
        ostype = 's3' # 默认使用s3接口
        bucket = 'my-bucket'
        if (len(path) > 2):
            ostype = path[1]
            bucket = path[2]
        else:
            bucket = path[1]

        if (ostype.lower() in 'minio'):
            from minio import Minio
            client = Minio(
                addr,
                access_key=username,
                secret_key=password,
                secure=False
            )
            try:
                if client.bucket_exists(bucket):
                    print("bucket %s exists" % bucket)
                else:
                    print("bucket %s does not exist and create.." % bucket)

                    # Create bucket.
                    client.make_bucket(bucket)

                result = client.fput_object(
                    bucket, key, source,
                    # metadata={name: suffix},
                )

                fileid = result.etag

                print(
                    "created %s object; etag: %s, version-id: %s" % 
                    (result.object_name, result.etag, result.version_id)
                )

                link_url = addr
                # from datetime import timedelta
                # link_url = client.get_presigned_url(
                #     "GET",
                #     bucket,
                #     key,
                #     expires=timedelta(hours=2),
                # )
                
            except Exception as e:
                print('connect minio server failed! (%s)' % e, error)
                pass
    
            pass

        elif (ostype.lower() in 's3'):

            def check_bucket(s3, bucket):
                try:
                    # 新建一个bucket(bucket name 中不能有_下划线)
                    s3.create_bucket(Bucket=bucket)
                except Exception as e:
                    print('create bucket failed! (%s)' % e)

                return True

            def check_object(s3, bucket, key):
                try:
                    s3.Object(bucket, key).load()
                except ClientError as e:
                    print('check object failed! code: (%s)' % (e))
                    return int(e.response['Error']['Code']) != 404
                return True

            import botocore

            from boto3.session import Session
            from botocore.exceptions import ClientError

            session = Session(  aws_access_key_id=username,
                                aws_secret_access_key=password)

            # 连接到S3
            addr = ("http://%s:%d" % (url.hostname, url.port))
            s3 = session.resource('s3', endpoint_url=addr)

            check_bucket(s3, bucket)

            if (check_object(s3, bucket, key) == False):
                try:
                    s3.Bucket(bucket).upload_file(Key=key, Filename=source)
                except Exception as e:
                    print('upload_file failed! (%s)' % e)

            link_url = addr
            # result = s3.Object(bucket, name).upload_file(source)
            
            pass

    elif (scheme.lower() in 'ipfs'):
        import ipfshttpclient
        
        addr = ("/dns/%s/tcp/%d/http" % (url.hostname, url.port))
        with ipfshttpclient.connect(addr) as client:
            path = path.replace('/', '')
            
            fileid = client.add(source, recursive=True)['Hash']
            link_url = storage_link_addr + fileid
    
    elif (scheme.lower() in 'ftp'):
        path, filename, _, _ = get_path_name_suffix_from_filepath(path)

        from .ftptool import ftptool
        ftp_obj = ftptool.FTPHost.connect(url.hostname, port = url.port, user = username, password = password)
        if (filename is None) or (filename == ""):
            filename = get_filename_from_filepath(source)
        save_path = path + '/' + filename

        f = ftp_obj.file_proxy(save_path)
        f.upload_from_file(source)
        pass

    elif (scheme.lower() in 'file'):
        des_path = url.hostname # 格式如 file://${STORAGE_PATH}， 所以把hostname作为路径
        if (not path_exists(des_path)):
            des_path = make_param(des_path, None)
        try:
            check_path_exists(des_path)
        except Exception as e:
            print('preprocessing has except: %s' % e)
        
        fileid = pinyin(filename)
        des_path = os.path.join(des_path, fileid)

        import shutil
        shutil.move(source, des_path)

        link_url = des_path

        pass

    # 测速
    end = time.perf_counter()
    stime = round(end - start, 2)
    speed = filesize / stime
    speed = speed / float(1024*1024)

    print(
                "filename: %s, fileid: %s, filesize: %s m, time: %s s, speed: %s m/s" 
                % (filename, fileid, filesize / float(1024*1024), stime, speed)
    )
    return True, {'key': key, 'url': link_url}

def download_file_from_url(source, save_filepath = None):
    print('download file from %s' % source)

    if (path_exists(source) == True):
        name, suffix = get_name_suffix_from_filepath(source)
        return source, name, suffix

    #########################################################################

    url = get_parse_from_url(source)

    scheme = url.scheme
    path = url.path
    addr = url.hostname + ':' + str(url.port)
    username = url.username 
    if (username is None): username = 'admin'
    password = url.password
    if (password is None): password = 'admin'

    if (path[0] == "/"):
        path = path[1:]
    _, filename, name, suffix = get_path_name_suffix_from_filepath(path)

    #########################################################################

    if (save_filepath == None):
        import tempfile
        save_filepath = tempfile.mktemp(suffix=suffix)
    else:
        save_filepath = os.path.join(save_filepath, filename + suffix)
        check_path_exists(save_filepath)

    #########################################################################

    if (scheme.lower() in 'http'):
        #########################################################################

        from urllib import request #解析url
        from urllib.parse import quote

        s = quote(source, safe=string.printable)
        r = request.urlopen(s)
        if (r.code == 200):
            print('download file filename: %s suffix: %s' % (filename, suffix))

            with open(save_filepath, "wb") as f:
                data = r.read()
                f.write(data)
            f.close
        pass
    elif (scheme.lower() in 'os'):
        #########################################################################

        # 如果是对象存储，先取bucket名称
        path = params_split(path, '/')
        ostype = 's3' # 默认使用s3接口
        bucket = 'my-bucket'
        if (len(path) > 2):
            ostype = path[0]
            bucket = path[1]
            object = path[2]
        else:
            bucket = path[0]
            object = path[1]

        if (ostype.lower() in 'minio'):
            from minio import Minio
            client = Minio(
                addr,
                access_key=username,
                secret_key=password,
                secure=False
            )
            client.fget_object(bucket, object, save_filepath)

            pass
        elif (ostype.lower() in 's3'):
            pass
        pass
    elif (scheme.lower() in 'ipfs'):
        pass
    elif (scheme.lower() in 'ftp'):
        from .ftptool import ftptool
        ftp_obj = ftptool.FTPHost.connect(url.hostname, port = url.port, user = username, password = password)
        filename, suffix = get_name_suffix_from_filepath(source)

        f = ftp_obj.file_proxy(path)
        f.download_to_file(save_filepath)

    elif (scheme.lower() in 'file'):
        save_filepath = path
        pass

    print('download file save to: %s， name: %s, suffix: %s' % (save_filepath, name, suffix))

    return save_filepath, name, suffix

#########################################################
# http 相关

def get_scheme_from_url(url):
    tag = '://'
    pos = url.find(tag)
    if (pos < 0):
        return None
    return url[0:pos]

def get_scheme_path_from_url(url):
    tag = '://'
    pos = url.find(tag)
    if (pos < 0):
        return None
    return url[0:pos], url[(pos + len(tag)):]

def get_filepath_from_url(url, save_filepath = None):
    print('download file from %s' % url)

    from urllib import parse, request #解析url
    from urllib.parse import quote
    import string
    
    parsed = parse.urlparse(url)
    if (parsed.scheme.lower() != 'http'): # 暂时只支持http协议
        return None
    
    filepath = None

    s = quote(url, safe=string.printable)
    r = request.urlopen(s)
    if (r.code == 200):
        filename, suffix = get_name_suffix_from_filepath(parsed.path)
        print('download file filename: %s suffix: %s' % (filepath, suffix))
        if (save_filepath == None):
            import tempfile
            filepath = tempfile.mktemp(suffix=suffix)
        else:
            filepath = os.path.join(save_filepath, filename + suffix)
            check_path_exists(save_filepath)
 
        print('download file save to: %s' % filepath)
        with open(filepath, "wb") as f:
            data = r.read()
            f.write(data)
        f.close
    return filepath

def get_parse_from_url(url):
    from urllib import parse #解析url
    return parse.urlparse(url)

def get_json_from_url(url, default = None):
    import requests
    headers = {'Connection': 'close'}
    requests.adapters.DEFAULT_RETRIES = 5
    requests.session().keep_alive = False # 链接后断掉
    r = requests.get(url, headers = headers)
    if (r.status_code != 200):
        return default

    return r.json()

def post_json_from_url(url, data):
    if (url is None):
        return False, None

    import requests
    import json

    headers = {'Content-Type': 'application/json', 'Connection': 'close'}

    requests.adapters.DEFAULT_RETRIES = 5
    requests.session().keep_alive = False # 链接后断掉
    try:
        result = requests.post(url, data = json.dumps(data), headers = headers)
        if (result.status_code == 200):
            result = json.loads(result.text)
            if (result is not None):
                return True, result
        else:
            result = ("status_code: %d" % result.status_code)

    except Exception as e:
        result = e
    
    requests.session().close

    return False, result

#########################################################

def get_funname_from_protocol_version(protocol_version, prefix = ""):
    ver_list = params_split(protocol_version, '.')
    fun_name = prefix
    fun_name_x = prefix

    i = 0
    for ver in ver_list:
        if i >= 3: # 版本最长4位，最后一位为通配
            fun_name_x = fun_name_x + '_' + 'x'
        else:
            fun_name_x = fun_name_x + '_' + ver

        fun_name = fun_name + '_' + ver
        i = i + 1
    return fun_name, fun_name_x

def get_local_ip(ifname = ""):
    if (len(ifname) <= 0):
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip

    import socket
    import fcntl
    import struct
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915, # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def get_remote_ip(test_url = "http://whatismyip.akamai.com"):
    import requests
    r = requests.get(test_url)
    return r.text

def send_mail( **kwargs):
    from .smtptool.smtptool import send
    send(**kwargs)
    pass

#########################################################

class Timer():
    def __init__(self):
        self.start_dt = None

    def start(self):
        self.start_dt = now()

    def stop(self):
        end_dt = now()
        print('Time taken: %s' % (end_dt - self.start_dt))

class Process(multiprocessing.Process):
    def __init__(self, cmd, args):
        multiprocessing.Process.__init__(self)
        self.args = []
        if (cmd != None):
            self.args.append(cmd)
        for j in range(0, len(args)):
            self.args.append(args[j])

        print(self.args)

    def run(self):
        subprocess.check_call(self.args)