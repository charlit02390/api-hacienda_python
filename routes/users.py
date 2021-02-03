import connexion
import json
from service import users as service
from helpers import utils

def create_new_user():
    body = json.loads(connexion.request.data)
    result = service.create_user(body['data'])
    return utils.build_response(result)


def route_get_user_byid(user_id):
    result = service.get_list_users(user_id)
    return utils.build_response(result)


def route_list_users():
    result = service.get_list_users()
    return utils.build_response(result)


def route_delete_user(user_id):
    result = service.delete_user(user_id)
    return utils.build_response(result)


def route_delete_user_companies():
    body = json.loads(connexion.request.data)
    result = service.delete_user_companies(body)
    return utils.build_response(result)


def route_modify_user():
    body = json.loads(connexion.request.data)
    result = service.modify_user(body['data'])
    return utils.build_response(result)


def login():
    body = connexion.request.form
    result = service.login(body)
    return utils.build_response(result)

