
import connexion
from service import companies as service
from helpers import utils

def route_list_companies():
    result = service.get_list_companies()
    return utils.build_response(result)


def route_get_company_byid(id):
    result = service.get_list_companies(id)
    return utils.build_response(result)


def route_save_company():
    file = connexion.request.files['firma']
    logo = connexion.request.files['logo']

    body = connexion.request.form
    result = service.create_company(body, file.stream.read(), logo.stream.read())
    return utils.build_response(result)


def route_delete_company(id):
    result = service.delete_company(id)
    return utils.build_response(result)


def route_modify_company():
    file = connexion.request.files['firma']
    logo = connexion.request.files['logo']
    body = connexion.request.form
    result = service.modify_company(body, file.stream.read(), logo.stream.read())
    return utils.build_response(result)

