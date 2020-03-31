import json
from infrastructure import company_smtp
from infrastructure import companies


def save_company_smtp(data, id_company):
    _host = data['host']
    _user = data['user']
    _password = data['password']
    _port = data['port']
    _encrypt_type = data['encrypt_type']

    company_exist = companies.verify_company(id_company)

    company_smtp_exist = company_smtp.verify_company_smtp(id_company)

    if company_exist:
        if not company_smtp_exist:
            result = company_smtp.save_company_smtp(_host, _user, _password, _port, _encrypt_type, id_company)
            if result:
                return {'message': 'smtp data saved successfully'}
            else:
                return {'error': 'smtp data can not be saved'}
        else:
            return {'error': 'company already have smtp data'}
    else:
        return {'error': 'the company not exist'}


def get_company_smtp(id_company):
    result = {'smtp': company_smtp.get_company_smtp(id_company)}
    return result


def delete_company_smtp(id_company):
    result = company_smtp.delete_company_smtp(id_company)
    return result


def modify_company_smtp(data, id_company):
    _host = data['host']
    _user = data['user']
    _password = data['password']
    _port = data['port']
    _encrypt_type = data['encrypt_type']

    company_smtp_exist = company_smtp.verify_company_smtp(id_company)

    if company_smtp_exist:
        result = company_smtp.modify_company_smtp(_host, _password, _user, _port, _encrypt_type, id_company)
        if result:
            return {'message': 'smtp data modify successfully'}
        else:
            return {'error': 'smtp data can not be modify'}
    else:
        return {'error': 'company do not have smtp data'}
