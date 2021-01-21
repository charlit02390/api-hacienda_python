# -*- coding: utf-8 -*-
import re
import base64
import logging
import random
import requests
import json
import time
from . import fe_enums
from . import utils
from infrastructure import companies
from OpenSSL import crypto
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from helpers.errors.exceptions import InputError
from helpers.errors.enums import InputErrorCodes

try:
    from lxml import etree
except ImportError:
    from xml.etree import ElementTree

try:
    from OpenSSL import crypto
except(ImportError, IOError) as err:
    logging.info(err)

from .xades.context2 import XAdESContext2, PolicyId2, create_xades_epes_signature

_logger = logging.getLogger(__name__)


def get_consecutivo_hacienda(tipo_documento, consecutivo, sucursal_id,
                             terminal_id):  # duped in api_facturae and not used
    tipo_doc = fe_enums.TipoDocumento[tipo_documento].value

    inv_consecutivo = str(consecutivo).zfill(10)
    inv_sucursal = str(sucursal_id).zfill(3)
    inv_terminal = str(terminal_id).zfill(5)

    consecutivo_mh = inv_sucursal + inv_terminal + tipo_doc + inv_consecutivo

    return consecutivo_mh


# '''Variables para poder manejar el Refrescar del Token# '''
last_tokens = {}
last_tokens_time = {}
last_tokens_expire = {}
last_tokens_refresh = {}


# Funcion para enviar el XML al Ministerio de Hacienda
def send_xml(inv, token, date, tipo_ambiente):  # sorta duped in api_facturae? This one is not used.
    headers = {'Authorization': 'Bearer ' +
                                token, 'Content-type': 'application/json'}

    # establecer el ambiente al cual me voy a conectar
    endpoint = fe_enums.UrlHaciendaRecepcion[tipo_ambiente].value

    xml_base64 = utils.stringToBase64(inv.xml_comprobante)

    data = {'clave': inv.number_electronic,
            'fecha': date,
            'emisor': {
                'tipoIdentificacion': inv.company_id.identification_id.code,
                'numeroIdentificacion': inv.company_id.vat
            },
            'receptor': {
                'tipoIdentificacion': inv.partner_id.identification_id.code,
                'numeroIdentificacion': inv.partner_id.vat
            },
            'comprobanteXml': xml_base64
            }

    json_hacienda = json.dumps(data)

    try:
        #  enviando solicitud post y guardando la respuesta como un objeto json
        response = requests.request(
            "POST", endpoint, data=json_hacienda, headers=headers)

        # Verificamos el codigo devuelto, si es distinto de 202 es porque hacienda nos está devolviendo algun error
        if response.status_code != 202:
            error_caused_by = response.headers.get(
                'X-Error-Cause') if 'X-Error-Cause' in response.headers else ''
            error_caused_by += response.headers.get('validation-exception', '')
            _logger.info('Status: {}, Text {}'.format(
                response.status_code, error_caused_by))

            return {'status': response.status_code, 'text': error_caused_by}
        else:
            # respuesta_hacienda = response.status_code
            return {'status': response.status_code, 'text': response.reason}
            # return respuesta_hacienda

    except ImportError:
        raise Warning('Error enviando el XML al Ministerior de Hacienda')


# Obtener Attachments para las Facturas Electrónicas
def get_invoice_attachments(invoice, record_id):  # duped in api_facturae and not used
    attachments = []

    attachment = invoice.env['ir.attachment'].search(
        [('res_model', '=', 'account.invoice'), ('res_id', '=', record_id),
         ('res_field', '=', 'xml_comprobante')], limit=1)

    if attachment.id:
        attachment.name = invoice.fname_xml_comprobante
        attachment.datas_fname = invoice.fname_xml_comprobante
        attachments.append(attachment.id)

    attachment_resp = invoice.env['ir.attachment'].search(
        [('res_model', '=', 'account.invoice'), ('res_id', '=', record_id),
         ('res_field', '=', 'xml_respuesta_tributacion')], limit=1)

    if attachment_resp.id:
        attachment_resp.name = invoice.fname_xml_respuesta_tributacion
        attachment_resp.datas_fname = invoice.fname_xml_respuesta_tributacion
        attachments.append(attachment_resp.id)

    return attachments


def consulta_clave(clave, token, tipo_ambiente):  # duped in api_facturae...
    endpoint = fe_enums.UrlHaciendaRecepcion[tipo_ambiente].value + clave

    headers = {
        'Authorization': 'Bearer {}'.format(token),
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Postman-Token': 'bf8dc171-5bb7-fa54-7416-56c5cda9bf5c'
    }

    _logger.error('MAB - consulta_clave - url: %s' % endpoint)

    try:
        # response = requests.request("GET", url, headers=headers)
        response = requests.get(endpoint, headers=headers)
        ############################
    except requests.exceptions.RequestException as e:
        _logger.error('Exception %s' % e)
        return {'status': -1, 'text': 'Excepcion %s' % e}

    if 200 <= response.status_code <= 299:
        response_json = {
            'status': 200,
            'ind-estado': response.json().get('ind-estado'),
            'respuesta-xml': response.json().get('respuesta-xml')
        }
    elif 400 <= response.status_code <= 499:
        response_json = {'status': 400, 'ind-estado': 'error'}
    else:
        _logger.error('MAB - consulta_clave failed.  error: %s',
                      response.status_code)
        response_json = {'status': response.status_code,
                         'text': 'token_hacienda failed: %s' % response.reason}
    return response_json


def send_message(inv, date_cr, token, env):  # duped in api_facturae and not used.
    endpoint = fe_enums.UrlHaciendaRecepcion[env].value

    comprobante = {}
    comprobante['clave'] = inv.number_electronic
    comprobante['consecutivoReceptor'] = inv.consecutive_number_receiver
    comprobante["fecha"] = date_cr
    vat = re.sub('[^0-9]', '', inv.partner_id.vat)
    comprobante['emisor'] = {}
    comprobante['emisor']['tipoIdentificacion'] = inv.partner_id.identification_id.code
    comprobante['emisor']['numeroIdentificacion'] = vat
    comprobante['receptor'] = {}
    comprobante['receptor']['tipoIdentificacion'] = inv.company_id.identification_id.code
    comprobante['receptor']['numeroIdentificacion'] = inv.company_id.vat

    comprobante['comprobanteXml'] = inv.xml_comprobante
    _logger.info('MAB - Comprobante : %s' % comprobante)
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer {}'.format(token)}
    _logger.info('MAB - URL : %s' % endpoint)
    _logger.info('MAB - Headers : %s' % headers)

    try:
        response = requests.post(
            endpoint, data=json.dumps(comprobante), headers=headers)

    except requests.exceptions.RequestException as e:
        _logger.info('Exception %s' % e)
        return {'status': 400, 'text': u'Excepción de envio XML'}
        # raise Exception(e)

    if not (200 <= response.status_code <= 299):
        _logger.error('MAB - ERROR SEND MESSAGE - RESPONSE:%s' %
                      response.headers.get('X-Error-Cause', 'Unknown'))
        return {'status': response.status_code, 'text': response.headers.get('X-Error-Cause', 'Unknown')}
    else:
        return {'status': response.status_code, 'text': response.text}


def p12_expiration_date(p12file, password):
    try:
        pkcs12 = crypto.load_pkcs12(p12file, password)
        data = crypto.dump_certificate(crypto.FILETYPE_PEM, pkcs12.get_certificate())
        cert = x509.load_pem_x509_certificate(data, default_backend())
        return cert.not_valid_after
    except crypto.Error as crypte:
        excStr = str(crypte)
        if excStr.find('mac verify failure'):
            raise InputError(status=InputErrorCodes.P12_PIN_MISMATCH) from crypte
        else:
            raise
