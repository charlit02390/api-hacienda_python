import json
import base64
from service import utils_mh
from infrastructure import companies
from infrastructure.dbadapter import DatabaseError


def create_company(data, file, logo):
    # verify company first, 'cuz can't save a company that already exists.
    try:
        _company_user = data['id_compania']
    except KeyError as ker:
        return {'error' : 'Invalid property: ' + str(ker)} 

    company_exists = True
    try:
        company_exists = companies.verify_company(_company_user)
    except DatabaseError as dbe:
        return {'error' : str(dbe)}

    if company_exists:
        return {'error' : 'The company with ID: ' + _company_user + ' is already registered.'}

    # get the company data
    try:    
        _name = data['nombre_compania']
        _tradename = data['nombre_comercial']
        _type_identification = data['tipo_identificacion']
        _dni = data['cedula']
        _state = data['provincia']
        _county = data['canton']
        _district = data['distrito']
        _neighbor = data['barrio']
        _address = data['otras_senas']
        _phone_code = data['cod_telefono']
        _phone = data['telefono']
        _email = data['email']
        _activity_code = data['codigo_actividad']
        _user_mh = data['usuario_hacienda']
        _pass_mh = data['password_hacienda']
        _pin = data['pin']
        _env = data['ambiente']
        _is_active = data['estado']
    except KeyError as ker:
        return {'error' : 'Invalid property: ' + str(ker)}

    _signature = base64.b64encode(file)
    _logo = base64.b64encode(logo)
    
    _expiration_date = utils_mh.p12_expiration_date(file, _pin)
    if isinstance(_expiration_date,dict) and 'error' in _expiration_date:
        return _expiration_date # change this to a nice user message


    try:
        result = companies.create_company(_company_user, _name, _tradename, _type_identification, _dni, _state, _county,
                                          _district, _neighbor, _address, _phone_code, _phone, _email, _activity_code,
                                          _is_active, _user_mh, _pass_mh, _signature, _logo,_pin, _env,
                                          _expiration_date)
    except DatabaseError as dbe:
        return {'error' : str(dbe)}

    return {'message': 'company created successfully!'}


def get_list_companies(id_company=0):
    if id_company == 0:
        result = {'companies': companies.get_companies()}
    else:
        result = {'company': companies.get_company_data(id_company)}
    return result


def delete_company(id_company):
    result = companies.delete_company_data(id_company)
    return result


def modify_company(data, file, logo):
    try:
        _company_user = data['id_compania']
        _name = data['nombre_compania']
        _tradename = data['nombre_comercial']
        _type_identification = data['tipo_identificacion']
        _dni = data['cedula']
        _state = data['provincia']
        _county = data['canton']
        _district = data['distrito']
        _neighbor = data['barrio']
        _address = data['otras_senas']
        _phone_code = data['cod_telefono']
        _phone = data['telefono']
        _email = data['email']
        _activity_code = data['codigo_actividad']
        _user_mh = data['usuario_hacienda']
        _pass_mh = data['password_hacienda']
        _pin = data['pin']
        _env = data['ambiente']
        _is_active = data['estado']
    except KeyError as ker:
        return {'error' : 'Invalid property: ' + str(ker)}

    _signature = base64.b64encode(file)
    _logo = base64.b64encode(logo)

    _expiration_date = utils_mh.p12_expiration_date(file, _pin)
    if isinstance(_expiration_date, dict) and 'error' in _expiration_date:
        return _expiration_date # return nice user message instead.

    try:
        result = companies.modify_company(_company_user, _name, _tradename, _type_identification, _dni, _state, _county,
                                      _district, _neighbor, _address, _phone_code, _phone, _email, _activity_code,
                                      _is_active, _user_mh, _pass_mh, _signature, _logo, _pin, _env, _expiration_date)
    except DatabaseError as dbe:
        return {'error' : str(dbe)}

    return {'message': 'company modified successfully!'}
