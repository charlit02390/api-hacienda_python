import json
import base64
from service import utils_mh
from infrastructure import companies


def create_company(data, file, logo):
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
    _signature = base64.b64encode(file)
    _logo = base64.b64encode(logo)
    _pin = data['pin']
    _env = data['ambiente']
    _is_active = data['estado']
    _expiration_date = utils_mh.p12_expiration_date(file, _pin)

    company_exist = companies.verify_company(_company_user)

    if not company_exist:
        result = companies.create_company(_company_user, _name, _tradename, _type_identification, _dni, _state, _county,
                                          _district, _neighbor, _address, _phone_code, _phone, _email, _activity_code
                                          , _is_active)

        result_mh = companies.save_mh_data(_company_user, _user_mh, _pass_mh, _signature, _logo,
                                           _pin, _env, _expiration_date)

        if result is not True:
            return result
        elif result_mh is not True:
            return result_mh
        else:
            return {'message': 'company created successfully!'}
    else:
        return {'message': 'company already exists'}


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
    _signature = base64.b64encode(file)
    _logo = base64.b64encode(logo)
    _pin = data['pin']
    _env = data['ambiente']
    _is_active = data['estado']
    _expiration_date = utils_mh.p12_expiration_date(file, _pin)

    result = companies.modify_company(_company_user, _name, _tradename, _type_identification, _dni, _state, _county,
                                      _district, _neighbor, _address, _phone_code, _phone, _email, _activity_code
                                      , _is_active)

    result_mh = companies.modify_mh_data(_company_user, _user_mh, _pass_mh, _signature, _logo,
                                         _pin, _env,_expiration_date)

    if result is not True and result_mh is not True:
        return result
    else:
        return {'message': 'company modify successfully!'}
