# -*- coding: utf-8 -*-
import connexion
import json
from service import documents as service


def create_documents():
    body = json.loads(connexion.request.data)
    result = service.create_document(body['data'])
    return result


def processing_documents():
    body = json.loads(connexion.request.data)
    result = service.processing_documents(body['data']['id_compania'], body['data']['clave'],
                                          body['data']['es_consulta'])
    return result


def get_documents_report():
    body = json.loads(connexion.request.data)
    result = service.document_report(body['data']['id_compania'], body['data']['tipo_documento'])
    return result


def route_get_vouchers(emisor=None, receptor=None, offset=None, limit=None):
    body = json.loads(connexion.request.data)
    result = service.consult_vouchers(body['data']['id_compania'], emisor, receptor, offset, limit)
    return result


def route_get_voucher_byid(clave):
    body = json.loads(connexion.request.data)
    result = service.consult_voucher_byid(body['data']['id_compania'], clave)
    return result
