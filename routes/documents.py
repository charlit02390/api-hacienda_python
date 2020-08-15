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
    #TODO: Los primeros dos none son body['data']['id_compania'], body['data']['clave']
    result = service.consult_vouchers(None, None, emisor, receptor, offset, limit)
    return result


def route_get_voucher_byid(clave):
    # TODO: Los primeros dos none son body['data']['id_compania'], body['data']['clave']
    result = service.consult_voucher_byid(None, None, clave)
    return result
    print (clave)
    return {'1': '1'}