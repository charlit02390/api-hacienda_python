import json
import base64
from infrastructure import companies


def create_company(data, file):
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
    _pin = data['pin']
    _env = data['ambiente']

    result = companies.create_company(_company_user, _name, _tradename, _type_identification, _dni, _state, _county,
                                      _district, _neighbor, _address, _phone_code, _phone, _email, _activity_code)

    result_mh = companies.save_mh_data(_company_user, _user_mh, _pass_mh, _signature, _pin, _env)

    if result is not True:
        return result
    elif result_mh is not True:
        return result_mh
    else:
        return {'message': 'company created successfully!'}


def get_list_companies(id_company=0):
    if id_company == 0:
        result = {'companies': companies.get_companies()}
    else:
        result = {'company': companies.get_company_data(id_company)}
    return result
