# -*- coding: utf-8 -*-
"""
    manage.py
    ~~~~~~~~~

    Start some long-running worker processes
"""

from flask.ext.script import Manager
import json

from receiver import create_app
from receiver.core import kafka
from receiver.track import track_page_view

app = create_app()
manager = Manager(app)


@manager.command
def track():
    topic = kafka.topics.get('page_views')
    consumer = topic.get_simple_consumer()
    while consumer:
        line = consumer.consume().value
        # import pdb; pdb.set_trace()
        try:
            args = json.loads(line)
            assert isinstance(args, dict)
            track_page_view(args)

        except:
            pass


if __name__ == "__main__":
    manager.run()
