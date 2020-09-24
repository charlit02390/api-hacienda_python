import json
import time
from configuration import globalsettings
import six
from werkzeug.exceptions import Unauthorized

from infrastructure import users
from infrastructure.dbadapter import DbAdapterError

from jose import jwt, JWTError

from service import utils
from helpers.errors.enums import InputErrorCodes, AuthErrorCodes, InternalErrorCodes
from helpers.errors.exceptions import InputError, AuthError, ServerError
from helpers.utils import build_response_data # CONSIDER MAKING THIS A DECORATOR

cfg = globalsettings.cfg


def create_user(data):
    _email = data['email']
    _password = data['password']
    _name = data['name']
    _idrol = data['idrol']
    _idcompanies = data['idcompanies']

    user_exist = users.verify_email(_email)
    if user_exist:
        raise InputError('Email {}'.format(_email), status=InputErrorCodes.DUPLICATE_RECORD)

    users.save_user(_email, _password, _name, _idrol, _idcompanies)

    return build_response_data({'message' : 'User created successfully'})


def modify_user(data):
    _email = data['email']
    _password = data['password']
    _name = data['name']
    _idrol = data['idrol']
    _idcompanies = data['idcompanies']

    users.modify_user(_email, _password, _name, _idrol, _idcompanies)

    return build_response_data({'message' : 'User updated successfully'})


def get_list_users(id_user=0):
    if id_user == 0:
        result = { 'data': {'users': users.get_users()}}
    else:
        result = { 'data':{'user': users.get_user_data(id_user)}}

    return build_response_data(result)


def delete_user(id_user):
    users.delete_user_data(id_user)
    return build_response_data({'message' : 'The user has been deleted successfully.'})


def delete_user_companies(data):
    _email = data['email']
    users.delete_user_companies(_email)
    return build_response_data({'message' : "The user's associated companies have been cleared."})


def login(data):
    email = data['email']
    password = data['password']

    user_check = users.check_user(email, password)
    if not user_check:
        raise AuthError(status=AuthErrorCodes.WRONG_CREDENTIALS)


    try:
        token = generate_token(email)
    except Exception as ex: # Internal Error Code: token generation error
        raise ServerError(status=InternalErrorCodes.INTERNAL_ERROR,
                            message='A problem was found while generating the JWT')
        
    result = { 'data' : {'token' : token, 'user' : user_check}}

    return build_response_data(result)


def generate_token(email):
    timestamp = _current_timestamp()
    payload = {
        "iss": cfg['jwt_issuer'],
        "iat": int(timestamp),
        "exp": int(timestamp + cfg['jwt_lifetime_seconds']),
        "sub": str(email),
    }

    return jwt.encode(payload, cfg['jwt_secret'], algorithm=cfg['jwt_algorithm'])


def decode_token(token):
    try:
        return jwt.decode(token, cfg['jwt_secret'], algorithms=cfg['jwt_algorithm'])
    except JWTError as e:
        six.raise_from(Unauthorized, e)


def _current_timestamp() -> int:
    return int(time.time())
