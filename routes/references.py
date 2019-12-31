import connexion
import json
from service import references as service

def generated_key():
    body = json.loads(connexion.request.data)
    result = service.generate_key(body['data'])
    return result


def get_token():
    body = request.form
    result = service.get_token_hacienda(body)
    return result
