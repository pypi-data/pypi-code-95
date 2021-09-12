"""
包括mysqlOperator一个类

Classes
----------
mysqlOperator: mysql数据库操作， 包括创建table、添加列、新增数据、更新数据、查询数据

Example
----------
>>> from commonMethods_zhaozl.toolbox.Method_mysqlOperator import mysqlOperator

"""

import pymysql  # PyMySQL==0.10.0
import pandas as pd  # pandas==1.1.0


class mysqlOperator:
	"""
	mysql数据库操作， 包括创建table、添加列、新增数据、更新数据、查询数据

	[1] 参数
	----------
	databaseName:
	    数据库名称，str，形如“bearing_pad_temper”
	tableName:
	    数据表名称，str，形如“轴承瓦温20200320_20200327_原始数据”
	host:
	    主机地址，str，optional， default， 'localhost'
	port:
	    主机端口，int，optional， default， 3306
	userID:
	    用户ID，str，optional， default， 'root'
	password:
	    密码，str，optional， default， '000000'

	[2] 示例1
	--------
	>>> databaseName = 'bearing_pad_temper'
	>>> tableName = '轴承瓦温20200320_20200327_原始数据'
	>>> host = 'localhost'
	>>> port = 3306
	>>> userID = 'root'
	>>> password = '000000'
	>>> obj = objectMySQL(databaseName=databaseName, tableName=tableName, host=host, port=port, userID=userID, password=password)
	>>> print(obj)
	"""
	def __init__(self, **kwargs):
		self.dataBaseName = kwargs['databaseName']
		self.tableName = kwargs['tableName']
		host = kwargs['host'] if 'host' in kwargs.keys() else 'localhost'
		port = kwargs['port'] if 'port' in kwargs.keys() else 3306
		userID = kwargs['userID'] if 'userID' in kwargs.keys() else 'root'
		password = kwargs['password'] if 'password' in kwargs.keys() else '000000'
		self.__con__ = pymysql.connect(host=host, port=port, db=self.dataBaseName, user=userID, passwd=password,
		                               charset='utf8mb4')
		self.__cur__ = self.__con__.cursor()

	def createTable(self, **kwargs):
		"""
		根据指定的tableName和columns创建dataTable

		:param kwargs: tableName: str, 表单名; columns: str, 列名+数据类型+缺省控制， 使用','隔开，字符串形如"test01 float null"
		:returns: None
		"""
		self.__cur__.execute('create table if not exists ' + kwargs['tableName'] + '(' + kwargs['columns'] + ')')
		self.__cur__.close()
		self.__con__.close()

	def addColumn(self, **kwargs):
		"""
		根据指定的tableName和column在已有数据表中添加列

        :param kwargs: tableName：表单名；column：初始列名、数据类型、缺省值，字符串形如"test02 float null"
        :returns: None
        """
		self.__cur__.execute(
			'alter table ' + self.dataBaseName + '.' + kwargs['tableName'] + ' add column ' + kwargs['column'])
		self.__cur__.close()
		self.__con__.close()

	def insertRow(self, **kwargs):
		"""
		根据指定的tableName和values在已有数据表中添加行

        :param kwargs: tableName：表单名；values：新增值，字符串形如'510, 512'
        :return: None
        """
		self.__cur__.execute('insert into ' + kwargs['tableName'] + ' value ' + '(' + kwargs['values'] + ')')
		self.__con__.commit()

	def updateValue(self, **kwargs):
		"""
		根据指定的tableName和targetColumn在已有数据表中更新已有数据

        :param kwargs: tableName：表单名；targetColumn：更新列名，字符串形如"test02'；value：更新值，字符串形如'110"
        :return: None
		"""
		com = 'update ' + self.dataBaseName + '.' + kwargs['tableName'] + ' set ' + kwargs['targetColumn'] + '=' + \
		      kwargs['value']
		self.__cur__.execute(com)
		self.__cur__.close()
		self.__con__.close()

	def selectData(self, **kwargs):
		"""
		根据查询数据的条件condition（控制时间）和content（所需查询的测点名称，使用','分隔）

        :param kwargs: content: 需要调用的列名，str，默认为查询数据的样本数"count(*)"，形如”'汽机润滑油冷油器出口总管油温1,发电机励端轴瓦温度'“; condition: 调用数据的条件，str，默认为全部数据，形如“'(时间戳>=\'2020-03-20 16:18:03\') and (时间戳<=\'2020-03-20 16:18:11\')'”
        :return: dataframe, 调取的数据
		>>> content = '汽机润滑油冷油器出口总管油温1,发电机励端轴瓦温度'
		>>> condition = "(时间戳>=\'2020-03-20 16:18:03\') and (时间戳<=\'2020-03-20 16:18:11\')"
        >>> obj = objectMySQL(databaseName='bearing_pad_temper', tableName='轴承瓦温20200320_20200327_原始数据')
        >>> data = obj.selectData(content=content, condition=condition)
        >>> print(data)
        """
		condition = kwargs['condition'] if 'condition' in kwargs.keys() else False
		content = kwargs['content'] if 'content' in kwargs.keys() else 'count(*)'
		if condition:
			com = 'select ' + content + ' from ' + self.dataBaseName + '.' + self.tableName + ' where ' + kwargs[
				'condition']
		else:
			com = 'select ' + content + ' from ' + self.dataBaseName + '.' + self.tableName
		self.__cur__.execute(com)
		res = self.__cur__.fetchall()
		self.__cur__.close()
		self.__con__.close()
		if content != 'count(*)':
			res = pd.DataFrame(res, columns=content.split(","))
		else:
			res = pd.DataFrame({'inspectedDataSize': [res[0][0]]})
		return res