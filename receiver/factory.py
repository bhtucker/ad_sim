# -*- coding: utf-8 -*-
"""
    receiver.factory
    ~~~~~~~~~~~~~~~~
    receiver factory module
"""

from flask import Flask
import logging
from .helpers import register_blueprints
from .core import redis


def create_app(package_name, package_path, settings_override=None):
    """Returns a :class:`Flask` application instance configured with common
    functionality for the Receiver app.
    :param package_name: application package name
    :param package_path: application package path
    :param settings_override: a dictionary of settings to override
    """
    app = Flask(package_name, instance_relative_config=True)

    app.config.from_object('receiver.settings')
    app.config.from_pyfile('settings.cfg', silent=True)
    app.config.from_object(settings_override)

    logger = logging.getLogger('werkzeug')
    handler = logging.FileHandler('access.log')
    logger.addHandler(handler)
    app.logger.addHandler(handler)
    redis.init_app(app)

    register_blueprints(app, package_name, package_path)

    return app
