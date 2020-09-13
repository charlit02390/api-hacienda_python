import json
from infrastructure import company_smtp
from infrastructure import companies
from infrastructure.dbadapter import DatabaseError


def save_company_smtp(data, id_company):
    try:
        _host = data['host']
        _user = data['user']
        _password = data['password']
        _port = data['port']
        _encrypt_type = data['encrypt_type']
    except KeyError as ker:
        return {'error' : 'Invalid property: ' + ker}

    try:
        company_exists = companies.verify_company(id_company)
    except DatabaseError as dbe:
        return {'error' : str(dbe)}

    if not company_exists:
        return {'error' : "The specified company doesn't exist."}

    try:
        company_smtp_exists = company_smtp.verify_company_smtp(id_company)
    except DatabaseError as dbe:
        return {'error' : str(dbe)}

    if company_smtp_exists:
        return {'error' : "The company already has SMTP data."}

    try:
        company_smtp.save_company_smtp(_host, _user, _password, _port, _encrypt_type, id_company)
    except DatabaseError as dbe:
        return {'error' : str(dbe)}

    return {'message' : 'SMTP data created successfully'}


def get_company_smtp(id_company):
    result = {'smtp': company_smtp.get_company_smtp(id_company)}
    return result


def delete_company_smtp(id_company):
    try:
        result = company_smtp.delete_company_smtp(id_company)
    except DatabaseError as dbe:
        return {'error' : str(dbe)}

    return result


def modify_company_smtp(data, id_company):
    try:
        _host = data['host']
        _user = data['user']
        _password = data['password']
        _port = data['port']
        _encrypt_type = data['encrypt_type']
    except KeyError as ker:
        return {'error' : 'Invalid property: ' + str(ker)}

    try:
        company_smtp_exists = company_smtp.verify_company_smtp(id_company)
    except DatabaseError as dbe:
        return {'error' : str(dbe)}

    if not company_smtp_exists:
        return {'error' : "The company doesn't have SMTP data to be updated."}

    try:
        result = company_smtp.modify_company_smtp(_host, _password, _user, _port, _encrypt_type, id_company)
    except DatabaseError as dbe:
        return {'error' : str(dbe)}

    return result
