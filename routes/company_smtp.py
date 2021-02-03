
import connexion
import json
from service import company_smtp as service
from helpers import errors
from helpers import utils


def route_save_company_smtp(company_id):
    body = json.loads(connexion.request.data)
    result = service.save_company_smtp(body['data'], company_id)
    return utils.build_response(result)


def route_get_company_smtp(company_id):
    result = service.get_company_smtp(company_id)
    return utils.build_response(result)


def route_delete_company_smtp(company_id):
    result = service.delete_company_smtp(company_id)
    return utils.build_response(result)


def route_modify_company_smtp(company_id):
    body = json.loads(connexion.request.data)
    result = service.modify_company_smtp(body['data'], company_id)
    return utils.build_response(result)
