from flask import g
import functools
from connexion import request

# constants
DEBUG_SWITCH_NAME = 'debugOn'
DEBUG_SWITCH_KEYWORD = 'activate1!'
DEBUG_G_VAR_NAME = 'is_debug'


def set_debug_mode(func):
    @functools.wraps(func)
    def decoratored(*args, **kwargs):
        debugVal = True if request.args.get(DEBUG_SWITCH_NAME, '') == DEBUG_SWITCH_KEYWORD else False
        g.is_debug = debugVal
        
        return func(*args,**kwargs)

    return decoratored
