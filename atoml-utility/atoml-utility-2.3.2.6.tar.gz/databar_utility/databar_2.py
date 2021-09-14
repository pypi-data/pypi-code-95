import pandas as pd
import numpy as np

from general_utility import utils as us
from general_utility.appbase import ab

class Databar_Pro(object):
    def __init__(self, **kwargs):
        pass

class Databar_Pro_2_2(Databar_Pro):
    def __init__(self, **kwargs):
        self.params = us.check_attribute(kwargs, 'params', None)
        if not isinstance(self.params, dict):
            self.params = us.str_to_dict(self.params, ",", ":")

        self.values = {}
        input = us.check_attribute(kwargs, 'input', None)
        if (input is not None):
            self.load(input)

    def param(self, key, default = None):
        return us.check_attribute(self.params, key, default)

    ####################################################################

    def add(self, data = None):
        if (data is None):
            return False, None

        for (K, V) in data.items():
            values = us.check_attribute(self.values, K, {})
            if ('databar' in K.lower()):
                value = us.check_attribute(values, K, [])
                for databar in V:
                    value.append(databar[K])
                self.values[K] = value
            else:
                self.values[K] = V
        
        return True, self.serializes()

    def serializes(self, data = None):
        if (data is None):
            data = self.values
        
        result = {}
        if (isinstance(data, dict)):
            for (K, V) in data.items():
                if (isinstance(V, list)):
                    for item in V:
                        item_serializes = us.check_attribute(result, K, [])
                        if (hasattr(item, 'serialize')): # 复数序列化
                            item_serializes.append(item.serialize())

                        result[K] = item_serializes
                elif (isinstance(V, dict)):
                    result[K] = us.dict_copy(V, '*', '')
                else:
                    result[K] = V
        elif (isinstance(data, list)):
            result['values'] = data

        return result

    ####################################################################

    def load(self, databars):
        if (databars is None):
            return False

        if (isinstance(databars, list)):
            for item in databars:
                self.load(item) # 循环添加
            return True

        if (not isinstance(databars, dict)):
            return False

        df = None
        index_field = None
        strategy_type = None
                    
        ab.print_log('-------------------------------------------------------')
        ab.print_log("load databars: %s" % databars)

        if (us.att_isin(databars, 'date_range')):
            date_range = us.check_attribute(databars, 'date_range')
            """ 起始日期 """
            start_date = us.check_date(us.check_attribute(date_range, 'start_date'), "%Y%m%d")
            end_date = us.check_date(us.check_attribute(date_range, 'end_date'), "%Y%m%d")

            ab.print_log("start & end datetime: %s ~ %s" % (start_date, end_date))

        if (us.att_isin(databars, 'databarx')):
            databar = us.check_attribute(databars, 'databarx')
            databars['x'] = self.load_databar(databar, start_date, end_date)

        if (us.att_isin(databars, 'databary')):
            databar = us.check_attribute(databars, 'databary')
            databars['y'] = self.load_databar(databar, start_date, end_date)

        self.values = us.dict_merged(self.values, databars)

        return True
        
    def load_databar(self, databar, start_date = 'NOW', end_date = 'NOW'):
        params_list = 'time_step, random_seed, translation, train_data_rate, valid_data_rate, shuffle_train_data'

        dfs = None
        num = 0
        for item in databar:
            source_type = us.check_attribute(databar, 'source_type')
            source_pool = us.check_attribute(databar, 'source_pool')
            all_fields = us.check_attribute(databar, 'all_fields')
            index_field = us.check_attribute(databar, 'index_field')
            calc_field = us.check_attribute(databar, 'calc_field')
            strategy_type = us.check_attribute(databar, 'strategy_type')
            normalization = us.check_attribute(databar, 'normalization')
            
            df = None
            if ("file." in source_type): # 文件
                df = self.load_databar_from_csv(source_type, source_pool, all_fields, index_field, start_date, end_date)
                if (df is not None):
                    df = self.strategy(df, calc_field, strategy_type) # 数据预处理
            elif ("db." in source_type): # 数据库
                pass

            if (df is None) and (df.empty):
                continue

            # 更改标签名，避免合并的时候丢失数据
            for field in us.params_split(calc_field, ','):
                df = df.rename(columns={field: field + '_' + str(num)})

            num = num + 1

            if (dfs is not None):
                dfs = pd.merge(dfs, df, on = index_field).sort_values(by = index_field)
            else:
                dfs = df.sort_values(by = index_field)

        if ((index_field != None) and (index_field.lower() != 'null')):
            dfs = dfs.drop(index_field, axis=1) # 删除索引列

        if (dfs is not None):
            ab.print_log(dfs.head(3))
            ab.print_log('.........')
            ab.print_log(dfs.tail(3))
            ab.print_log('-------------------------------------------------------')

        result = us.dict_copy(self.params, params_list, '')
        result['columns'] = dfs.columns.tolist()
        dfs = dfs.values # 训练数据集合

        if (dfs is not None) and (normalization): # 归一化
            # 数据的均值和方差
            result['mean'] = np.mean(dfs, axis= 0)
            result['std'] = np.std(dfs, axis = 0)

            result['values'] = (dfs - result['mean']) / result['std'] # 归一化，去量纲
        else:
            result['values'] = dfs

        train_data_rate = float(us.check_attribute(result, 'train_data_rate', 1)) # 训练数据的比例
        result['data_num'] = dfs.shape[0] # 总的数据量
        result['train_num'] = int(result['data_num'] * train_data_rate) # 参与训练的数据量
        result['test_num'] = result['data_num'] - result['train_num'] # 参与测试的数据量

        result['sample_interval'] = min(result['test_num'], int(result['time_step'])) # 步长,也就是根据多久的数据进行预测(为了防止time_step大于测试集数量,一般都会为time_step值
        result['start_num_in_test'] = result['test_num'] % result['sample_interval'] # 这些天的数据不够一个sample_interval
        result['time_step_size'] = result['test_num'] // result['sample_interval'] # 根据测试步长得出的测试预测结果数量

        return result

    def load_databar_from_csv(self, source_type, source_pool, all_fields, index_field, start_date, end_date):
        if ('.csv' not in source_type.lower()):
            return None

        filepath = source_pool # 这里只做了单文件处理
        if (us.path_exists(filepath) == False):
            filepath = us.make_param(filepath, None)
            if (us.path_exists(filepath) == False):
                return None

        df = pd.read_csv(filepath, nrows = 1)

        columns = []
        if (all_fields.lower() == 'all') or (all_fields == '*'):
            columns = df.columns.values.tolist()
        else:
            fields_list = us.params_split(all_fields, ',')
            for field in fields_list:
                if field[0] == '-': # 判断是白名单还是黑名单
                    if (len(columns) <= 0):
                        columns = df.columns.values.tolist()
                    columns.remove(field[1:])
                else:
                    columns.append(field)

        df = pd.read_csv(filepath, usecols = columns)
        # if ('date' in columns): # 时间筛选，目前还有问题，先注释5
        #     df = df.loc[(df['date'] >= start_date) & (df['date'] <= end_date)]

        if ((index_field != None) and (index_field.lower() != 'null')):
            df.set_index(index_field)

        return df

    def strategy(self, df, calc_field, strategy_type):
        if (df is None) and (strategy_type is None): # 这里如果设置了策略类型，则需要进行数据再加工处理
            return df

        result_field = []
        calc_field = us.params_split(calc_field, ',') # 字符串转换为列表格式
        if (strategy_type.lower() == 'all'):
            result_field = [] # df.columns.tolist()
            pass # 直接返回所有
        else:
            if (strategy_type.lower() == 'single'):
                df[strategy_type] = df[calc_field]
                result_field.append(strategy_type)
            if (strategy_type.lower() == 'avg'):
                df[strategy_type] = df[calc_field].mean(axis=1)
                result_field.append(strategy_type)
            elif (strategy_type.lower() == 'sum'):
                df[strategy_type] = df[calc_field].sum(axis=1)
                result_field.append(strategy_type)
            
            df = df.drop(calc_field, axis=1) # 应为转换了，所以删除

        return df, result_field

    def get_values(self, **kwargs):

        ###############################################################################

        def get_train_data(values, name = '', islabel = False):
            if (name == ''):
                x = get_train_data(values, name = 'x')
                y = get_train_data(values, name = 'y', islabel = True)
                
                from sklearn.model_selection import train_test_split
                result = train_test_split(x, y, 
                            test_size = self.params['valid_data_rate'],
                            random_state = self.params['random_seed'],
                            shuffle = self.params['shuffle_train_data']) 

                return result
            
            values = us.check_attribute(values, name)

            train_data_rate = float(us.check_attribute(values, 'train_data_rate', 0.6))
            time_step = int(us.check_attribute(values, 'time_step', 20))
            translation = int(us.check_attribute(values, 'translation', 0))
            train_num = int(us.check_attribute(values, 'train_num', 1))

            result = us.check_attribute(values, 'values')
            
            if (islabel):
                result = result[translation : translation + train_num]
            else:
                result = result[:train_num]

            return np.array([result[i : i + time_step] for i in range(train_num - time_step)])

        ###############################################################################

        def get_test_data(values, name = '', islabel = False):
            if (name == ''):
                x = get_test_data(values, name = 'x')
                y = get_test_data(values, name = 'y', islabel = True)
                return x, y

            values = us.check_attribute(values, name)

            train_data_rate = us.check_attribute(values, 'train_data_rate', 0.6)
            time_step = us.check_attribute(values, 'time_step', 20)
            translation = us.check_attribute(values, 'translation', 0)
            train_num = us.check_attribute(values, 'train_num', 1)

            sample_interval = us.check_attribute(values, 'sample_interval', 0)
            start_num_in_test = us.check_attribute(values, 'start_num_in_test', 0)
            time_step_size = us.check_attribute(values, 'time_step_size', 0)

            result = us.check_attribute(values, 'values')
            result = result[int(train_num):]

            if (not islabel):
                result = [result[   int(start_num_in_test + i * sample_interval) : 
                                    int(start_num_in_test + (i + 1) * sample_interval)]
                            for i in range(int(time_step_size))]
            else:
                result = result[int(start_num_in_test):]

            return np.array(result)

        ###############################################################################

        def get_other(values, name = ''):
            if (name == ''):
                x = get_other(values, 'x')
                y = get_other(values, 'y')
                return x, y

            params_list = 'data_num, train_num, test_num, start_num_in_test, time_step_size, translation, mean, std, columns'

            return us.dict_copy(us.check_attribute(values, name), params_list, '')

        ###############################################################################

        if (self.values is None):
            return None

        type = us.check_attribute(kwargs, 'type', 'train')

        if (type.lower() == 'train'):
            x_train, x_valid, y_train, y_valid = get_train_data(self.values)

            ab.print_log('x_train shape: ')
            ab.print_log(x_train.shape)
            ab.print_log('x_valid shape: ')
            ab.print_log(x_valid.shape)
            ab.print_log('y_train shape: ')
            ab.print_log(y_train.shape)
            ab.print_log('y_valid shape: ')
            ab.print_log(y_valid.shape)
            ab.print_log('-------------------------------------------------------')

            return x_train, y_train, x_valid, y_valid
        elif (type.lower() == 'test'):
            x_test, y_test = get_test_data(self.values)

            ab.print_log('x_test shape: ')
            ab.print_log(x_test.shape)
            ab.print_log('y_test shape: ')
            ab.print_log(y_test.shape)
            ab.print_log('-------------------------------------------------------')

            return x_test, y_test

        elif (type.lower() == 'other'):

            return get_other(self.values)

        return None, None

# 2.3.1版本基本没变，主要是验证数据解析框架
class Databar_Pro_2_3_1(Databar_Pro_2_2):
    pass

# 2.3.2版本
class Databar_Pro_2_3_2_x(Databar_Pro_2_3_1):
    def __init__(self, **kwargs):
        self.params = us.check_attribute(kwargs, 'params', None)
        if (self.params is not None) and (not isinstance(self.params, dict)):
            self.params = us.str_to_dict(self.params, ",", ":")

        self.type = None # 2.3.2版本新增属性
        self.values = {}
        input = us.check_attribute(kwargs, 'input', None)
        if (input is not None):
            self.load(input)
    pass

    def load_databar_from_sql(self, input):
        link = us.make_param(us.check_attribute(input, "link", None), None)
        if (link is None):
            link = us.make_param("${DATABASE_URL_QUOTATION}", None)

        sql = us.check_attribute(input, "value", None)

        from sqlalchemy import create_engine
        db_engine = create_engine(link)
        if (db_engine is None):
            ab.print_log("create engine error!")
            return None

        try:
            df = pd.read_sql(sql = sql, con = db_engine)
        except Exception as e:
            print("e: ", e)
            return None

        return df

    def load_databar_from_csv(self, input):
        filepath = us.check_attribute(input, "filepath", "")
        if ('.csv' not in filepath.lower()):
            return None

        if (us.path_exists(filepath) == False):
            filepath = us.make_param(filepath, None)
            if (us.path_exists(filepath) == False):
                return None

        df = pd.read_csv(filepath) #, nrows=250)

        return df

    def load_single_input(self, inputs):
        result = None
        for input in inputs:
            type = us.check_attribute(input, "type", None)
            if (type.lower() == "db"):
                df = self.load_databar_from_sql(input)
            elif (type.lower() == "csv"):
                df = self.load_databar_from_csv(input)
            else:
                pass
            if (result is None):
                result = df
            else:
                df = result
                result = []
                result.append(df)
        
        return result

    def load(self, inputs):
        # 因为增加了对 sql_input 的支持,故单独列出来,原databar_input还是走原来的解析代码
        single_input = us.check_attribute(inputs, 'single_input', None)
        if (single_input is None):
            databar_input = us.check_attribute(inputs, 'databar_input', None)
            if (databar_input is not None):
                self.type = 'databar'
                return super().load(databar_input)
            else:
                return super().load(inputs)
        else:
            self.type = 'single'
            self.values = self.load_single_input(single_input)
            return True
            
    def load_databar(self, databar, start_date = 'NOW', end_date = 'NOW'):
        params_list = 'time_step, random_seed, translation, train_data_rate, valid_data_rate, shuffle_train_data'

        dfs = None
        num = 0
        for item in databar:
            type = us.check_attribute(item, 'type', None)

            link = us.check_attribute(item, 'link', None)
            value = us.check_attribute(item, 'value', None)

            index_field = us.check_attribute(item, 'index_field', None)
            calc_field = us.check_attribute(item, 'calc_field', None)
            strategy_type = us.check_attribute(item, 'strategy_type', None)
            normalization = us.check_attribute(item, 'normalization', None)

            if (type.lower() == 'db'):
                # 2.3.2 协议版本增加SQL输入类型
                df = self.load_databar_from_sql({"dblink": link, "sql": value})
                pass
            elif (type.lower() == 'file'):
                # 2.3.2更改为精简读取模式
                df = self.load_databar_from_csv({"filepath": value})
                # df.insert(0, 'ID', range(0, len(df)))
                # df.to_csv('./test.csv')

            if (df is None) and (df.empty):
                continue

            print(df.tail(3))
            df, strategy_field = self.strategy(df, calc_field, strategy_type) # 数据预处理

            # 更改数据集列名称，避免合并的时候丢失数据
            blacklist = False
            if (calc_field[0] == '-'):
                blacklist = True

            for field in df.columns:
                if ((',' + field) in calc_field) or ((field + ',') in calc_field):
                    if (blacklist == False):
                        # 白名单添加
                        df = df.rename(columns={field: field + '_' + str(num)})
                    else:
                        if (index_field.lower() != field.lower()): # 删除不需要的字段
                            df = df.drop(field, axis=1)
                else:
                    if (blacklist == True) or (calc_field.lower() == 'all'):
                        # 黑名单以外的添加
                        df = df.rename(columns={field: field + '_' + str(num)})
                    else:
                        if (index_field.lower() != field.lower()) and (field not in strategy_field): # 删除不需要的字段
                            df = df.drop(field, axis=1)

            num = num + 1

            if (dfs is not None):
                dfs = pd.merge(dfs, df, on = index_field).sort_values(by = index_field)
            else:
                dfs = df.sort_values(by = index_field)

        if (dfs is not None):
            ab.print_log(dfs.head(3))
            ab.print_log('.........')
            ab.print_log(dfs.tail(3))
            ab.print_log('-------------------------------------------------------')

        result = us.dict_copy(self.params, params_list, '')
        
        if ((index_field != None) and (index_field.lower() != 'null')):
            result['index'] = dfs[index_field].values
            dfs = dfs.drop(index_field, axis=1) # 删除索引列

        result['columns'] = dfs.columns.tolist()
        dfs = dfs.values # 训练数据集合

        if (dfs is not None) and (normalization): # 归一化
            # 数据的均值和方差
            result['mean'] = np.mean(dfs, axis= 0)
            result['std'] = np.std(dfs, axis = 0)

            result['values'] = (dfs - result['mean']) / result['std'] # 归一化，去量纲
        else:
            result['values'] = dfs

        train_data_rate = float(us.check_attribute(result, 'train_data_rate', 1)) # 训练数据的比例
        result['data_num'] = dfs.shape[0] # 总的数据量
        result['train_num'] = int(result['data_num'] * train_data_rate) # 参与训练的数据量
        result['test_num'] = result['data_num'] - result['train_num'] # 参与测试的数据量

        result['sample_interval'] = min(result['test_num'], int(result['time_step'])) # 步长,也就是根据多久的数据进行预测(为了防止time_step大于测试集数量,一般都会为time_step值)
        result['start_num_in_test'] = result['test_num'] % result['sample_interval'] # 这些天的数据不够一个sample_interval
        result['time_step_size'] = result['test_num'] // result['sample_interval'] # 根据测试步长得出的测试预测结果数量

        return result
        
    def get_type(self):
        return self.type.lower()

    def get_data(self, **kwargs):
        ###############################################################################
        
        def get_value(values, value_name = '', return_index = False):
            if (value_name == ''):
                # 递归返回
                x = get_value(values, value_name = 'x', return_index = return_index)
                y = get_value(values, value_name = 'y', return_index = return_index)
                return x, y

            ################################################

            # 原始值
            values = us.check_attribute(values, value_name)
            result_values = us.check_attribute(values, 'values')
            
            result_index = None
            if (return_index):
                result_index = us.check_attribute(values, 'index')

            # 各类参数
            train_num = int(us.check_attribute(values, 'train_num', 1))
            translation = us.check_attribute(values, 'translation', 0)

            if (value_name.lower() == "x"):
                # 特征数据
                result_values = result_values[: train_num]
                if (result_index is not None):
                    result_index = result_index[: train_num]
            else:
                 # 如果是标签数据集(Y)则进行平移,表示预测后N条的数据
                result_values = result_values[translation : translation + train_num]
                if (result_index is not None):
                    result_index = result_index[translation : translation + train_num]

            # 步进(time_step)平移值
            time_step = int(us.check_attribute(values, 'time_step', 20))

            if (result_index is not None):
                return  np.array([result_values[i : i + time_step] for i in range(train_num - time_step)]), \
                        np.array([result_index[i : i + time_step] for i in range(train_num - time_step)])

            return np.array([result_values[i : i + time_step] for i in range(train_num - time_step)])

        ###############################################################################

        def get_test_data(values, value_name = '', return_index = False):
            if (value_name == ''):
                x = get_test_data(values, value_name = 'x', return_index = return_index)
                y = get_test_data(values, value_name = 'y', return_index = return_index)
                return x, y

            values = us.check_attribute(values, value_name)
            train_num = us.check_attribute(values, 'train_num', 1)

            sample_interval = us.check_attribute(values, 'sample_interval', 0)
            start_num_in_test = us.check_attribute(values, 'start_num_in_test', 0)
            time_step_size = us.check_attribute(values, 'time_step_size', 0)

            result_values = us.check_attribute(values, 'values')
            result_values = result_values[int(train_num):]

            result_index = None
            if (return_index):
                result_index = us.check_attribute(values, 'index')
                result_index = result_index[int(train_num):]

            if (value_name.lower() == "x"):
                result_values = [result_values[   
                                    int(start_num_in_test + i * sample_interval) : 
                                    int(start_num_in_test + (i + 1) * sample_interval)]
                            for i in range(int(time_step_size))]

                if (result_index is not None):
                    result_index = [result_index[   
                                    int(start_num_in_test + i * sample_interval) : 
                                    int(start_num_in_test + (i + 1) * sample_interval)]
                            for i in range(int(time_step_size))]

            else:
                result_values = result_values[int(start_num_in_test):]

                if (result_index is not None):
                    result_index = result_index[int(start_num_in_test):]

            if (result_index is not None):
                return  np.array(result_values), \
                        np.array(result_index)

            return np.array(result_values)
            
        ###############################################################################

        def get_other(values, name = ''):
            if (name == ''):
                x = get_other(values, 'x')
                y = get_other(values, 'y')
                return x, y

            params_list = 'data_num, train_num, test_num, start_num_in_test, time_step_size, translation, mean, std, columns'

            return us.dict_copy(us.check_attribute(values, name), params_list, '')

        ###############################################################################

        if (self.values is None):
            return None

        type = us.check_attribute(kwargs, 'type', 'train')

        if (type.lower() == 'train'):
            X = {}
            Y = {}

            X['train'], Y['train'] = get_value(self.values, return_index = False) # 训练数据不需要索引
            
            ab.print_log('-------------------------------------------------------')
            '''
            # 使用sklean的数据分割,暂时不使用
            from sklearn.model_selection import train_test_split
            result = train_test_split(X['train'], Y['train'], 
                        test_size = self.params['valid_data_rate'],
                        random_state = self.params['random_seed'],
                        shuffle = self.params['shuffle_train_data'])
            X['train'], X['valid'], Y['train'], Y['valid'] = result
            ab.print_log('x value {:} valid {:}'.format(X['train'].shape, X['valid'].shape))
            ab.print_log('y value {:} valid {:}'.format(Y['train'].shape, Y['valid'].shape))
            '''
            return X, Y
        elif (type.lower() == 'test'):
            x = {}
            y = {}

            X, Y = get_test_data(self.values, return_index = True) # 测试数据需要索引,因为要做回测

            assert X[0].shape[0] == X[1].shape[0], 'X index and value count hava different!'
            assert Y[0].shape[0] == Y[1].shape[0], 'Y index and value count hava different!'

            x['value'], x['index'] = X
            y['value'], y['index'] = Y

            ab.print_log('x value {:} index {:}'.format(x['value'].shape, x['index'].shape))
            ab.print_log('y value {:} index {:}'.format(y['value'].shape, y['index'].shape))

            ab.print_log('-------------------------------------------------------')

            return x, y

        elif (type.lower() == 'other'):

            return get_other(self.values)

        elif (type.lower() == 'raw'):
            x = us.check_attribute(self.values, "x", None)
            y = us.check_attribute(self.values, "y", None)

            return x, y

        return None, None

    def get_values(self, **kwargs):
        if (self.get_type() == 'databar'):
            return self.get_data(**kwargs)

        elif (self.get_type() == 'single'):
            return self.values, None # sql类型输出是单数据集

        return None, None
