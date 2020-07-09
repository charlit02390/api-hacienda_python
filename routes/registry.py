"""Module for hiring a service in order to get or manipulate resources.
"""
import connexion
from service import registry as service
from service import utils


def route_get_person(id):
    """
    Calls the service for looking up a person's data and returns a response with the information found.

    :returns: dict - A dictionary to be serialized as json to be sent as response, alonside a status code.
    """
    data = service.get_person(id)
    response = utils.prepareResponse('persona', data)
    return response, data['httpstatus']
