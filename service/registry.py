"""Module that enables interaction with the registry infrastructure and facilitates data to routes. I guess...
"""
import json
from infrastructure import registry
from service import utils


def get_person(id: str) -> dict:
    """
    Returns information about the specified person.

    :param id: str - An 'id' string representing the unique identification to find.
    :returns: dict - A dictionary with keys:
        'httpstatus' : an http response status code
        'data' : data for the response's body
        ['error'] : An optional error message if an exception/error occurred
        ['message'] : An optional message for additional information
    """
    # should prolly check the id length and restrict it to the proper length...
    # make a "constant" for length, which value should be 9...
    # TODO i guess... too lazy rn
    result = registry.get_person(id)
    response = utils.buildResponseData(result, dict, 'Person not found for the id: "' + id + '".')


    return response
