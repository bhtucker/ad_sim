# -*- coding: utf-8 -*-
"""
    wsgi
    ~~~~
    receiver wsgi module
"""

from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware

import receiver

application = DispatcherMiddleware(receiver.create_app())

if __name__ == "__main__":
    run_simple(
        '0.0.0.0', 5000, application,
        use_reloader=True, use_debugger=True)
