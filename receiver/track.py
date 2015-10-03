# -*- coding: utf-8 -*-
"""
    track.py
    ~~~~~~~~~~~

    Take request parameters and update redis counters
"""
from receiver.core import redis


def _get_brand_key(args):
    return '|'.join([args['user_id'], args['brand']])


def _get_brand_avg_key(args):
    return _get_brand_key(args) + '|price'


def _get_conversion_key(args):
    return '|'.join([args['user_id'], args['timestamp']])


def _update_brand_price_avg(args, new_brand_count):
    brand_avg_key = _get_brand_avg_key(args)
    old_average = redis.get(brand_avg_key)

    if old_average:
        old_value = float(old_average) * (int(new_brand_count) - 1)
        new_value = old_value + float(args['price'])
        new_average = new_value / float(new_brand_count)
    else:
        new_average = float(args['price'])

    redis.set(brand_avg_key, new_average)


def track_page_view(args):
    # increment user view count
    redis.incr(args['user_id'])

    # increment brand count
    new_brand_count = redis.incr(_get_brand_key(args))

    _update_brand_price_avg(args, new_brand_count)
