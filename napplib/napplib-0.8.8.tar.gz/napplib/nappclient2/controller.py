import os, requests, json, datetime, logging, zipfile, glob
from .utils import Utils
from .models.product import Product
from .models.order import Order
from .models.order_item import OrderItem


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(threadName)-11s %(levelname)-10s %(message)s")
server_url = 'https://connection.nappsolutions.io'


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
        filename = Utils.create_zip(output_path)
        sign_file = filename.split('/')[-1]
        
        logging.info(f'[NappClient2] Upload file {filename} for store {store_reference}')
        
        headers = dict()
        headers['Authorization'] = f'{store_reference}'
        
        signed_url = requests.get(f'{server_url}/upload/sign/{sign_file}/{bucket}', headers=headers).content.decode('utf-8')

        logging.info(f'[NappClient2] Signed URL: {signed_url}')
        
        headers = dict()
        headers['User-Agent'] = 'NappClient2'
        headers['Content-Type'] = 'application/zip'

        upload_response = requests.put(signed_url, headers=headers, files = {'archive': open(filename, 'rb')})
        logging.info(f'[NappClient2] Upload file {sign_file} response: {upload_response.status_code}')


    @classmethod
    def download_storage_file(self, store_reference, bucket, file):
        headers = dict()
        headers['Authorization'] = f'{store_reference}'
        
        download_url = requests.get(f'{server_url}/download/file/?bucket={bucket}&filename={file}', headers=headers).content.decode("utf-8")
        download_url = json.loads(download_url)['url']

        logging.info(f'[NappClient2] Generating Download file URL: {download_url}')
        
        headers = dict()
        headers['User-Agent'] = 'NappClient2'
        headers['Content-Type'] = 'application/zip'

        download_response = requests.get(download_url, headers=headers)
        logging.info(f'[NappClient2] Download file {file} response: {download_response.status_code}')


    @classmethod
    def upload_storage_file(self, store_reference, bucket, file):
        headers = dict()
        headers['Authorization'] = f'{store_reference}'
        
        upload_url = requests.get(f'{server_url}/upload/sign/{file}/{bucket}', headers=headers).content.decode('utf-8')

        logging.info(f'[NappClient2] Generating Upload file URL: {upload_url}')
        
        headers = dict()
        headers['User-Agent'] = 'NappClient2'
        headers['Content-Type'] = 'application/zip'

        upload_response = requests.put(upload_url, headers=headers, files = {'archive': open(file, 'rb')})
        logging.info(f'[NappClient2] Upload file {file} response: {upload_response.status_code}')