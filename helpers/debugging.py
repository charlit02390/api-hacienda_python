"""
Module that contains debugging utilities
"""

import functools
from timeit import default_timer as timer

from flask import g
from connexion import request

# constants
DEBUG_SWITCH_NAME = 'debugOn'
DEBUG_SWITCH_KEYWORD = 'activate1!'
DEBUG_G_VAR_NAME = 'is_debug'


def set_debug_mode(func):
    """
    Decorator for route functions. Sets an is_debug property to
    flask's g variable, so the error handler can expose debugging
    information to the request received.

    :param func: function - the function to decorate
    :returns: function - the decorated function
    """
    @functools.wraps(func)
    def decoratored(*args, **kwargs):
        debugVal = True if \
            request.args.get(DEBUG_SWITCH_NAME, '') \
            == DEBUG_SWITCH_KEYWORD else \
            False
        g.is_debug = debugVal
        
        return func(*args,**kwargs)

    return decoratored


def log_section(name: str, time_it: bool = False):
    """
    Decorator function for including a header and footer
    to functions that summarize an operation.

    :param name: str - the name of the section that will be logged.
    :param time_it: [optional] bool - True if execution time for
        the operation must be recorded and logged.
        Default is False.

    :returns: function - the decorated function
    """
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


def time_my_func(func):
    @functools.wraps(func)
    def decoratored(*args, **kwargs):
        s = timer()
        val = func(*args, **kwargs)
        e = timer()
        print('Function: {}. Execution Time: {}'
              .format(func.__qualname__, (e-s)))
        return val
    return decoratored
