import pika
import pandas as pd
from dwhutils.ReadEntity import ReadEntity

p_date = '2018-12-31'
trans = ReadEntity(p_date=p_date, layer='biz', entity_name='transaktion').read_entity

konto = ReadEntity(p_date=p_date, layer='biz', entity_name='konto').read_entity

trans_konto = ReadEntity(p_date=p_date, layer='biz', entity_name='trans_konto').read_entity

data = trans.merge(trans_konto, how='inner', on='transaktion_hk').merge(konto, how='inner', on='konto_hk')
# data = data[data['konto_hk'] == '000209D4F9F396607D2A405977FB2743']
data['ausfuehrungsdatum'] = pd.to_datetime(data['ausfuehrungsdatum'])
data.set_index('ausfuehrungsdatum', inplace=True)

data.sort_index(inplace=True)



connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='q1')

channel.basic_publish(exchange='',routing_key='q1', body=data.to_json(orient='records'))
print(" [x] Sent 'Hello World!'")
connection.close()
