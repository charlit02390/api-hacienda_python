"""Module that enables interaction with the registry infrastructure and facilitates data to routes. I guess...
"""
import json
from infrastructure import registry
from helpers import utils

def get_person(id: str) -> dict:
    """
    Returns information about the specified person.

    :param id: str - An 'id' string representing the unique
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
    # should prolly check the id length and restrict it to the
    # proper length...
    # make a "constant" for length, which value should be 9...
    # TODO i guess... too lazy rn
    result = { 'data' : registry.get_person(id) }

    response = utils.build_response_data(
        result,
        warn_msg='Person not found for the id: "{}".'.format(
            id
            ))
    return response
