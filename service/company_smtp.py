import json
from infrastructure import company_smtp
from infrastructure import companies
from infrastructure.dbadapter import DbAdapterError
from helpers import errors
from flask import g
from helpers.errors.enums import InputErrorCodes
from helpers.errors.exceptions import InputError
from helpers.utils import build_response_data

def save_company_smtp(data, id_company):
    _host = data['host']
    _user = data['user']
    _password = data['password']
    _port = data['port']
    _encrypt_type = data['encrypt_type']
    _sender = data['sender']

    company_exists = companies.verify_company(id_company)

    if not company_exists:
        raise InputError('Company', str(id_company), status=InputErrorCodes.NO_RECORD_FOUND)

    company_smtp_exists = company_smtp.verify_company_smtp(id_company)

    if company_smtp_exists:
        raise InputError(status=InputErrorCodes.DUPLICATE_RECORD,
                         message="The company already has SMTP data.")

    company_smtp.save_company_smtp(_host, _user, _password, _port,
                                   _encrypt_type, id_company, _sender)

    return build_response_data({'message' : 'SMTP data created successfully'})


def get_company_smtp(id_company):
    result = {'data':{'smtp': company_smtp.get_company_smtp(id_company)}}
    return build_response_data(result)


def delete_company_smtp(id_company):
    company_smtp.delete_company_smtp(id_company)
    return build_response_data({'message' : "The company's SMTP has been deleted."})


def modify_company_smtp(data, id_company):
    _host = data['host']
    _user = data['user']
    _password = data['password']
    _port = data['port']
    _encrypt_type = data['encrypt_type']
    _sender = data['sender']

    company_smtp_exists = company_smtp.verify_company_smtp(id_company)

    if not company_smtp_exists:
        raise InputError(status=InputErrorCodes.NO_RECORD_FOUND, message="The company doesn't have SMTP data to be updated.")

    company_smtp.modify_company_smtp(_host, _password, _user, _port,
                                     _encrypt_type, id_company, _sender)

    return build_response_data({'message' : "The company's SMTP was successfully updated."})
