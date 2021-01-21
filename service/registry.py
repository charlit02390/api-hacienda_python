"""Module that enables interaction with the registry infrastructure and facilitates data to routes. I guess...
"""
import json
from infrastructure import registry
from helpers import utils

def get_person(person_id: str) -> dict:
    """
    Returns information about the specified person.

    :param person_id: str - An 'id' string representing the unique
        identification to find.
    :returns: dict - A dictionary with keys:

        - 'http_status' : an http response status code.
        - 'data' : data for the response's body.
        - ['error'] : An optional error message if an
          exception/error occurred.
        - ['message'] : An optional message for additional
          information.
        - ['headers'] : An optional dictionary with headers
          to be sent.

    """
    max_length = 12
    if len(person_id) > max_length:
      return utils.build_response_data({
        'error': {
          'http_status': 400,
          'code': 400,
          'detail': (
            'ID length is too long.'
            ' Must be {} characters or less.'
            ).format(max_length)
        }
      })

    person =  registry.get_person(person_id)
    if person is None:
      return utils.build_response_data({
        'error': {
          'http_status': 404,
          'code': 404,
          'detail': 'Person not found.'
          }
      })

    result = {'data': person}

    response = utils.build_response_data(
        result,
        warn_msg='Person not found for the id: "{}".'.format(
            person_id
            ))
    return response
