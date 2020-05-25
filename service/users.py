import json
import time
from configuration import globalsettings
import six
from werkzeug.exceptions import Unauthorized

from infrastructure import users

from jose import jwt, JWTError

cfg = globalsettings.cfg


def create_user(data):
    _email = data['email']
    _password = data['password']
    _name = data['name']
    _idrol = data['idrol']
    _idcompanies = data['idcompanies']

    user_exist = users.verify_email(_email)

    if not user_exist:

        result = users.save_user(_email, _password, _name, _idrol)

        if result is True:
            for id in _idcompanies:
                _idcompany = id['id']
                result = users.save_user_company(_email,_idcompany)
        else:
            return {'Error': 'The user can not be created'}

        return result
    else:
        return {'message': 'Email already registered'}


def modify_user(data):
    _email = data['email']
    _password = data['password']
    _name = data['name']
    _idrol = data['idrol']
    _idcompanies = data['idcompanies']

    result = users.modify_user(_email, _password, _name, _idrol)

    for id in _idcompanies:
        _idcompany = id['id']
        user_company_exist = users.verify_user_company(_email,_idcompany)
        if user_company_exist is False:
            result = users.save_user_company(_email,_idcompany)

    return result


def get_list_users(id_user=0):
    if id_user == 0:
        result = {'users': users.get_users()}
    else:
        result = {'user': users.get_user_data(id_user)}
    return result


def delete_user(id_user):
    result = users.delete_user_data(id_user)
    return result


def delete_user_companies(data):
    _email = data['email']
    _idcompanies = data['idcompanies']

    for id in _idcompanies:
        _idcompany = id['id']
        result = users.delete_user_company(_email, _idcompany)
    if result is True:
        return {'message': 'The user company has been deleted'}
    else:
        return {'error': 'The user company can not be deleted'}


def login(email, password):
    user_check = users.check_user(email, password)
    if user_check is not None:
        token = generate_token(email)
        return {'token': token,
                'user': user_check}
    else:
        return {'error': 'the credentials are not correct please check the email or password'}


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
