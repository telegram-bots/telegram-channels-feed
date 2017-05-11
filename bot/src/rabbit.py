from pika import BlockingConnection, ConnectionParameters, BasicProperties
from src.config import encoding


class RabbitMQ:
    def __init__(self, config):
        self.config = config
        self.props = BasicProperties(delivery_mode=2,
                                     content_type="text/plain",
                                     content_encoding=encoding)
        self.connection = BlockingConnection(
            ConnectionParameters(host=config['host'],
                                 port=config.getint('port')))
        self.channel = self.connection.channel()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.channel.stop_consuming()
        self.channel.close()
        self.connection.close()

    def init(self):
        self.channel.exchange_declare(exchange=self.config['exchange'],
                                      type="direct",
                                      durable=True)
        self.channel.queue_declare(queue=self.config['queue'], durable=True)
        self.channel.queue_bind(exchange=self.config['exchange'],
                                queue=self.config['queue'])

    def consume(self, callback):
        self.channel.basic_consume(callback, queue=self.config['queue'])
        self.channel.start_consuming()
