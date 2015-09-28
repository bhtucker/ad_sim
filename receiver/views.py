# -*- coding: utf-8 -*-
"""
    receiver.views
    ~~~~~~~~~~~~~~
    Some routing
"""
from flask import Blueprint, render_template, request, jsonify, current_app
from .core import redis
from pykafka import KafkaClient
import json
from functools import wraps

bp = Blueprint('views', __name__)


def send_to_kafka(topic):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if 'KAFKA_URI' in current_app.config:
                kafka = KafkaClient(current_app.config['KAFKA_URI'])
                producer = kafka.topics.get(topic).get_producer()
                producer.produce(json.dumps(request.args))

            return fn(*args, **kwargs)
        return wrapper
    return decorator


def _get_brand_key(request):
    return '|'.join([request.args['user_id'], request.args['brand']])


def _get_brand_avg_key(request):
    return _get_brand_key(request) + '|price'


def _get_conversion_key(request):
    return '|'.join([request.args['user_id'], request.args['timestamp']])


def _update_brand_price_avg(request, new_brand_count):
    brand_avg_key = _get_brand_avg_key(request)
    old_average = redis.get(brand_avg_key)

    if old_average:
        old_value = float(old_average) * (int(new_brand_count) - 1)
        new_value = old_value + float(request.args['price'])
        new_average = new_value / float(new_brand_count)
    else:
        new_average = float(request.args['price'])

    redis.set(brand_avg_key, new_average)


@bp.route('/')
def index():
    """Returns the demo interface."""
    return render_template('index.html')


@bp.route('/log', methods=['POST'])
@send_to_kafka('page_views')
def log_event():

    # increment user view count
    redis.incr(request.args['user_id'])

    # increment brand count
    new_brand_count = redis.incr(_get_brand_key(request))

    _update_brand_price_avg(request, new_brand_count)

    return jsonify(dict(success=True))


@send_to_kafka('conversions')
@bp.route('/conversion', methods=['POST'])
def log_conversion_event():
    conversion_key = _get_conversion_key(request)

    for k, v in request.args.iteritems():
        redis.hset(conversion_key, k, v)

    return jsonify(dict(success=True))


@send_to_kafka('impressions')
@bp.route('/show', methods=['GET'])
def show_():
    user_id = request.args['user_id']
    val = redis.get(user_id)
    if 'verbose' in request.args:
        return jsonify(dict(
            impressions=redis.get(request.args['user_id']),
            brand_impressions=redis.get(_get_brand_key(request)),
            brand_average=redis.get(_get_brand_avg_key(request))
        ))

    if int(val) > 2:
        return jsonify(dict(show=True))
    else:
        return jsonify(dict(show=False))
