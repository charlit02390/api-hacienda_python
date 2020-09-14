import connexion
import json

from flask import request

from service import references as service


def generated_key():
    body = json.loads(connexion.request.data)
    try:
        result = service.generate_key(body['data'])
    except KeyError as ker:
        result = {'error' : 'Missing property: ' + str(ker)}
    return result


def get_token():
    body = request.form
    result = service.get_token_hacienda(body)
    return result
