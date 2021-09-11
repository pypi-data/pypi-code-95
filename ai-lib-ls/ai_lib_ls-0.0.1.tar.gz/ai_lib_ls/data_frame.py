"""
*@File    : data_frame.py
*@Time    :9/10/21 5:45 下午
*author:QauFue ,技术改变未来
*doc ：Dataframe 数据常见的操作
"""


class DataframeUtil():

    def __init__(self, df):
        df = df

    def df_head(self):
        '''查询面几行的数据'''
        self.df.head()

    def get_h_data(self, array_h):
        '''查询一列的数据'''
        self.df.reindex(columns=array_h)  # ['Sex', 'Age', 'Parch', 'Fare']

    def updata_data(self, key_str, value_str, update_value):
        '''将列中的数据修改替换

        key_str ：列的名称
        value_str ：列名称的参数值
        update_value：将列中的值修改为的值
        '''
        self.df.loc[self.df[key_str] == value_str] = update_value

if __name__ == '__main__':

    d=DataframeUtil()
    d.updata_data()