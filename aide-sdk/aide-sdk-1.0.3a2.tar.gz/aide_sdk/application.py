from aide.messaging.consumer import Consumer
from aide.messaging.publisher import Publisher

from aide_sdk.inference.inference_manager import InferenceManager
from aide_sdk.inference.aideoperator import AideOperator
from aide_sdk.logger.logger import LogManager
from aide_sdk.manifests.manifest import load
from aide_sdk.messaging.config import QueueConfiguration, ElasticConfiguration, PacsConfiguration
from aide_sdk.messaging.pacs_client import PacsClient
from aide_sdk.messaging.elastic_api import ElasticWebAPIClient


LogManager.init_logging()
logger = LogManager._get_audit_logger()


class AideApplication:
    @staticmethod
    def start(operator: AideOperator) -> None:
        manifest = load()
        rabbit_config = QueueConfiguration(input_queue=manifest.get_queue_name(),
                                           outout_queue="input")
        elastic_config = ElasticConfiguration()
        pacs_config = PacsConfiguration()

        model_consumer = Consumer(rabbit_config.consumer_config)
        model_publisher = Publisher(rabbit_config.publisher_config)
        elastic_client = ElasticWebAPIClient(elastic_config)
        pacs_client = PacsClient(pacs_config)

        manager = InferenceManager(model_consumer, model_publisher, operator, elastic_client, pacs_client)
        manager.start_listening()
        model_consumer.join()
