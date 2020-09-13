import connexion
import json
from service import users as service


def create_new_user():
    body = json.loads(connexion.request.data)
    try:
        result = service.create_user(body['data'])
    except KeyError as ker:
        result = {'error' : 'Missing property: ' + str(ker)}
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
    try:
        result = service.delete_user_companies(body['data'])
    except KeyError as ker:
        result = {'error' : 'Missing property: ' + str(ker)}
    return result


def route_modify_user():
    body = json.loads(connexion.request.data)
    try:
        result = service.modify_user(body['data'])
    except KeyError as ker:
        result = {'error' : 'Missing property: ' + str(ker)}
    return result


def login():
    body = connexion.request.form
    result = service.login(body)
    return result

