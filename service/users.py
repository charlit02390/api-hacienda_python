import json
import time
from configuration import globalsettings
import six
from werkzeug.exceptions import Unauthorized

from infrastructure import users
from infrastructure.dbadapter import DatabaseError

from jose import jwt, JWTError

cfg = globalsettings.cfg


def create_user(data):
    try:
        _email = data['email']
        _password = data['password']
        _name = data['name']
        _idrol = data['idrol']
        _idcompanies = data['idcompanies']
    except KeyError as ker:
        return {'error' : 'Invalid property: ' + str(ker)}

    try:
        user_exist = users.verify_email(_email)
    except DatabaseError as dbe:
        return {'error' : str(dbe)}

    if user_exist:
        return {'message' : 'Given email is already registed.'}

    try:
        result = users.save_user(_email, _password, _name, _idrol, _idcompanies)
    except DatabaseError as dbe:
        return {'error' : "The user couldn't be created."} # or just... {'error' : str(dbe)}
    except KeyError as ker:
        return {'error' : str(ker)}

    return {'message' : 'User created successfully'}


def modify_user(data):
    try:
        _email = data['email']
        _password = data['password']
        _name = data['name']
        _idrol = data['idrol']
        _idcompanies = data['idcompanies']
    except KeyError as ker:
        return {'error' : str(ker)}

    try:
        users.modify_user(_email, _password, _name, _idrol, _idcompanies)
    except DatabaseError as dbe:
        return {'error' : str(dbe)}
    except KeyError as ker:
        return {'error' : str(ker)}

    return {'message' : 'User updated successfully'}


def get_list_users(id_user=0):
    if id_user == 0:
        result = {'users': users.get_users()}
    else:
        result = {'user': users.get_user_data(id_user)}
    return result


def delete_user(id_user):
    try:
        result = users.delete_user_data(id_user)
    except DatabaseError as dbe:
        return {'error' : str(dbe)}

    return result


def delete_user_companies(data): # scrap this?
    try:
        _email = data['email']
        _idcompanies = list(id['id'] for id in data['idcompanies'])
    except KeyError as ker:
        return {'error' : 'Invalid property ' + ker}

    try:
        users.delete_user_company(_email, _idcompanies)
    except DatabaseError as dbe:
        return {'error' : str(dbe)}

    return {'message' : "The user's associated companies have been cleared."}


def login(data):
    try:
        email = data['email']
        password = data['password']
    except KeyError as ker:
        return {'error' : 'Invalid property: ' + ker}

    user_check = users.check_user(email, password)
    result = None
    if '_error' in user_check:
        result = {'error' : 'A problem occurred during the login proccess.'}
    elif '_warning' in user_check:
        result = {'error': 'the credentials are not correct please check the email or password'}
    else:
        try:
            token = generate_token(email)
        except Exception as ex:
            return {'error' : 'A problem occurred during the login proccess.'}
        
        return {'token' : token, 'user' : user_check}


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
