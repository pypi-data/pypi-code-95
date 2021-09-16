import pandas as pd
import sqlite3
import psycopg2
import re
import datetime
import pymysql
pymysql.install_as_MySQLdb()
from sqlalchemy import create_engine
import tushare as ts
ts.set_token('46304a165e1a71a0ff4ffaaa9c3da977498c1d1c918c798322ffe6b1')
pro = ts.pro_api()

class DbHandle:
    def __init__(self, db_name, engine='sqlite3'):
        self.engine = engine
        self.db_name = db_name

    # 每次访问数据库新建连接，访问数据库结束后关闭连接，防止一些BUG的发生
    def establish_connection(self):
        if self.engine.lower() == 'postgresql':
            return psycopg2.connect(host='localhost', user='postgres', password='lzg000', database=self.db_name)
        elif self.engine.lower() == 'sqlite3':
            return sqlite3.connect(self.db_name)
        elif self.engine.lower() == 'mysql':
            return create_engine('mysql://root:abc123@192.168.0.252/' + self.db_name + '?charset=utf8').connect()

    # 存进表的通用接口
    def to_db(self, df, table_name, start=None, end=None, datetime_index='date'):
        # 防止字符串日期无法识别报错
        try:
            if start:
                df = df[(df[datetime_index] >= start)]
            elif end:
                df = df[(df[datetime_index] <= end)]
        except:
            if start:
                df = df[(df[datetime_index] >= datetime.datetime.strptime(start, '%Y-%m-%d'))]
            elif end:
                df = df[(df[datetime_index] <= datetime.datetime.strptime(end, '%Y-%m-%d'))]
        db_conn = self.establish_connection()
        df.to_sql(table_name, con=db_conn, if_exists='append', index=False)
        db_conn.close()


    #判断表是否存在，防止把表顶掉
    def table_exists(self, table_name):
        db_conn = self.establish_connection()
        db_cursor = db_conn.cursor()
        # 这个函数用来判断表是否存在
        sql = "select name from sqlite_master where type='table' order by name"
        db_cursor.execute(sql)
        tables = [db_cursor.fetchall()]
        table_list = re.findall('(\'.*?\')', str(tables))
        table_list = [re.sub("'", '', each) for each in table_list]
        db_conn.close()
        if table_name in table_list:
            return True
        else:
            return False
        
    def create_table(self, table_config_dict):
        table_name_str = table_config_dict['table_name']
        drop_str = "DROP TABLE IF EXISTS " + table_name_str + ";"
        create_str = " CREATE TABLE  IF NOT EXISTS " + table_name_str + " ("
        for col, attribute in table_config_dict['cols_attribute'].items():
            create_str += col + ' ' + attribute + ', '
        create_str = create_str[:-2]
        if table_config_dict['primary_key']:
            create_str += ', primary key ('
            for col in table_config_dict['primary_key']:
                create_str += col+', '
            create_str = create_str[:-2]+')'
        create_str += ');'

        if table_config_dict['unique_index']:
            if self.engine.lower() == 'mysql':
                unique_index_str = "CREATE UNIQUE INDEX uq_" + table_name_str.split('.')[-1] + " ON  " + table_name_str + " ("
                for col in table_config_dict['unique_index']:
                    unique_index_str += col + ' ASC,'
                unique_index_str = unique_index_str[:-1] + ");"
            else:
                unique_index_str = "CREATE UNIQUE INDEX 'uq_" + table_name_str.split('.')[-1] + "' ON  `" + table_name_str + "` ("
                for col in table_config_dict['unique_index']:
                    unique_index_str += "'" + col + "'" + ' ASC,'
                unique_index_str = unique_index_str[:-1] + ");"

        db_conn = self.establish_connection()
        db_cursor = db_conn.cursor() if self.engine.lower() != 'mysql' else db_conn
        db_cursor.execute(drop_str)
        db_cursor.execute(create_str)
        if table_config_dict['unique_index']: db_cursor.execute(unique_index_str)
        if self.engine.lower() != 'mysql': db_conn.commit()
        db_conn.close()

    # 得到建表的json
    def get_table_config(self,
                         df,
                         table_name_str,
                         code_col='code',
                         date_col='date',
                         datetime_col='datetime',
                         unique_index=None,
                         primary_key=None,
                         id=False):
        table_config_dict = {'table_name': str(), 'cols_attribute': {},
                             'unique_index': []}
        if id:table_config_dict['ID'] = "INTEGER PRIMARY KEY " + 'auto_increment' if self.engine.lower() == 'mysql' else 'AUTOINCREMENT'
        table_config_dict['table_name'] = table_name_str
        table_config_dict['unique_index'] = unique_index
        table_config_dict['primary_key'] = primary_key
        for col in df.columns:
            if col == code_col:
                table_config_dict['cols_attribute'][col] = 'INTEGER NOT NULL'
            elif col == date_col:
                table_config_dict['cols_attribute'][col] = 'DATE NOT NULL'
            elif col == datetime_col:
                table_config_dict['cols_attribute'][col] = 'DATETIME NOT NULL'
            elif col == 'time':
                table_config_dict['cols_attribute'][col] = 'TIME NOT NULL'
            else:
                table_config_dict['cols_attribute'][col] = 'FLOAT'
        return table_config_dict

    def get_update_time_frame(self, table_name, datetime_index='datetime'):
        con = self.establish_connection()
        df = pd.read_sql('select max('+datetime_index+') from '+table_name+' order by datetime limit 4300', con=con)
        con.close()
        max_date = str(df.values[0, 0]).split('T')[0]
        dates = self.cal_date(max_date, '2030-01-01', period='D', dtype='str')
        start = dates[dates.index(max_date) + 1]
        now = datetime.datetime.now()
        end = str(now.date())
        if now.time().hour <= 15: end = dates[dates.index(end) - 1]; print('未到收盘点，使用昨日数据更新')
        assert end >= start, '无可更新数据'
        return start, end

    def read_db(self,
                start,
                end,
                period='D',
                fields='*',
                code=None,
                table_name_str='fundamentals',
                datetime_index='date',
                code_col = 'code',
                dates = None,
                opening=False):
        '''
        :param start: 开始日期，例如'2018-01-01'
        :param end: 结束日期
        :param fields: 列，例如['amoflow', 'code']
        :param code: 代码，三种方式，①'000001' ②['000001', '000002'] ③不传默认取所有
        :return: dataframe
        '''
        fields = ''.join([x + ',' for x in fields]).strip(',')
        table_name_str = table_name_str
        datetime_index = datetime_index

        # 根据不同周期生成不同sql语句
        if dates:
            dates_sql = '(' + ','.join(map(lambda x: "'" + x + "'", dates)) + ')'
            datetime_sql = datetime_index + " in " + dates_sql
        else:
            if period.upper() == 'D':
                datetime_sql = datetime_index + " >='" + start + "' and " + datetime_index + " <= '" + end + "'"
            else:
                if period.upper() == 'W':
                    cal_dates = self.cal_date(start, end, period='W', dtype='str', opening=opening)

                elif period.upper() == 'M':
                    cal_dates = self.cal_date(start, end, period='M', dtype='str', opening=opening)

                cal_dates_sql = '(' + ','.join(map(lambda x: "'" + x + "'", cal_dates)) + ')'
                datetime_sql = datetime_index + " in " + cal_dates_sql

        # 如果指定了股票代码，则取出指定的数据，默认取出所有数据
        if code:
            if isinstance(code, list):
                code = '(' + ','.join(map(lambda x: str(int(x)), code)) + ')'
                code_sql = 'in ' + code
            else:
                code_sql = '= ' + code

            str_sql = "select " + fields + " from " + table_name_str + " where " + code_col + " " + code_sql + " and " + datetime_sql
        else:
            str_sql = 'select ' + fields + ' from ' + table_name_str + " where " + datetime_sql
        conn = self.establish_connection()
        df = pd.read_sql(str_sql, con=conn)
        conn.close()
        print(str_sql)
        return df

    def cal_date(self, start, end, period, dtype='str', opening=False):
        # 修正时间字符串格式
        start = start.replace('-', '')
        end = end.replace('-', '')
        # 取交易日历
        df = pro.query('trade_cal', start_date=start, end_date=end)
        df_d = df[df.is_open == 1]
        df_d.set_index(pd.to_datetime(df_d['cal_date'], format='%Y%m%d'), inplace=True)
        # 判断周期
        if period == 'D':
            cal_dates = df_d['cal_date']
        elif period == 'W':
            df_w = df_d.resample('W').agg({'cal_date': 'last' if not opening else 'first'})
            cal_dates = df_w['cal_date']
        elif period == 'M':
            df_m = df_d.resample('M').agg({'cal_date': 'last' if not opening else 'first'})
            cal_dates = df_m['cal_date']
        # 删除空值
        cal_dates.dropna(inplace=True)
        # 判断返回类型
        if dtype == 'str':
            cal_dates = cal_dates.astype(str).apply(lambda x: x[:4] + '-' + x[4:6] + '-' + x[                                                                       6:]).tolist()  # .index.to_series().dt.strftime('%Y-%m-%d').tolist()
        elif dtype == 'dt':
            cal_dates = pd.to_datetime(cal_dates, format='%Y%m%d').dt.date.tolist()
        return cal_dates

    def check_time(self, time):
        """
        :param time: 需要转换为YYYY-mm-dd格式str的日期，支持格式datetime.date, datetime.datetime, str, int

        :return: YYYY-mm-dd格式str的日期.
        """

        if isinstance(time, int):
            if 19000000 < time:
                time = str(time)
                str_time = time[0:4] + '-' + time[4:6] + '-' + time[6:]
            else:
                raise ValueError('数值型start,time必须为8位数int,如20180808,当前输入:{}'.format(time))
        elif isinstance(time, str):
            if len(time) == 10:
                time = datetime.datetime.strptime(time, '%Y-%m-%d')
            elif len(time) == 8:
                time = datetime.datetime.strptime(time, '%Y%m%d')
            elif len(time) == 19:
                time = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
            else:
                raise ValueError('输入str类型时间仅支持"2010-08-08"或"20100808"')
            str_time = time.strftime('%Y-%m-%d')

        elif isinstance(time, (datetime.datetime, datetime.date)):
            try:
                str_time = time.strftime('%Y-%m-%d')
            except ValueError:
                raise ValueError('datetime型start,time必须符合YYYY-MM-DD hh:mm:ss,如2018-08-08 00:00:00')
        else:
            raise ValueError('时间格式错误:{}'.format(time))
        return str_time

    @staticmethod
    def check_df_cols(newcols, dfcols):
        if newcols is not None:
            check_df_cols = [x for x in newcols.keys() if x not in dfcols]
            if len(check_df_cols) > 0:
                raise ValueError('输入的newcols含有df_data列索引以外的字段{}'.format(check_df_cols))

    @staticmethod
    def check_exist_col(dbpath, tablename, newcols, dfcols, con, autoadd=False):
        if newcols is None and not autoadd:
            return dict(), []
        try:
            cols = pd.read_sql('PRAGMA table_info([' + tablename + '])', con=con)['name'].to_list()
        except Exception as e:
            raise Exception('数据库查询表{}字段时发生异常'.format(tablename), e)
        true_newcols = dict()
        if newcols is not None and autoadd:
            autocols = {x: '' for x in dfcols if x not in list(newcols.keys()) + cols}
            for col in newcols.keys():
                if col not in cols:
                    true_newcols[col] = newcols[col]
            for col in autocols.keys():
                true_newcols[col] = ''
            return true_newcols, []
        elif newcols is None and autoadd:
            autocols = {x: '' for x in dfcols if x not in cols}
            for col in autocols.keys():
                true_newcols[col] = ''
            return true_newcols, []
        elif newcols is not None and not autoadd:
            autocols = [x for x in dfcols if x not in list(newcols.keys()) + cols]
            for col in newcols.keys():
                if col not in cols:
                    true_newcols[col] = newcols[col]
            return true_newcols, autocols

    @staticmethod
    def check_update_col(dbpath, tablename, dfcols, con, updatecols=None):
        assert isinstance(updatecols, list) or updatecols is None, 'updatecols必须是list或None'
        try:
            # cols = pd.read_sql('PRAGMA table_info([' + tablename + '])', con=con)['name'].to_list()
            cols = pd.read_sql('show full columns from ' + tablename, con=con)['Field'].tolist()
        except Exception as e:
            raise Exception('数据库查询表{}字段时发生异常'.format(tablename), e)
        if updatecols is not None:
            errorcols = [x for x in updatecols if x not in dfcols or x not in cols or x in ['date', 'datetime', 'code']]
            if len(errorcols) > 0:
                raise Exception('更新列中包含表{0}没有的列{1}或包含了code,date,datetime'.format(tablename, errorcols))
            true_updatecols = updatecols
        else:
            true_updatecols = [x for x in dfcols if x in cols and x not in ['date', 'datetime', 'code']]
        return true_updatecols

    @staticmethod
    def update_creat_update_data(dbpath, df_data, index_col, con):
        df_data.to_sql('update_data', con=con, if_exists='replace', index=False)

        conn_cursor = con  # .cursor()
        try:
            conn_cursor.execute('CREATE INDEX inx_update on update_data(' + index_col + ')')
        # con.commit()
        except Exception as e:
            print('update临时表创建索引失败，更新速度会下降，但不影响流程', e)

    @staticmethod
    def update_set_col(dbpath, tablename, newcols, con):
        if len(newcols) == 0:
            return
        conn_cursor = con.cursor()
        conn_cursor.execute("BEGIN TRANSACTION")  # 事务开启
        try:
            for col in newcols.keys():
                conn_cursor.execute('ALTER TABLE ' + tablename + ' ADD COLUMN ' + f"'{col}'" + ' ' + newcols[col])
            con.commit()  # 智能提交模式
        except Exception as e:
            raise Exception('方法update_set_col执行数据库增列失败，请联系管理员调试', e)
        conn_cursor.close()

    @staticmethod
    def drop_update_data(dbpath, con):
        conn_cursor = con  # .cursor()
        try:
            conn_cursor.execute('DROP TABLE update_data')
        # con.commit()
        except:
            print(
                '删除{}库中update_data失败, 请手动删除，(删除与否不影响程序运行，仅影响库所占内存，update为多余表)'.format(dbpath))

    def update_data(
            self, tablename, index_col, df_data, dbpath=None, con=None, newcols=None, autoadd=False, updatecols=None):
        """
        :param dbpath:数据库文件目录，str，如:D:/test/dbpath_tushare_data.sqlite3
        :param tablename: 数据库内所需要使用的某一个表的表名，str，如ts_day_data
        :param newcols: 新增列，支持dict，如{'pe': 'float', 'pb': 'float', 'eps': 'float'},默认False
        :param index_col: 所需要更改的数据库的唯一索引组合，str,如股票日级别：'code,date',分钟级别'code,datetime'，少数无code
        表如市场表为'date'或'datetime',不接受不含有时间的索引，此类表为截面表，请使用replace_data方法
        :param df_data: 用于添加进数据库的dataframe数据，字段必须含有index_col中的索引
        :param con: 连接，同pandas.read_sql的con参数，有则使用连接，无则必须保证dbpath有输入
        :param autoadd: 自动添dataframe加多余列，采取默认的sqlite格式，默认False,为True时若newcols不为None则剩余列执行autoadd
        :param updatecols: 指定更新的某些数据库已有列，接受list，默认None为更新传入dataframe中除索引外所有在数据库表里的列，
        否则更新传入的list中列
        """

        assert len(df_data.columns.unique()) == len(df_data.columns), 'df_data不能含有重复列'
        assert isinstance(tablename, str), 'tablename必须为str'
        assert isinstance(dbpath, str) or dbpath is None, 'dbpath必须为str或None'
        assert isinstance(df_data, pd.DataFrame), 'df_data必须为dataframe'
        assert isinstance(newcols, dict) or newcols is None, 'newcol为dict或None'
        # assert isinstance(con, sqlite3.Connection) or con is None, 'con为有效sqlite连接或None'

        conn = con
        self.check_df_cols(newcols=newcols, dfcols=df_data.columns)
        true_newcols, dropcols = self.check_exist_col(
            dbpath=dbpath, tablename=tablename, newcols=newcols, autoadd=autoadd, dfcols=df_data.to_dict(), con=conn)
        if len(dropcols) > 0:
            df_data = df_data.drop(dropcols, axis=1).copy(deep=True)
        true_updatecols = self.check_update_col(
            dbpath=dbpath, tablename=tablename, dfcols=df_data.to_dict(), updatecols=updatecols, con=conn)
        self.update_creat_update_data(dbpath=dbpath, df_data=df_data, index_col=index_col, con=conn)
        self.update_set_col(dbpath=dbpath, tablename=tablename, newcols=true_newcols, con=conn)  # 添加更新库中表没有列名

        conn_cursor = conn
        conn_cursor.execute("START TRANSACTION;")  # 事务开启
        true_updatecol = list(true_newcols.keys()) + true_updatecols
        set_sql = ' set '
        for col in true_updatecol:
            set_sql += tablename + '.' + col + '= update_data.' + col
            if col != true_updatecol[-1]: set_sql += ','
        where_sql = ' where '
        index_col_list = index_col.split(',')
        for col in index_col_list:
            where_sql += tablename + '.' + col + ' = update_data.' + col
            if col != index_col_list[-1]: where_sql += ' and '
        str_sql = 'update ' + tablename + ',update_data' + set_sql + where_sql
        # str_sql = 'update barralevel3, update_data set barralevel3.R_revision_ratio = update_data.R_revision_ratio where barralevel3.code = update_data.code and barralevel3.datetime = update_data.datetime'

        conn_cursor.execute(str_sql)
        # conn.commit()
        self.drop_update_data(dbpath=dbpath, con=conn)
        conn_cursor.close()
        print(tablename + '表update成功')

class DbFactor(DbHandle):
    def __init__(self, engine, db_name='factor'):
        super().__init__(engine=engine, db_name=db_name)

    #把dateframe存入表factor_short_day
    def todb_factor_short(self, df, period, start=None, end=None):
        if period == 'D':
            self.to_db(df, 'factor_short_day', start=start, end=end)
        elif period == '30m':
            self.to_db(df, 'factor_short_30m', start=start, end=end)

    #读取短线因子表
    def read_factor_short(self, start, end, period, fields='*', code = None):
        '''
        :param start: 开始日期，例如'2018-01-01'
        :param end: 结束日期
        :param period: 周期，1m, 5m, 15m, 30m, D, W, M, Y
        :param fields: 列，例如['amoflow', 'code']
        :param code: 代码，三种方式，①'000001' ②['000001', '000002'] ③不传默认取所有
        :return: dataframe
        '''
        fields = ''.join([x + ',' for x in fields]).strip(',')
        table_basic_name = 'factor_short'
        if period == 'D':
            table_name_str = table_basic_name + '_' + 'day'
            datetime_index = 'date'
        elif period == '30m':
            table_name_str = table_basic_name + '_' + '30m'
            datetime_index = 'datetime'
        #如果指定了股票代码，则取出指定的数据，默认取出所有数据
        if code:
            if isinstance(code, list):
                code = '(' + ','.join(map(lambda x: str(int(x)), code)) + ')'
                str_sql = "select " + fields + " from " + table_name_str + " where code in " + code + " and "+datetime_index+" >='"  + start + "' and "+datetime_index+" <= '" + end + "'"

            else:
                str_sql = "select " + fields + " from " + table_name_str + " where code = '" + code + "' and "+datetime_index+" >='"  + start + "' and "+datetime_index+" <= '" + end + "'"
        else:
            str_sql = 'select ' + fields + ' from ' + table_name_str + " where "+datetime_index+" >='"  + start + "' and "+datetime_index+" <= '" + end + "'"
        conn = self.establish_connection()
        if fields == '*':
            df = pd.read_sql(str_sql, con = conn, index_col='ID')
        else:
            df = pd.read_sql(str_sql, con = conn)
        conn.close()
        print(str_sql)
        return df

class FundamentalsFactor(DbHandle):
    def __init__(self, engine='sqlite3', db_name=r'C:\数据库\Sqlite\database\L1_fundamentals.sqlite3'):
        super().__init__(engine=engine, db_name=db_name)

    #把dateframe存入表factor_short_day
    def todb_fundamentals(self, df, start=None, end=None):
            self.to_db(df, 'fundamentals', start=start, end=end)

    def read_factor(self, start, end, period = 'M', fields='*', code = None, table_name_str='fundamentals', datetime_index='date'):
        '''
        :param start: 开始日期，例如'2018-01-01'
        :param end: 结束日期
        :param fields: 列，例如['amoflow', 'code']
        :param code: 代码，三种方式，①'000001' ②['000001', '000002'] ③不传默认取所有
        :return: dataframe
        '''
        if isinstance(fields, str):
            fields = fields.strip(',')
        else:
            fields = ''.join([x + ',' for x in fields]).strip(',')
        table_name_str = table_name_str
        datetime_index = datetime_index

        #根据不同周期生成不同sql语句
        if period == 'D':
            datetime_sql = datetime_index+" >='"  + start + "' and "+datetime_index+" <= '" + end + "'"
        else:
            if period == 'W':
                cal_dates = self.cal_date(start, end, period='W', dtype='str')

            elif period == 'M':
                cal_dates = self.cal_date(start, end, period='M', dtype='str')

            cal_dates_sql = '(' + ','.join(map(lambda x: "'" + x + "'", cal_dates)) + ')'
            datetime_sql = datetime_index + " in " + cal_dates_sql

        #如果指定了股票代码，则取出指定的数据，默认取出所有数据
        if code:
            if isinstance(code, list):
                code = '(' + ','.join(map(lambda x: str(int(x)), code)) + ')'
                code_sql = 'in ' + code
            else:
                code_sql = '= ' + code

            str_sql = "select " + fields + " from " + table_name_str + " where code " + code_sql + " and " + datetime_sql
        else:
            str_sql = 'select ' + fields + ' from ' + table_name_str + " where " + datetime_sql
        conn = self.establish_connection()
        # if fields == '*':
        #     df = pd.read_sql(str_sql, con = conn, index_col='ID')
        # else:
        df = pd.read_sql(str_sql, con = conn)
        conn.close()
        print(str_sql)
        return df

class MktHandle(DbHandle):
    def __init__(self, engine='sqlite3', db_name=r'C:\数据库\Sqlite\database\L1_tushare_data.sqlite3'):
        super().__init__(engine=engine, db_name=db_name)

    def fq(self, df, target_cols=['open', 'high', 'low', 'close'], adj='qfq'):
        '''
        :param df: 行情数据df，带有复权因子列adj_factor
        :param target_cols: 要复权的列
        :return:
        '''
        now_adj = df['adj_factor'].iat[-1] if adj=='qfq' else df['adj_factor'].iat[0]
        df.loc[:, target_cols] = df[target_cols].mul(df['adj_factor'], axis=0) / now_adj
        return df

    def read_day(self, start, end, period='D', fields='*', code=None, table_name_str='ts_day_data',
                    datetime_index='date', adj='qfq'):

        start = self.check_time(start)
        end = self.check_time(end)

        if adj and 'adj_factor' not in fields and fields!= '*': fields.append('adj_factor')

        df = self.read_db(start, end, period=period, fields=fields, code=code, table_name_str=table_name_str,
                    datetime_index=datetime_index)
        if adj:
            target_cols = [x for x in fields if x in ['open', 'high', 'low', 'close']]
            df = df.groupby('code').apply(lambda x: self.fq(x, target_cols=target_cols, adj=adj))  # 前复权
            df = df[df.columns.difference(['adj_factor'])]
        return df

if __name__ == '__main__':

    df = pd.read_csv(r'D:\work\LZG\scrapy_spider\wencai\test.csv')
    d = DbHandle(db_name='wencai.sqlite3')
    table_config = d.get_table_config(df,
                                      table_name_str='weicai_socore',
                                      primary_key=['ticker', 'datetime'],
                                      code_col='ticker',
                                      unique_index=['ticker','datetime'])
    d.create_table(table_config)

    #初始化一个factor数据库管理对象
    #%%
    # d = FundamentalsFactor(engine='sqlite3')
    #入库
    # df = pd.read_csv('fundamentals.csv')
    # df_val = df[['code', 'date', '']]
    # d.todb_fundamentals(df)
    # #从库里取数据
    # df = d.read_factor(start = '2018-11-01', end = '2019-12-01', period='W')

    # #建表
    # table_config_dict = d.get_table_config('fundamentals.csv')
    # d.create_table(table_config_dict)
    # #入库
    # df = pd.read_csv('fundamentals.csv')
    # df.drop_duplicates(['code', 'date'], inplace=True)
    # d.todb_fundamentals(df)

