from functools import wraps
import requests as rq

REQUEST_TIMEOUT = 10


def handle_network_errors(default=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (rq.exceptions.ConnectionError, rq.exceptions.Timeout):
                print("could not reach the server\n")
                return default
        return wrapper
    return decorator
