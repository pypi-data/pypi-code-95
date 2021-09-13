# -*- coding:utf-8 -*-
from lcyframe.libs import Copyright

def get_handler_init(path):
    """

    :param path:
    :return:
    """

    auto_str = """%s
import os
import re
import logging
dir_path = os.listdir(os.path.abspath(os.path.dirname(__file__)))

""" % (Copyright.file_pre)

    import_str = """
# xxx_handler xx leng must > 1.
hander_files = [x for x in dir_path if re.findall('[A-Za-z]\w+\.py$', x)]

for hander_file in hander_files:
    model_name = hander_file[:-3]
    if model_name == "__init__":
        continue
    logging.debug("handler [%s] register success!" % hander_file)
    __import__(model_name, globals(), locals(), [model_name], -1)
"""

    return auto_str + import_str


def get_docs_agree():
    """

    :return:
    """
    auto_str = """
## 一、约定说明
### 1.1 参数说明

**参数位置：本框架规定了所有请求时，参数所配置的位置说明：**
* query: 参数位置在？后面：http://www.domain.com/path?{name}={value}
* form-data: 参数位置在body里,以multipart/form-data方式提交。通常表现为json格式
* www-form: 参数位置在body里,以multipart/x-www-form-urlencoded方式提交。通常为表单键值对格式
* file: 参数位置在body里,以multipart/form-data方式提交，常用户上传数据
* raw：不建议
* binary：不建议

**参数值类型：在设置schema.yml时，指定type的值允许是以下几种之一**
* int: 整形
* float: 浮点型
* str: 字符串
* json: json串
* file: 上传文件

### 1.2 headers
API请求时，需要提供请求头

headers：
```
{
    "uid": 用户uid, int,  注册成功、登录成功后返回
    "token": 授权码, str, 注册成功、登录成功后返回
    "locale": "cn",
    "lang": "",
    "version": "", 默认 1.0
    "bundle": "",
    "platform": 0 IOS, 1 Android
    "os": "",
    "device_id": ""
}
```
### 1.3 API 返回结果
所有http_status响应值为200的请求，仅代表本次HTTP请求响应成功。
返回以下2种结果之一：
* 当error=0时，代表应用服务器处理成功，客户端可以正常处理data
* 当error!=0时，代表应用服务器处理失败，error即为对应的异常码。
* msg：字段为本次请求的提示信息
* data：为本次请求返回的数据

result:
```
成功：{"error": 0, "msg": msg, "data": {}}
失败：{"error": 1, "msg": msg, "data": {}}
```

### 1.4 双向校验码seq生成
部分防刷接口需要提供参数seq，生成方法如下

salt：写死在客户端
```
例如：
params={"nickname": "阿刘", "age": "111", "timestamp": 1473761433}
上述2个参数value 均为 utf-8 编码, 根据key的字典顺序排序 键和值之间用"="连接 键值对之间用"&"连接,
生成待校验的字符串string, string 与 salt 字符串 拼接,计算校验码：
seq = md5(salt + "nickname=阿刘&age=111&timestamp=1473761433")
注：凡需要传seq的接口，必须同时提供请求时间戳参数：timestamp
```

### 1.5 翻页码规则：仅支持查看下一页，不支持跳页
参数名：last_id，由服务器返回。客户端可以在请求列表时，回传给服务端，
```
    1、当不提供该参数时，代表查看第一页
    2、当服务端返回last_id=-1时，代表没有下一页了
```

### 1.6 域名配置
api：http://api.domain.com
admin 接口：http://xx.domain.com
docs文档：http://docs.domain.com
"""
    return auto_str


def get_mq_work_init():
    auto_str = """%s
import os
import re
import logging
dir_path = os.listdir(os.path.abspath(os.path.dirname(__file__)))
    """ % Copyright.file_pre

    import_str = """
hander_files = [x for x in dir_path if re.findall('[A-Za-z]\w+_worker\.py$', x)]

for hander_file in hander_files:
    model_name = hander_file[:-3]
    logging.debug("register mq workers [%s.py] success!" % model_name)
    __import__(model_name, globals(), locals(), [model_name], -1)
    """

    return auto_str + import_str


def get_nsq_producer_init(root_path, produce_path):
    """

    :param path:
    :return:
    """

    auto_str = """%s
import os
import re
import logging
from importlib import import_module
from lcyframe.libs.singleton import NsqCon
nsq = NsqCon.get_connection()

dir_path = os.listdir(os.path.abspath(os.path.dirname(__file__)))
produce_path = "%s"
""" % (Copyright.file_pre, produce_path)

    import_str = """
# xxx_handler xx leng must > 1.
hander_files = [x for x in dir_path if re.findall('[A-Za-z]\w+\.py$', x)]

for hander_file in hander_files:
    model_name = hander_file[:-3]
    if model_name == "__init__":
        continue

    model_name = produce_path.strip("/").replace("/", ".") + "." + model_name
    objs = __import__(model_name, fromlist=["*"])
    for p in dir(objs):
        if p.startswith("__"):
            continue
            
        # if not p.lower().startswith("publish"):
            #logging.debug("nsq producer [%s] load fail. it must been start with 'publish'" % p)
        #    continue
        
        if not hasattr(getattr(objs, p), "topic"):
            continue
        
        logging.debug("nsq producer [%s] register success!" % p)
        setattr(nsq, p, getattr(objs, p)())
"""

    return auto_str + import_str


def get_nsq_work_init():
    auto_str = """%s
import os
import re
import logging
dir_path = os.listdir(os.path.abspath(os.path.dirname(__file__)))
    """ % Copyright.file_pre

    import_str = """
hander_files = [x for x in dir_path if re.findall('[A-Za-z]\w+_worker\.py$', x)]

for hander_file in hander_files:
    model_name = hander_file[:-3]
    logging.debug("register nsq workers [%s.py] success!" % model_name)
    __import__(model_name, globals(), locals(), [model_name], -1)

    """
    return auto_str + import_str


def get_mqtt_producer_init(root_path, produce_path):
    """

    :param path:
    :return:
    """

    auto_str = """%s
import os
import re
import logging
from importlib import import_module
from lcyframe.libs.singleton import MqttCon
mqtt = MqttCon.get_connection()

dir_path = os.listdir(os.path.abspath(os.path.dirname(__file__)))
produce_path = "%s"
""" % (Copyright.file_pre, produce_path)

    import_str = """
# xxx_handler xx leng must > 1.
hander_files = [x for x in dir_path if re.findall('[A-Za-z]\w+\.py$', x)]

for hander_file in hander_files:
    model_name = hander_file[:-3]
    if model_name == "__init__":
        continue

    model_name = produce_path.strip("/").replace("/", ".") + "." + model_name
    objs = __import__(model_name, fromlist=["*"])
    # objs = import_module(model_name)  # 重名py文件会被覆盖
    for p in dir(objs):
        if p.startswith("__"):
            continue
            
        # if not p.lower().startswith("publish"):
            #logging.debug("mqtt producer [%s] load fail. it must been start with 'publish'" % p)
        #    continue
        
        if not hasattr(getattr(objs, p), "topic"):
            continue
            
        logging.debug("mqtt producer [%s] register success!" % p)
        setattr(mqtt, p, getattr(objs, p)())
"""

    return auto_str + import_str


def get_mqtt_work_init():
    auto_str = """%s
import os
import re
import logging
dir_path = os.listdir(os.path.abspath(os.path.dirname(__file__)))
    """ % Copyright.file_pre

    import_str = """
hander_files = [x for x in dir_path if re.findall('[A-Za-z]\w+_worker\.py$', x)]

for hander_file in hander_files:
    model_name = hander_file[:-3]
    logging.debug("register mqtt workers [%s.py] success!" % model_name)
    __import__(model_name, globals(), locals(), [model_name], -1)

    """
    return auto_str + import_str

def get_celery_works_init(root_path, workers_path):
    """

    :param path:
    :return:
    """

    auto_str = """%s
import os
import re
import logging
from lcyframe.libs.singleton import CeleryCon
from lcyframe.libs.celery_route import Events
app = CeleryCon._app

dir_path = os.listdir(os.path.abspath(os.path.dirname(__file__)))
workers_path = "%s"
""" % (Copyright.file_pre, workers_path)

    import_str = """
hander_files = [x for x in dir_path if re.findall('[A-Za-z]\w+\.py$', x)]

for hander_file in hander_files:
    model_name = hander_file[:-3]
    if model_name == "__init__":
        continue

    model_name = workers_path.strip("/").replace("/", ".") + "." + model_name
    objs = __import__(model_name, fromlist=["*"])
    module_name = objs.__name__.split(".")[-1]

    setattr(Events, module_name, objs)

    for p in dir(objs):
        if p.startswith("__"):
            continue

        if type(getattr(objs, p)) == type:
            if not hasattr(getattr(objs, p), "queue"):
                continue

            if hasattr(app, p) and p != 'BaseEvent':
                raise Exception("exists same attribute：%s" % p)

        # logging.debug("celery task [%s] register success!" % p)
        setattr(Events, p, getattr(objs, p))

    setattr(app, Events.__name__, Events)

"""

    return auto_str + import_str