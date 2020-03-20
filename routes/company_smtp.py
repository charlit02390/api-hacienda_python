
import connexion
import json
from service import company_smtp as service


def route_save_company_smtp(id):
    body = json.loads(connexion.request.data)
    result = service.save_company_smtp(body['data'], id)
    return result


def route_get_company_smtp(id):
    result = service.get_company_smtp(id)
    return result


def route_delete_company_smtp(id):
    result = service.delete_company_smtp(id)
    return result


def route_modify_company_smtp(id):
    body = json.loads(connexion.request.data)
    result = service.modify_company_smtp(body['data'], id)
    return result
