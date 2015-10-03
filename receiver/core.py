# -*- coding: utf-8 -*-
"""
    receiver.core
    ~~~~~~~~~~~~~

    Extensions module for receiver app
"""

from flask_redis import Redis
from pykafka import KafkaClient

redis = Redis()


class KafkaProxy(object):
    """
    Store a Kafka client
    initialized with the Flask app
    """
    def __init__(self):
        self._kafkaclient = None

    def init_app(self, app):
        self._kafkaclient = KafkaClient(app.config.get('KAFKA_URI'))

    def __getattr__(self, attr):
        return getattr(self._kafkaclient, attr)

kafka = KafkaProxy()
