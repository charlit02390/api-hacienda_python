import connexion
import json
from service import users as service


def create_new_user():
    body = json.loads(connexion.request.data)
    result = service.create_user(body['data'])
    return result


def route_get_user_byid(id):
    result = service.get_list_users(id)
    return result


def route_list_users():
    result = service.get_list_users()
    return result


def route_delete_user(id):
    result = service.delete_user(id)
    return result


def route_delete_user_companies():
    body = json.loads(connexion.request.data)
    result = service.delete_user_companies(body['data'])
    return result


def route_modify_user():
    body = json.loads(connexion.request.data)
    result = service.modify_user(body['data'])
    return result


def login(email, password):
    result = service.login(email, password)
    return result

