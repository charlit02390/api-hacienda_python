# -*- coding: utf-8 -*-
import connexion
import json
from service import documents as service
from helpers import utils
from helpers.debugging import set_debug_mode

@set_debug_mode
def create_documents():
    body = json.loads(connexion.request.data)
    result = service.create_document(body['data'])
    return utils.build_response(result)


def processing_documents():
    body = json.loads(connexion.request.data)
    result = service.processing_documents(body['data']['id_compania'], body['data']['clave'],
                                          body['data']['es_consulta'])
    return utils.build_response(result)


def consult_documents():
    body = json.loads(connexion.request.data)
    result = service.consult_document_notdatabase(body['data']['id_compania'], body['data']['clave'],
                                          body['data']['tipo_documento'])
    return utils.build_response(result)


def get_documents_report():
    body = json.loads(connexion.request.data)
    result = service.document_report(body['data']['id_compania'], body['data']['tipo_documento'])
    return utils.build_response(result)


def route_get_vouchers(emisor=None, receptor=None, offset=None, limit=None):
    body = json.loads(connexion.request.data)
    result = service.consult_vouchers(body['data']['id_compania'], emisor, receptor, offset, limit)
    return utils.build_response(result)


def route_get_voucher_byid(clave):
    body = json.loads(connexion.request.data)
    result = service.consult_voucher_byid(body['data']['id_compania'], clave)
    return utils.build_response(result)

def get_pdf(key: str):
    result = service.get_pdf(key)
    return utils.build_response(result)
