import connexion
import json

from flask import request

from service import references as service
from helpers import utils

def generated_key():
    body = json.loads(connexion.request.data)
    result = service.generate_key(body['data'])
    return utils.build_response(result)


def get_token():
    body = request.form
    result = service.get_token_hacienda(body)
    return result
