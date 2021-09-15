import pika
import json

class WorkerService:
    __instance = None

    @staticmethod
    def getInstance(queue_url: str, exchange: str, exchange_type: str):
        if WorkerService.__instance == None:
            WorkerService(queue_url, exchange, exchange_type)
        return WorkerService.__instance

    def __init__(self, queue_url: str, exchange: str, exchange_type: str):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=queue_url))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=exchange, exchange_type=exchange_type)
        WorkerService.__instance = self

    def start_consuming(self, callback, queue_chanel: str) -> None:
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=queue_chanel, on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()

    def push_to_channel(self, file_name: str, document_type_id: int, processing_options: int, queue_chanel: str, exchange_type: str = '')  -> None:
        self.channel.queue_declare(queue=queue_chanel, durable=True)
        self.channel.basic_publish(
            exchange=exchange_type,
            routing_key=queue_chanel,
            body=json.dumps({"file_name": file_name, "document_type_id": document_type_id,
                             "processing_options": processing_options}),
            properties=pika.BasicProperties(
                delivery_mode=2, 
            )
        )
