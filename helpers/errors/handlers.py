import traceback

from werkzeug.exceptions import InternalServerError, HTTPException
from flask import g
from flask import Response
from connexion.apps.flask_app import FlaskApp
from connexion.apis.flask_api import FlaskApi

from helpers.utils import build_response
from helpers.errors import exceptions
from helpers.errors.enums import InternalErrorCodes
from helpers.debugging import DEBUG_G_VAR_NAME

from jsonschema import validate  # for development

schema = {
    'type': 'object',
    'properties': {
        'status': {
            'type': 'string'
        },
        'code': {
            'type': 'number'
        },
        'detail': {
            'type': 'string'
        },
        'message': {
            'type': 'string'
        }
    },
    'required': [
        'status',
        'code',
        'detail'
    ]
}


def internal_server_error_handler(exception: InternalServerError):
    _original_exception = exception.original_exception
    if isinstance(_original_exception, exceptions.IBError):
        return iberror_handler(_original_exception)
    else:
        return generic_exception_handler(exception)


def generic_exception_handler(exception: InternalServerError):
    error = {'http_status': 500,
             'code': InternalErrorCodes.INTERNAL_ERROR,
             'status': exceptions.IBError.status,
             'detail': exception.description}
    if g.get(DEBUG_G_VAR_NAME):
        error['debug'] = exceptions.IBError._build_debug_info(exception.original_exception)

    mimetype = 'application/json'
    validate(instance=error, schema=schema)
    return FlaskApi.get_response(build_response(error), mimetype)


def iberror_handler(exception: exceptions.IBError):
    data = exception.to_response()
    validate(instance=data, schema=schema)
    http_status_code = exception.code
    response = (data, http_status_code)
    mimetype = 'application/json'
    return FlaskApi.get_response(response, mimetype)


def register_flask_app_handlers(app: FlaskApp):
    app.add_error_handler(exceptions.IBError, iberror_handler)
    app.add_error_handler(HTTPException, internal_server_error_handler)
    app.add_error_handler(InternalServerError, internal_server_error_handler)
