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


try:
    from lxml import etree
except ImportError:
    from xml.etree import ElementTree

try:
    from OpenSSL import crypto
except(ImportError, IOError) as err:
    logging.info( err )

from .xades.context2 import XAdESContext2, PolicyId2, create_xades_epes_signature

_logger = logging.getLogger( __name__ )


def get_consecutivo_hacienda(tipo_documento, consecutivo, sucursal_id, terminal_id):
    tipo_doc = fe_enums.TipoDocumento[tipo_documento].value

    inv_consecutivo = str( consecutivo ).zfill( 10 )
    inv_sucursal = str( sucursal_id ).zfill( 3 )
    inv_terminal = str( terminal_id ).zfill( 5 )

    consecutivo_mh = inv_sucursal + inv_terminal + tipo_doc + inv_consecutivo

    return consecutivo_mh


def get_clave_hacienda(self, tipo_documento, consecutivo, sucursal_id, terminal_id, situacion='normal'):
    tipo_doc = fe_enums.TipoDocumento[tipo_documento].value

    # '''Verificamos si el consecutivo indicado corresponde a un numero# '''
    inv_consecutivo = re.sub( '[^0-9]', '', consecutivo )
    if len( inv_consecutivo ) != 10:
       return ( 'La numeración debe de tener 10 dígitos' )

    # '''Verificamos la sucursal y terminal# '''
    inv_sucursal = re.sub( '[^0-9]', '', str( sucursal_id ) ).zfill( 3 )
    inv_terminal = re.sub( '[^0-9]', '', str( terminal_id ) ).zfill( 5 )

    # '''Armamos el consecutivo pues ya tenemos los datos necesarios# '''
    consecutivo_mh = inv_sucursal + inv_terminal + tipo_doc + inv_consecutivo

    if not self.company_id.identification_id:
       return(
            'Seleccione el tipo de identificación del emisor en el pérfil de la compañía' )

    # '''Obtenemos el número de identificación del Emisor y lo validamos númericamente# '''
    inv_cedula = re.sub( '[^0-9]', '', self.company_id.vat )

    # '''Validamos el largo de la cadena númerica de la cédula del emisor# '''
    if self.company_id.identification_id.code == '01' and len( inv_cedula ) != 9:
        return( 'La Cédula Física del emisor debe de tener 9 dígitos' )
    elif self.company_id.identification_id.code == '02' and len( inv_cedula ) != 10:
        return(
            'La Cédula Jurídica del emisor debe de tener 10 dígitos' )
    elif self.company_id.identification_id.code == '03' and (len( inv_cedula ) != 11 or len( inv_cedula ) != 12):
        return(
            'La identificación DIMEX del emisor debe de tener 11 o 12 dígitos' )
    elif self.company_id.identification_id.code == '04' and len( inv_cedula ) != 10:
        return(
            'La identificación NITE del emisor debe de tener 10 dígitos' )
    inv_cedula = str( inv_cedula ).zfill( 12 )

    # '''Limitamos la cedula del emisor a 20 caracteres o nos dará error# '''
    cedula_emisor = utils.limit( inv_cedula, 20 )

    # '''Validamos la situación del comprobante electrónico# '''
    situacion_comprobante = fe_enums.SituacionComprobante[ situacion ].value
    if not situacion_comprobante:
        return(
            'La situación indicada para el comprobante electŕonico es inválida: ' + situacion )

    # '''Creamos la fecha para la clave# '''

    cur_date = utils.get_time_hacienda('F')

    codigo_pais = self.company_id.phone_code

    # '''Creamos un código de seguridad random# '''
    codigo_seguridad = str( random.randint( 1, 99999999 ) ).zfill( 8 )

    clave_hacienda = codigo_pais + cur_date + cedula_emisor + \
                     consecutivo_mh + situacion_comprobante + codigo_seguridad

    return {'length': len( clave_hacienda ), 'clave': clave_hacienda, 'consecutivo': consecutivo_mh}


# '''Variables para poder manejar el Refrescar del Token# '''
last_tokens = {}
last_tokens_time = {}
last_tokens_expire = {}
last_tokens_refresh = {}


def get_token_hacienda(data):

    global last_tokens
    global last_tokens_time
    global last_tokens_expire
    global last_tokens_refresh
    _user_api = data['compania_id']
    result_mh = companies.get_mh_data( _user_api )
    _dni = result_mh[0][0]
    _mh_user = result_mh[0][1]
    _mh_pass = result_mh[0][2]
    _env = result_mh[0][5]

    token = last_tokens.get( _dni, False )
    token_time = last_tokens_time.get(_dni, False )
    token_expire = last_tokens_expire.get( _dni, 0 )
    current_time = time.time()

    if token and (current_time - token_time < token_expire - 10):
        token_hacienda = token
    else:
        headers = {}
        data = {'client_id': _env ,
                'client_secret': '',
                'grant_type': 'password',
                'username': _mh_user,
                'password': _mh_pass
                }

        # establecer el ambiente al cual me voy a conectar
        endpoint = fe_enums.UrlHaciendaToken[_env]

        try:
            # enviando solicitud post y guardando la respuesta como un objeto json
            response = requests.request(
                "POST", endpoint, data=data, headers=headers )
            response_json = response.json()

            if 200 <= response.status_code <= 299:
                token_hacienda = response_json.get( 'access_token' )
                last_tokens[_dni] = token
                last_tokens_time[_dni] = time.time()
                last_tokens_expire[_dni] = response_json.get( 'expires_in' )
                last_tokens_refresh[_dni] = response_json.get( 'refresh_expires_in' )
            else:
                _logger.error(
                    'MAB - token_hacienda failed.  error: %s', response.status_code )

        except requests.exceptions.RequestException as e:
            raise Warning(
                'Error Obteniendo el Token desde MH. Excepcion %s' % e )

    return json.dumps({'token':token_hacienda })


def refresh_token_hacienda(tipo_ambiente, token):
    headers = {}
    data = {'client_id': tipo_ambiente,
            'client_secret': '',
            'grant_type': 'refresh_token',
            'refresh_token': token
            }

    # establecer el ambiente al cual me voy a conectar
    endpoint = fe_enums.UrlHaciendaToken[tipo_ambiente]

    try:
        # enviando solicitud post y guardando la respuesta como un objeto json
        response = requests.request(
            "POST", endpoint, data=data, headers=headers )
        response_json = response.json()
        token_hacienda = response_json.get( 'access_token' )
        return token_hacienda
    except ImportError:
        raise Warning( 'Error Refrescando el Token desde MH' )


def sign_xml(data):
    _user_api = data['compania_id']
    xml_encode = data['xml']
    policy_id = 'https://www.hacienda.go.cr/ATV/ComprobanteElectronico/docs/esquemas/2016/v4.2' \
                '/ResolucionComprobantesElectronicosDGT-R-48-2016_4.2.pdf'

    result_mh = companies.get_mh_data(_user_api)
    _pin = result_mh[0][4]
    _signature = result_mh[0][3]

    xml = base64.b64decode(xml_encode)

    root = etree.fromstring(xml)
    signature = create_xades_epes_signature()

    policy = PolicyId2()
    policy.id = policy_id

    root.append(signature)
    ctx = XAdESContext2(policy)
    certificate = crypto.load_pkcs12(_signature, _pin)
    ctx.load_pkcs12(certificate)
    ctx.sign(signature)

    xml_firmado = base64.b64encode(etree.tostring( root, encoding='UTF-8', method='xml', xml_declaration=True, with_tail=False)).decode('UTF-8')

    return json.dumps({'xml-firmado':xml_firmado })


# Funcion para enviar el XML al Ministerio de Hacienda
def send_xml(inv, token, date, tipo_ambiente):
    headers = {'Authorization': 'Bearer ' +
                                token, 'Content-type': 'application/json'}

    # establecer el ambiente al cual me voy a conectar
    endpoint = fe_enums.UrlHaciendaRecepcion[tipo_ambiente].value

    xml_base64 = utils.stringToBase64( inv.xml_comprobante )

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

    json_hacienda = json.dumps( data )

    try:
        #  enviando solicitud post y guardando la respuesta como un objeto json
        response = requests.request(
            "POST", endpoint, data=json_hacienda, headers=headers )

        # Verificamos el codigo devuelto, si es distinto de 202 es porque hacienda nos está devolviendo algun error
        if response.status_code != 202:
            error_caused_by = response.headers.get(
                'X-Error-Cause' ) if 'X-Error-Cause' in response.headers else ''
            error_caused_by += response.headers.get( 'validation-exception', '' )
            _logger.info( 'Status: {}, Text {}'.format(
                response.status_code, error_caused_by ) )

            return {'status': response.status_code, 'text': error_caused_by}
        else:
            # respuesta_hacienda = response.status_code
            return {'status': response.status_code, 'text': response.reason}
            # return respuesta_hacienda

    except ImportError:
        raise Warning( 'Error enviando el XML al Ministerior de Hacienda' )


# Obtener Attachments para las Facturas Electrónicas
def get_invoice_attachments(invoice, record_id):
    attachments = []

    attachment = invoice.env['ir.attachment'].search(
        [('res_model', '=', 'account.invoice'), ('res_id', '=', record_id),
         ('res_field', '=', 'xml_comprobante')], limit=1 )

    if attachment.id:
        attachment.name = invoice.fname_xml_comprobante
        attachment.datas_fname = invoice.fname_xml_comprobante
        attachments.append( attachment.id )

    attachment_resp = invoice.env['ir.attachment'].search(
        [('res_model', '=', 'account.invoice'), ('res_id', '=', record_id),
         ('res_field', '=', 'xml_respuesta_tributacion')], limit=1 )

    if attachment_resp.id:
        attachment_resp.name = invoice.fname_xml_respuesta_tributacion
        attachment_resp.datas_fname = invoice.fname_xml_respuesta_tributacion
        attachments.append( attachment_resp.id )

    return attachments

def consulta_clave(clave, token, tipo_ambiente):
    endpoint = fe_enums.UrlHaciendaRecepcion[tipo_ambiente].value + clave

    headers = {
        'Authorization': 'Bearer {}'.format( token ),
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Postman-Token': 'bf8dc171-5bb7-fa54-7416-56c5cda9bf5c'
    }

    _logger.error( 'MAB - consulta_clave - url: %s' % endpoint )

    try:
        # response = requests.request("GET", url, headers=headers)
        response = requests.get( endpoint, headers=headers )
        ############################
    except requests.exceptions.RequestException as e:
        _logger.error( 'Exception %s' % e )
        return {'status': -1, 'text': 'Excepcion %s' % e}

    if 200 <= response.status_code <= 299:
        response_json = {
            'status': 200,
            'ind-estado': response.json().get( 'ind-estado' ),
            'respuesta-xml': response.json().get( 'respuesta-xml' )
        }
    elif 400 <= response.status_code <= 499:
        response_json = {'status': 400, 'ind-estado': 'error'}
    else:
        _logger.error( 'MAB - consulta_clave failed.  error: %s',
                       response.status_code )
        response_json = {'status': response.status_code,
                         'text': 'token_hacienda failed: %s' % response.reason}
    return response_json


def consulta_documentos(self, inv, env, token_m_h, date_cr, xml_firmado):
    if inv.type == 'in_invoice' or inv.type == 'in_refund':
        if not inv.consecutive_number_receiver:
            if len( inv.number ) == 20:
                inv.consecutive_number_receiver = inv.number
            else:
                if inv.state_invoice_partner == '1':
                    tipo_documento = 'CCE'
                elif inv.state_invoice_partner == '2':
                    tipo_documento = 'CPCE'
                else:
                    tipo_documento = 'RCE'
                response_json = get_clave_hacienda(
                    self, tipo_documento, inv.number, inv.journal_id.sucursal, inv.journal_id.terminal )
                inv.consecutive_number_receiver = response_json.get(
                    'consecutivo' )

        clave = inv.number_electronic + "-" + inv.consecutive_number_receiver
    else:
        clave = inv.number_electronic

    response_json = consulta_clave( clave, token_m_h, env )
    _logger.debug( response_json )
    estado_m_h = response_json.get( 'ind-estado' )

    if (not xml_firmado) and (not date_cr):
        self.message_post( body='<p>Ha realizado la consulta a Haciendo de:'
                                + '<br /><b>Documento: </b>' + payload['clave']
                                + '<br /><b>Estado del documento: </b>' + estado_m_h + '</p>',
                           subtype='mail.mt_note',
                           content_subtype='html' )

    # Siempre sin importar el estado se actualiza la fecha de acuerdo a la devuelta por Hacienda y
    # se carga el xml devuelto por Hacienda
    last_state = inv.state_send_invoice
    if inv.type == 'out_invoice' or inv.type == 'out_refund':
        # Se actualiza el estado con el que devuelve Hacienda
        inv.state_tributacion = estado_m_h
        inv.date_issuance = date_cr
        inv.fname_xml_comprobante = 'comprobante_' + inv.number_electronic + '.xml'
        inv.xml_comprobante = xml_firmado
    elif inv.type == 'in_invoice' or inv.type == 'in_refund':
        inv.fname_xml_comprobante = 'receptor_' + inv.number_electronic + '.xml'
        inv.xml_comprobante = xml_firmado
        inv.state_send_invoice = estado_m_h

    # Si fue aceptado o rechazado por haciendo se carga la respuesta
    if (estado_m_h == 'aceptado' or estado_m_h == 'rechazado') or (
            inv.type == 'out_invoice' or inv.type == 'out_refund'):
        inv.fname_xml_respuesta_tributacion = 'respuesta_' + inv.number_electronic + '.xml'
        inv.xml_respuesta_tributacion = response_json.get( 'respuesta-xml' )

    # Si fue aceptado por Hacienda y es un factura de cliente o nota de crédito, se envía el correo con los documentos
    if inv.state_send_invoice == 'aceptado' and (last_state is False or last_state == 'procesando'):
        # if not inv.partner_id.opt_out:
        if inv.type == 'in_invoice' or inv.type == 'in_refund':
            email_template = self.env.ref(
                'cr_electronic_invoice.email_template_invoice_vendor', False )
        else:
            email_template = self.env.ref(
                'account.email_template_edi_invoice', False )

            # attachment_resp = self.env['ir.attachment'].search(
            #    [('res_model', '=', 'account.invoice'), ('res_id', '=', inv.id),
            #     ('res_field', '=', 'xml_respuesta_tributacion')], limit=1)
            # attachment_resp.name = inv.fname_xml_respuesta_tributacion
            # attachment_resp.datas_fname = inv.fname_xml_respuesta_tributacion

        attachments = []

        attachment = self.env['ir.attachment'].search(
            [('res_model', '=', 'account.invoice'), ('res_id', '=', inv.id),
             ('res_field', '=', 'xml_comprobante')], limit=1 )

        if attachment.id:
            attachment.name = inv.fname_xml_comprobante
            attachment.datas_fname = inv.fname_xml_comprobante
            attachments.append( attachment.id )

        attachment_resp = self.env['ir.attachment'].search(
            [('res_model', '=', 'account.invoice'), ('res_id', '=', inv.id),
             ('res_field', '=', 'xml_respuesta_tributacion')], limit=1 )

        if attachment_resp.id:
            attachment_resp.name = inv.fname_xml_respuesta_tributacion
            attachment_resp.datas_fname = inv.fname_xml_respuesta_tributacion
            attachments.append( attachment_resp.id )

        if len( attachments ) == 2:
            email_template.attachment_ids = [(6, 0, attachments)]

            email_template.with_context( type='binary', default_type='binary' ).send_mail( inv.id,
                                                                                           raise_exception=False,
                                                                                           force_send=True )  # default_type='binary'

            # limpia el template de los attachments
            email_template.attachment_ids = [(5)]


def send_message(inv, date_cr, token, env):
    endpoint = fe_enums.UrlHaciendaRecepcion[env].value

    comprobante = {}
    comprobante['clave'] = inv.number_electronic
    comprobante['consecutivoReceptor'] = inv.consecutive_number_receiver
    comprobante["fecha"] = date_cr
    vat = re.sub( '[^0-9]', '', inv.partner_id.vat )
    comprobante['emisor'] = {}
    comprobante['emisor']['tipoIdentificacion'] = inv.partner_id.identification_id.code
    comprobante['emisor']['numeroIdentificacion'] = vat
    comprobante['receptor'] = {}
    comprobante['receptor']['tipoIdentificacion'] = inv.company_id.identification_id.code
    comprobante['receptor']['numeroIdentificacion'] = inv.company_id.vat

    comprobante['comprobanteXml'] = inv.xml_comprobante
    _logger.info( 'MAB - Comprobante : %s' % comprobante )
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer {}'.format( token )}
    _logger.info( 'MAB - URL : %s' % endpoint )
    _logger.info( 'MAB - Headers : %s' % headers )

    try:
        response = requests.post(
            endpoint, data=json.dumps( comprobante ), headers=headers )

    except requests.exceptions.RequestException as e:
        _logger.info( 'Exception %s' % e )
        return {'status': 400, 'text': u'Excepción de envio XML'}
        # raise Exception(e)

    if not (200 <= response.status_code <= 299):
        _logger.error( 'MAB - ERROR SEND MESSAGE - RESPONSE:%s' %
                       response.headers.get( 'X-Error-Cause', 'Unknown' ) )
        return {'status': response.status_code, 'text': response.headers.get( 'X-Error-Cause', 'Unknown' )}
    else:
        return {'status': response.status_code, 'text': response.text}


def p12_expiration_date(p12file,password):

    try:
        pkcs12 = crypto.load_pkcs12(p12file, password)
        data = crypto.dump_certificate(crypto.FILETYPE_PEM, pkcs12.get_certificate())
        cert = x509.load_pem_x509_certificate(data, default_backend())
        return cert.not_valid_after
    except Exception as e:
        return {'error': str(e)}
