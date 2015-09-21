# -*- coding: utf-8 -*-
"""
    simulate_behavior.py
    ~~~~~~~~~~~~~~~~~~~~

    Pretend to browse e-commerce and respond to ads
"""

import sys
import requests
import time
import uuid
import numpy as np

N_BRANDS = 6


def _get_user_brand_prefs():
    """
    Provide a unit vector over the brands to represent
    a user's preference among them
    """
    prefs = np.random.uniform(0, 1, size=N_BRANDS)
    normalized_prefs = prefs * (1. / sum(prefs))
    return normalized_prefs


def _get_population_brand_prefs(n_users):
    """
    Create user_ids and preferences
    """

    return {
        str(uuid.uuid4()): _get_user_brand_prefs()
        for i in range(n_users)
    }


def _get_brand_patterns():
    """
    Define each brand's product mix (via params to a normal dist)
    """
    return [
        (np.random.uniform(100, 800), np.random.exponential(10))
        for i in range(N_BRANDS)
    ]


def _draw_user_brand_interest(user_prefs, brand_patterns):
    """
    Draw a brand based on user preference and a product based on brand params
    """
    try:
        brand_draw = np.random.multinomial(1, user_prefs)
    except:
        import pdb; pdb.set_trace()
    brand_index = brand_draw.argmax()

    product_price = np.random.normal(*brand_patterns[brand_index])
    return dict(brand=brand_index, price=product_price)


def _receive_ad(population_prefs, user_id, brand_index):
    """
    User receives an ad for brand
    If user has reasonable preference for this brand, the preference increments
    Otherwise, the preference drops.
    """
    prefs = population_prefs[user_id]
    if np.random.uniform(0, 1) > (N_BRANDS / 2.) * prefs[brand_index]:
        prefs[brand_index] += .1
    else:
        prefs[brand_index] = prefs[brand_index] - .1 if prefs[brand_index] > .1 else 0.

    population_prefs[user_id] = prefs * (1. / sum(prefs))
    return population_prefs


def _consider_purchase(product_viewed, population_prefs, user_id):
    """
    User considers ending activity via purchase or bailing entirely
    """
    sd = np.std(population_prefs[user_id])
    if sd < .05:
        # low variance in prefs, nothing compelling here, bail
        del population_prefs[user_id]
        return population_prefs, False
    if sd > .15:
        # high variance in prefs, go for it
        del population_prefs[user_id]
        return population_prefs, True
    return population_prefs, False


def _experience_product(product_viewed, user_id,
                        receiver_url, time_, population_prefs):
    """
    Send logs to tracking service and check to see if an ad should render
    """

    event = dict(user_id=user_id, timestamp=time_, **product_viewed)
    r = requests.post(receiver_url + '/log', params=event)
    time.sleep(.01)
    r = requests.get(receiver_url + '/show', params=event)
    if r.json().get('show'):
        population_prefs = _receive_ad(population_prefs, user_id, event['brand'])
    return population_prefs, event


def _register_purchase(event, receiver_url):
    requests.post(receiver_url + '/conversion', params=event)


def main():
    n_users = int(sys.argv[1])
    receiver_url = sys.argv[2]

    brand_patterns = _get_brand_patterns()
    population_prefs = _get_population_brand_prefs(n_users)
    user_ids = population_prefs.keys()
    time_ = 0

    while len(population_prefs) > n_users / 100.:
        time_ += 1
        user_idx = np.random.randint(len(population_prefs))
        user_id = user_ids[user_idx]
        user_prefs = population_prefs[user_id]
        product_viewed = _draw_user_brand_interest(user_prefs, brand_patterns)
        population_prefs, event = _experience_product(
            product_viewed, user_id, receiver_url, time_, population_prefs)
        if np.random.uniform(0, 1) > .9:
            population_prefs, purchase = _consider_purchase(
                product_viewed, population_prefs, user_id)
            if purchase:
                _register_purchase(event, receiver_url)
            user_ids = population_prefs.keys()


if __name__ == '__main__':
    main()
