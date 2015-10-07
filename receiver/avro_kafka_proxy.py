# -*- coding: utf-8 -*-
"""
    receiver.avro_kafka_proxy
    ~~~~~~~~~~~~~~~~~~~~~~~~~
 
    Hold a KafkaProxy that will encode messages to Avro
"""

from pykafka import KafkaClient
from StringIO import StringIO
from 

AVROSCHEMAS = {}

class KafkaProxy(object):
    """
    Store a Kafka client
    initialized with the Flask app
    """
    def __init__(self):
        self._kafkaclient = None
        self.avro_writers = {}

    def init_app(self, app):
        self._kafkaclient = KafkaClient(app.config.get('KAFKA_URI'))

    def __getattr__(self, attr):
        return getattr(self._kafkaclient, attr)

    def produce_avro(self, topic, message):
        if topic not in self.avro_writers:
            self._initialize_avro_writer(topic)
        self.avro_writers[topic].write(message)

    def _initialize_avro_writer(self, topic):
        pass


class AvroWriter(object):
    """
    Write messages to a particular kafka topic
    using a partiular avro schema
    """
    def __init__(self, topic):
        self.schema = AVROSCHEMAS.get(topic.name)
        self.producer = topic.get_producer()

