# -*- coding: utf-8 -*-
import connexion
import json
from service import documents as service


def create_documents():
    body = json.loads(connexion.request.data)
    result = service.create_document(body['data'])
    return result


def consult_document_company(company_id,key):
    result = service.consult_document(company_id, key)
    return result


def validate_document_company(company_id,key):
    result = service.validate_document(company_id, key)
    return result


def consult_documents():
    return "Entro";
