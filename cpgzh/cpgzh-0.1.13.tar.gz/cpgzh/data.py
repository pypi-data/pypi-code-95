import pickle
import time
import os


class Data:
    '数据存储类'

    def __init__(self, data_path) -> None:
        '数据类'
        self.status = 0  # 游戏状态\
        self.time = 0  # 游戏持续时间
        self.score = 0  # 得分
        self.start()
        self.data_path = data_path

    def start(self):
        '启动'
        self.__start = time.time()
        return self.__start

    def get_time(self):
        '获取游戏的持续时间'
        return time.time()-self.__start

    def save_data(self):
        '保存数据'
        try:
            with open(self.data_path, 'wb') as f:
                pickle.dump(self, f)
                print(f'{self.data_path}保存成功！')
                return 1
        except:
            print(f'{self.data_path}保存失败！')
            return 0

    def load_data(self):
        '加载数据'
        if os.path.isfile(self.data_path):
            with open(self.data_path, 'rb') as f:
                self = pickle.load(f)
                # print(f'{self.data_path}加载成功！')
                return 1
        else:
            # print(f'{self.data_path}加载失败！')
            #self = Data(self.data_path)
            return 0

    def del_data(self):
        '删除数据'
        try:
            os.remove(self.data_path)
            print(f'{self.data_path}删除成功')
            return 1
        except:
            print(f'{self.data_path}不存在')
            return 0
