# -*- coding: utf-8 -*-
"""
    receiver
    ~~~~~~~~

    receiver flask app
"""

from . import factory


def create_app(**kwargs):
    return factory.create_app(__name__, __path__)
