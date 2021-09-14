import pika
import json


class WorkerService:
    __instance = None

    @staticmethod
    def getInstance():
        if WorkerService.__instance == None:
            WorkerService()
        return WorkerService.__instance

    def __init__(self, queue_url: str):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=queue_url))
        self.channel = self.connection.channel()
        WorkerService.__instance = self

    def start_consuming(self, callback, queue_chanel: str) -> None:
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=queue_chanel, on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()

    def push_to_channel(self, document_id: int, file_name: str, document_type_id: int, processing_options: int, queue_chanel: str, extension="") -> None:
        self.channel.queue_declare(queue=queue_chanel, durable=True)
        self.channel.basic_publish(
            exchange='',
            routing_key=queue_chanel,
            body=json.dumps({"document_id": document_id, "file_name": file_name, "document_type_id": document_type_id,
                             "processing_options": processing_options, "extension": extension}),
            properties=pika.BasicProperties(
                delivery_mode=2,
            )
        )
