import random
import threading
from functools import wraps


def random_element(xlist):
    return random.choice(xlist) if len(xlist) > 0 else None


def deep_get_attr(obj, attr, default=None):
    attributes = attr.split(".")
    for i in attributes:
        try:
            obj = getattr(obj, i)
            if callable(obj):
                obj = obj()
        except AttributeError:
            return default
    return obj


def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default


def read_to_string(file_path):
    with open(file_path, 'r') as file:
        data = file.read()
    return data


def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper


def transactional(db):
    def wrapper(fn):
        @wraps(fn)
        def wrapped(self, *f_args, **f_kwargs):
            return db.execute_in_transaction(callback=lambda: fn(self, *f_args, **f_kwargs))
        return wrapped
    return wrapper
