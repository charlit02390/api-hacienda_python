import functools
from timeit import default_timer as timer

from flask import g
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


def log_section(name: str, time_it: bool = False):
    def decoratored(func):
        @functools.wraps(func)
        def wrapper_log_section(*args, **kwargs):
            print('*Start {}'.format(name))
            if time_it:
                start = timer()
                val = func(*args, **kwargs)
                end = timer()
                print('-Execution time: {}'.format((end - start)))
            else:
                val = func(*args, **kwargs)
            print(val)
            print('*End {}'.format(name))
            print('-----')
            return val

        return wrapper_log_section

    return decoratored
