from functools import wraps

from app import config
from flask import g
from flask_login import current_user


def use_template_globals(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        g.app_base_link = config.APP_BASE_LINK
        g.current_user = current_user
        g.static_base = config.STATIC_BASE
        g.images_base = config.IMAGES_BASE
        return fn(*args, **kwargs)
    return wrapped
