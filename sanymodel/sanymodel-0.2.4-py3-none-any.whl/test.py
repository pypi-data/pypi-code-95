#
from sanymodel.modeltools import ModelTool
#
t = ModelTool('Test', '1.0.0', '2021-01-01', '2021-02-01')
r = t.create_turbine_result('ALSFC', '001')
t.create_turbine_result('TYSFCB', '002')

print(t.results)
# print(t.get_result('TYSFCB', '002').add_fig('/tmp/1.png'))
# t.upload_results()

r.add_warning('有问题')
r.add_normal('还行')
r.add_error('坏事了！')
r.upload()
print(r.__dict__)


# r.upload()
# l = t.create_logger()
# l.info('b')
# l.upload()
# print(r.__dict__)

# t = Tag('测试', 'second', )
# # t.register(creator=None, description=None)
# t.register(creator='Tag', description='测试标签1')
# t.query()

# dt = datatools.DataTools()
# f = dt.get_files('localhost:50051', 'TYSFCB', 'second', '2021-01-01', '2021-01-02', '001')
# d = dt.get_data('localhost:50051', f, ['time', '风速1'])
# d['time'] = pd.to_datetime(d['time'])
# tag1 = d['风速1'] < 3
# tag1.index = d['time']
#
# bin = [5, 10, 20]
# tag2 = pd.cut(d['风速1'], bins=bin, labels=['小', '大'])
# tag2.index = d['time']
# tag2.to_pickle('/tmp/tag2.pkl')
#
# a = t.upload(tag2, 'ALSFC', '001')
# print(a)
#
# z = t.download( name='测试', data_type='second', start_time='2021-01-01', end_time='2021-01-01', wind_farm='ALSFC')
# print(z)
#
# tag3 = pd.read_pickle('/tmp/tag2.pkl')
#
# print(tag2[(tag2!='小') & (tag2!='大')])
#
# print(tag3.value_counts())


# print(tag1[tag1])
# print(tag1)
# print(d)
# s = pd

# Tag.upload()

# t = SensorErrorTag(field='轴1电机温度', name='变桨电机温度', data_type='second', usage='SensorError', creator='Tag',
#                    description='温度传感器异常的标签')
# t.register()
# print(t.query())
#
# dt = datatools.DataTools()
# f = dt.get_files('localhost:50051', 'TYSFCB', 'second', '2021-01-01', '2021-01-02', '001')
# d = dt.get_data('localhost:50051', f, ['time','轴1电机温度'])
#
# d['time'] = pd.to_datetime(d['time'])
# tag1 = d['轴1电机温度'] > 100
# tag1.index = d['time']
# print(tag1)
#
# t.upload(tag1, wind_farm= 'TYSFCB', turbine_num='001')
