"""
Module that contains overrides to connexion's configurations.
"""

import logging

from flask import jsonify
from connexion.decorators.validation import RequestBodyValidator, ValidationError, is_null

logger = logging.getLogger(__name__)

class DetailedRequestBodyValidator(RequestBodyValidator):
    # doing pretty much what the function does, except extending
    # the caught exception code.
    def validate_schema(self, data, url):
        if self.is_null_value_valid and is_null(data):
            return None

        errors = sorted(self.validator.iter_errors(data),
                        key=lambda e: e.path)
        if errors:
            logger.error("""{url} had validation errors:
{errors}""".format(url=url, errors=errors),
                         extra={'validator': 'body'})
            response_data = []
            for error in errors:
                response_data.append("""-In {}: {}.""".format(
                    str(list(error.absolute_path)), error.message))
            response = jsonify({ 'status': 400,
                                'detail': ("""The received json has the """
                                                """following errors:
""") + str(response_data)})
            response.status_code = 400
            return response

        return None

