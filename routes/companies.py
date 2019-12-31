
import connexion

from service import companies as service


def route_list_companies():
    result = service.get_list_companies()
    return result


def route_get_company_byid(id):
    result = service.get_list_companies(id)
    return result


def save_company():
    file = connexion.request.files['firma']
    body = connexion.request.form
    result = service.create_company(body, file.stream.read())
    return result


def route_update_company():
    return 1


def route_delete_company():
    return 1

