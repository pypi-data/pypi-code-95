import os, requests, json, logging, glob
from google.cloud import storage
from .utils import Utils
from .models.product import Product
from .models.order import Order
from .models.order_item import OrderItem


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(threadName)-11s %(levelname)-10s %(message)s")
server_url = 'https://connection.nappsolutions.io'
storage_client = storage.Client.from_service_account_json(f'{os.path.dirname(os.path.realpath(__file__))}/service-account.json')


class NappClient2Controller:
    @classmethod
    def get_integration(self, store_reference):
        if store_reference:
            r = requests.get(f'{server_url}/integration/store_id/{store_reference}')
            return json.loads(r.content.decode('utf-8'))
        else:
            logging.info('[NappClient2] Invalid store reference to get integration')
            return None


    @classmethod
    def create_event(self, status, event, stacktrace=None, total_orders=None, bucket=None):
        headers = dict()
        headers['Content-Type'] = 'application/json'
        
        payload = dict()
        payload['status'] = f'{status}'
        payload['file'] = f'{event}'
        payload['stacktrace'] = stacktrace 
        payload['total_orders'] = total_orders
        payload['bucket'] = bucket
        
        if status and event:
            response = requests.post(f'{server_url}/event/history', headers=headers, data=json.dumps(payload))
            logging.info(f"[NappClient2] Creating event {event} with status '{status}' - {response.status_code} {payload}")
        else:
            logging.info('[NappClient2] Invalid status or event, error to create event')
            return None
        
    
    @classmethod
    def save_files(self, output_path = '', products: Product = [], orders: Order = [], order_items: OrderItem = [], revision: int = 1, version: int = 1):
        csvs = glob.glob(f'{output_path}/*.csv')
        zips = glob.glob(f'{output_path}/*.zip')
        
        try:
            for file in csvs:
                os.remove(file)
        except:
            pass

        try:
            for file in zips:
                os.remove(file)
        except:
            pass
        
        if len(products) > 0:
            Utils.create_csv(f'{output_path}/products_r{revision}_v{version}.csv', products)
        if len(orders) > 0:
            Utils.create_csv(f'{output_path}/order_r{revision}_v{version}.csv', orders)
        if len(order_items) > 0:
            Utils.create_csv(f'{output_path}/order_item_r{revision}_v{version}.csv', order_items)


    @classmethod
    def upload_file(self, store_reference, bucket, output_path):
        try:
            filename = Utils.create_zip(output_path)
            event = f"{store_reference}/{filename.split('/')[-1]}"
            bucket_obj = storage_client.bucket(bucket)
            blob = bucket_obj.blob(event)
            blob.upload_from_filename(filename)
            logging.info(f'[NappClient2] Upload file {filename} with success')
        except Exception as e:
            logging.error(f'[NappClient2] Error to upload file: {e}')


    @classmethod
    def upload_storage_file(self, store_reference, bucket, file):
        try:
            event = f"{store_reference}/{file.split('/')[-1]}"
            bucket_obj = storage_client.bucket(bucket)
            blob = bucket_obj.blob(event)
            blob.upload_from_filename(file)
            logging.info(f'[NappClient2] Upload file {file} with success')
        except Exception as e:
            logging.error(f'[NappClient2] Error to upload file: {e}')


    @classmethod
    def download_storage_file(self, store_reference, bucket, file):
        try:
            event = f"{store_reference}/{file.split('/')[-1]}"
            bucket_obj = storage_client.bucket(bucket)
            blob = bucket_obj.blob(event)
            blob.download_to_filename(file)
            logging.info(f'[NappClient2] Download file {file} with success')
        except Exception as e:
            logging.err(f'[NappClient2] Error to downlaod file: {e}')
