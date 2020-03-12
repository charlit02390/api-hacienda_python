import json
from infrastructure import users


def create_user(data):
    _email = data['email']
    _password = data['password']
    _name = data['name']
    _idrol = data['idrol']
    _idcompanies = data['idcompanies']
    # _idlist = []                        #TODO: CAMBIAR EL METODO DE PASAR DE ARRAY JSON A ARRAY
    # for id in _idcompanies:
    #    _idcompany = id['id']
    #    _idlist.append(_idcompany)

    result = users.save_user(_email, _password, _name, _idrol, _idcompanies)

    return result


def modify_user(data):
    _email = data['email']
    _password = data['password']
    _name = data['name']
    _idrol = data['idrol']
    _idcompanies = data['idcompanies']
    # _idlist = []                        #TODO: CAMBIAR EL METODO DE PASAR DE ARRAY JSON A ARRAY
    # for id in _idcompanies:
    #    _idcompany = id['id']
    #    _idlist.append(_idcompany)

    result = users.modify_user(_email, _password, _name, _idrol, _idcompanies)

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
