# -*- coding: utf-8 -*-
"""
    receiver.views
    ~~~~~~~~~~~~~~
    Some routing
"""
from flask import Blueprint, render_template, request, jsonify
import json
from functools import wraps

from receiver.core import kafka, redis
from receiver.track import (
    _get_brand_key, _get_brand_avg_key, _get_conversion_key)

bp = Blueprint('views', __name__)


def send_to_kafka(topic):
    def decorator(fn):
        producer = kafka.topics.get(topic).get_producer()

        @wraps(fn)
        def wrapper(*args, **kwargs):
            producer.produce([json.dumps(request.args)])
            return fn(*args, **kwargs)
        return wrapper
    return decorator


@bp.route('/')
def index():
    """Returns the demo interface."""
    return render_template('index.html')


@bp.route('/log', methods=['GET'])
@send_to_kafka('page_views')
def log_event():
    user_id = request.args['user_id']
    val = float((redis.get(user_id) or 1.))
    brand_count = float(redis.get(_get_brand_key(request.args)) or 0.)

    if 'verbose' in request.args:
        return jsonify(dict(
            impressions=redis.get(request.args['user_id']),
            brand_impressions=redis.get(_get_brand_key(request)),
            brand_average=redis.get(_get_brand_avg_key(request))
        ))

    if brand_count > (val / 2.) and val > 8.:
        import pdb; pdb.set_trace()
        return jsonify(dict(show=True))
    else:
        return jsonify(dict(show=False))

    return jsonify(dict(success=True))


@send_to_kafka('conversions')
@bp.route('/conversion', methods=['POST'])
def log_conversion_event():
    conversion_key = _get_conversion_key(request)

    for k, v in request.args.iteritems():
        redis.hset(conversion_key, k, v)

    return jsonify(dict(success=True))
