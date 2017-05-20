import logging
import pika


class QueueConsumer:
    EXCHANGE_NAME = 'channels_feed'
    QUEUE_NAME = 'channels_feed.single'
    EXCHANGE_TYPE = 'direct'
    ROUTING_KEY = '#'
    DURABLE = True

    def __init__(self, config):
        """Create a new instance of the consumer class, passing in the AMQP
        URL used to connect to RabbitMQ.

        :param str url: The AMQP url to connect with

        """
        self.connection = None
        self.channel = None
        self.closing = False
        self.consumer_tag = None
        self.url = f"amqp://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['vh']}"

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def run(self, on_message_callback):
        """Run the consumer by connecting to RabbitMQ and then
        starting the IOLoop to block and allow the SelectConnection to operate.

        """
        self.on_message_callback = on_message_callback
        self.connection = self.connect()
        self.connection.ioloop.start()

    def stop(self):
        """Cleanly shutdown the connection to RabbitMQ by stopping the consumer
        with RabbitMQ. When RabbitMQ confirms the cancellation, on_cancelok
        will be invoked by pika, which will then closing the channel and
        connection. The IOLoop is started again because this method is invoked
        when CTRL-C is pressed raising a KeyboardInterrupt exception. This
        exception stops the IOLoop which needs to be running for pika to
        communicate with RabbitMQ. All of the commands issued prior to starting
        the IOLoop will be buffered but not processed.

        """
        logging.info('Stopping')
        self.closing = True
        if self.channel:
            logging.debug('Sending a Basic.Cancel RPC command to RabbitMQ')
            self.channel.basic_cancel(lambda q: self.channel.close(), self.consumer_tag)
        self.connection.ioloop.start()
        logging.info('Stopped')

    def connect(self):
        """This method connects to RabbitMQ, returning the connection handle.
        When the connection is established, the on_connection_open method
        will be invoked by pika.

        :rtype: pika.SelectConnection

        """
        logging.info(f"Connecting to {self.url}")
        return pika.SelectConnection(pika.URLParameters(self.url),
                                     self.on_connection_open,
                                     stop_ioloop_on_close=False)

    def reconnect(self):
        """Will be invoked by the IOLoop timer if the connection is
        closed. See the on_connection_closed method.

        """
        # This is the old connection IOLoop instance, stop its ioloop
        self.connection.ioloop.stop()

        if not self.closing:
            self.connection = self.connect()
            self.connection.ioloop.start()

    def start_consuming(self):
        """This method sets up the consumer by first calling
        add_on_cancel_callback so that the object is notified if RabbitMQ
        cancels the consumer. It then issues the Basic.Consume RPC command
        which returns the consumer tag that is used to uniquely identify the
        consumer with RabbitMQ. We keep the value to use it when we want to
        cancel consuming. The on_message method is passed in as a callback pika
        will invoke when a message is fully received.
    
        """
        logging.debug('Adding consumer cancellation callback')
        self.channel.add_on_cancel_callback(lambda method_frame: self.channel.close if self.channel else None)
        logging.debug('Issuing consumer related RPC commands')
        self.consumer_tag = self.channel.basic_consume(
            self.on_message_callback,
            self.QUEUE_NAME
        )

    def on_connection_open(self, connection):
        """This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.

        :type connection: pika.SelectConnection

        """
        logging.debug('Connection opened')
        self.connection.add_on_close_callback(self.on_connection_closed)
        self.connection.channel(on_open_callback=self.on_channel_open)

    def on_connection_closed(self, connection, reply_code, reply_text):
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.

        :param pika.connection.Connection connection: The closed connection obj
        :param int reply_code: The server provided reply_code if given
        :param str reply_text: The server provided reply_text if given

        """
        self.channel = None
        if self.closing:
            self.connection.ioloop.stop()
        else:
            logging.warning(f"Connection closed, reopening in 5 seconds: ({reply_code}) {reply_text}")
            self.connection.add_timeout(5, self.reconnect)

    def on_channel_open(self, channel):
        """This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it.

        Since the channel is now open, we'll declare the exchange to use.

        :param pika.channel.Channel channel: The channel object

        """
        logging.debug('Channel opened')
        self.channel = channel
        self.channel.add_on_close_callback(lambda c, rc, rt: self.connection.close())
        logging.debug(f"Declaring exchange {self.EXCHANGE_NAME}")
        self.channel.exchange_declare(
            lambda frame: self.channel.queue_declare(self.on_queue_declareok, self.QUEUE_NAME, durable=self.DURABLE),
            self.EXCHANGE_NAME,
            self.EXCHANGE_TYPE,
            durable=self.DURABLE
        )

    def on_queue_declareok(self, method_frame):
        """Method invoked by pika when the Queue.Declare RPC call made. 
        In this method we will bind the queue
        and exchange together with the routing key by issuing the Queue.Bind
        RPC command. When this command is complete, the lambda will
        be invoked by pika.

        :param pika.frame.Method method_frame: The Queue.DeclareOk frame
        """
        logging.debug(f"Binding {self.EXCHANGE_NAME} to {self.QUEUE_NAME} with {self.ROUTING_KEY}")
        self.channel.queue_bind(
            lambda q: self.start_consuming(),
            self.QUEUE_NAME,
            self.EXCHANGE_NAME,
            self.ROUTING_KEY
        )
