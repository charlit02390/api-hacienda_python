# -*- coding: utf-8 -*-

import requests
import datetime
import json
from . import fe_enums
import io
from io import BytesIO as StringIO
import re
import os
import base64
import pytz
import time
import logging
import random

from xml.sax.saxutils import escape
from .xades.context2 import XAdESContext2, PolicyId2, create_xades_epes_signature

from helpers.errors.enums import InternalErrorCodes
from helpers.errors.exceptions import ServerError, HaciendaError

try:
    from lxml import etree
except ImportError:
    from xml.etree import ElementTree

try:
    from OpenSSL import crypto
except(ImportError, IOError) as err:
    logging.info(err)

_logger = logging.getLogger(__name__)

NO_TAXCUT_DOC_TYPE = 'FEE'
NO_RETURNTAX_DOC_TYPES = (
    'FEC',
    'FEE'
)
INCLUDES_IVAFACTOR_TAX_CODE = '08'


def sign_xml(cert, password, xml,
             policy_id='https://www.hacienda.go.cr/ATV/ComprobanteElectronico/docs/esquemas/2016/v4.3/Resoluci%C3%B3n_General_sobre_disposiciones_t%C3%A9cnicas_comprobantes_electr%C3%B3nicos_para_efectos_tributarios.pdf'):
    root = etree.fromstring(xml)
    signature = create_xades_epes_signature()

    policy = PolicyId2()
    policy.id = policy_id

    root.append(signature)
    ctx = XAdESContext2(policy)
    certificate = crypto.load_pkcs12(base64.b64decode(cert), password)
    ctx.load_pkcs12(certificate)
    ctx.sign(signature)

    return etree.tostring(root, encoding='UTF-8', method='xml', xml_declaration=True, with_tail=False)


def get_time_hacienda(is_date=False):
    now_utc = datetime.datetime.now(pytz.timezone('UTC'))
    now_cr = now_utc.astimezone(pytz.timezone('America/Costa_Rica'))
    date_cr = now_cr.strftime("%Y-%m-%dT%H:%M:%S-06:00")
    if is_date:
        return now_cr
    else:
        return date_cr


# Utilizada para establecer un limite de caracteres en la cedula del cliente, no mas de 20
# de lo contrario hacienda lo rechaza
def limit(_str, _limit):
    return (_str[:_limit - 3] + '...') if len(_str) > _limit else _str


def get_mr_sequencevalue(inv):  # not used for now?
    #  Verificamos si el ID del mensaje receptor es válido
    mr_mensaje_id = int(inv.state_invoice_partner)
    if mr_mensaje_id < 1 or mr_mensaje_id > 3:
        return 'El ID del mensaje receptor es inválido.'
    elif mr_mensaje_id is None:
        return 'No se ha proporcionado un ID válido para el MR.'

    if inv.state_invoice_partner == '1':
        detalle_mensaje = 'Aceptado'
        tipo = 1
        tipo_documento = fe_enums.TipoDocumento['CCE']
        sequence = inv.env['ir.sequence'].next_by_code(
            'sequece.electronic.doc.confirmation')

    elif inv.state_invoice_partner == '2':
        detalle_mensaje = 'Aceptado parcial'
        tipo = 2
        tipo_documento = fe_enums.TipoDocumento['CPCE']
        sequence = inv.env['ir.sequence'].next_by_code(
            'sequece.electronic.doc.partial.confirmation')
    else:
        detalle_mensaje = 'Rechazado'
        tipo = 3
        tipo_documento = fe_enums.TipoDocumento['RCE']
        sequence = inv.env['ir.sequence'].next_by_code(
            'sequece.electronic.doc.reject')

    return {'detalle_mensaje': detalle_mensaje, 'tipo': tipo, 'tipo_documento': tipo_documento, 'sequence': sequence}


def get_consecutivo_hacienda(tipo_documento, consecutivo, sucursal_id,
                             terminal_id):  # duplicated in utils_mh? not used here
    tipo_doc = fe_enums.TipoDocumento[tipo_documento]

    inv_consecutivo = str(consecutivo).zfill(10)
    inv_sucursal = str(sucursal_id).zfill(3)
    inv_terminal = str(terminal_id).zfill(5)

    consecutivo_mh = inv_sucursal + inv_terminal + tipo_doc + inv_consecutivo

    return consecutivo_mh


def get_clave_hacienda(company_data, tipo_documento, consecutivo, sucursal_id, terminal_id,
                       situacion='normal'):  # duplicated in utils_mh?
    tipo_doc = fe_enums.TipoDocumento[tipo_documento]

    '''Verificamos si el consecutivo indicado corresponde a un numero'''
    inv_consecutivo = re.sub('[^0-9]', '', consecutivo)
    if len(inv_consecutivo) != 10:
        return 'La numeración debe de tener 10 dígitos'

    '''Verificamos la sucursal y terminal'''
    inv_sucursal = re.sub('[^0-9]', '', str(sucursal_id)).zfill(3)
    inv_terminal = re.sub('[^0-9]', '', str(terminal_id)).zfill(5)

    '''Armamos el consecutivo pues ya tenemos los datos necesarios'''
    consecutivo_mh = inv_sucursal + inv_terminal + tipo_doc + inv_consecutivo

    if not company_data['type_identification']:
        return (
            'Seleccione el tipo de identificación del emisor en el pérfil de la compañía')

    '''Obtenemos el número de identificación del Emisor y lo validamos númericamente'''
    inv_cedula = re.sub('[^0-9]', '', company_data['identification_dni'])

    '''Validamos el largo de la cadena númerica de la cédula del emisor'''
    if company_data['type_identification'] == '01' and len(inv_cedula) != 9:
        return 'La Cédula Física del emisor debe de tener 9 dígitos'
    elif company_data['type_identification'] == '02' and len(inv_cedula) != 10:
        return (
            'La Cédula Jurídica del emisor debe de tener 10 dígitos')
    elif company_data['type_identification'] == '03' and len(inv_cedula) not in (11, 12):
        return (
            'La identificación DIMEX del emisor debe de tener 11 o 12 dígitos')
    elif company_data['type_identification'] == '04' and len(inv_cedula) != 10:
        return (
            'La identificación NITE del emisor debe de tener 10 dígitos')

    inv_cedula = str(inv_cedula).zfill(12)

    '''Limitamos la cedula del emisor a 20 caracteres o nos dará error'''
    cedula_emisor = limit(inv_cedula, 20)

    '''Validamos la situación del comprobante electrónico'''
    situacion_comprobante = fe_enums.SituacionComprobante.get(situacion)
    if not situacion_comprobante:
        return (
                'La situación indicada para el comprobante electŕonico es inválida: ' + situacion)

    '''Creamos la fecha para la clave'''
    now_utc = datetime.datetime.now(pytz.timezone('UTC'))
    now_cr = now_utc.astimezone(pytz.timezone('America/Costa_Rica'))

    cur_date = now_cr.strftime("%d%m%y")

    codigo_pais = company_data['code_phone']

    '''Creamos un código de seguridad random'''
    codigo_seguridad = str(random.randint(1, 99999999)).zfill(8)

    clave_hacienda = ''.join((
        str(codigo_pais),
        cur_date,
        cedula_emisor,
        consecutivo_mh,
        situacion_comprobante,
        codigo_seguridad)
    )

    return {'length': len(clave_hacienda), 'clave': clave_hacienda, 'consecutivo': consecutivo_mh}


'''Variables para poder manejar el Refrescar del Token'''
last_tokens = {}
last_tokens_time = {}
last_tokens_expire = {}
last_tokens_refresh = {}


def get_token_hacienda(_company_id, _user_mh, _pass_mh, env):
    global last_tokens
    global last_tokens_time
    global last_tokens_expire
    global last_tokens_refresh

    token = last_tokens.get(_company_id, False)
    token_time = last_tokens_time.get(_company_id, False)
    token_expire = last_tokens_expire.get(_company_id, 0)
    current_time = time.time()

    if token and (current_time - token_time < token_expire - 10):
        token_hacienda = token
    else:
        headers = {}
        data = {'client_id': env,
                'client_secret': '',
                'grant_type': 'password',
                'username': _user_mh,
                'password': _pass_mh
                }

        # establecer el ambiente al cual me voy a conectar
        endpoint = fe_enums.UrlHaciendaToken[env]

        try:
            # enviando solicitud post y guardando la respuesta como un objeto json
            response = requests.request(
                "POST", endpoint, data=data, headers=headers)
            response_json = response.json()

            if 200 <= response.status_code <= 299:
                token_hacienda = response_json.get('access_token')
                last_tokens[_company_id] = token_hacienda
                last_tokens_time[_company_id] = time.time()
                last_tokens_expire[_company_id] = response_json.get('expires_in')
                last_tokens_refresh[_company_id] = response_json.get('refresh_expires_in')
            else:
                _logger.error(
                    'MAB - token_hacienda failed.  error: %s', response.status_code)
                raise Exception('MAB - token_hacienda failed.  error: %s' % response.status_code)

        except requests.exceptions.RequestException as e:
            raise Exception(
                'Error Obteniendo el Token desde MH. Excepcion %s' % e)

    return token_hacienda


def refresh_token_hacienda(tipo_ambiente, token):  # duplicated in utils_mh... how many more funcs are duplicated??
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
            "POST", endpoint, data=data, headers=headers)
        response_json = response.json()
        token_hacienda = response_json.get('access_token')
        return token_hacienda
    except ImportError:
        raise Exception('Error Refrescando el Token desde MH')


def gen_xml_mr_43(clave, cedula_emisor, fecha_emision, id_mensaje,
                  detalle_mensaje, cedula_receptor,
                  consecutivo_receptor,
                  monto_impuesto=0, total_factura=0,
                  codigo_actividad=False,
                  condicion_impuesto=False,
                  monto_total_impuesto_acreditar=False,
                  monto_total_gasto_aplicable=False):  # not used...
    #  Verificamos si la clave indicada corresponde a un numeros
    mr_clave = re.sub('[^0-9]', '', clave)
    if len(mr_clave) != 50:
        return (
            'La clave a utilizar es inválida. Debe contener al menos 50 digitos')

    #  Obtenemos el número de identificación del Emisor y lo validamos númericamente
    mr_cedula_emisor = re.sub('[^0-9]', '', cedula_emisor)
    if len(mr_cedula_emisor) != 12:
        mr_cedula_emisor = str(mr_cedula_emisor).zfill(12)
    elif mr_cedula_emisor is None:
        return 'La cédula del Emisor en el MR es inválida.'

    mr_fecha_emision = fecha_emision
    if mr_fecha_emision is None:
        return 'La fecha de emisión en el MR es inválida.'

    '''Verificamos si el ID del mensaje receptor es válido'''
    mr_mensaje_id = int(id_mensaje)
    if 1 > mr_mensaje_id > 3:
        return 'El ID del mensaje receptor es inválido.'
    elif mr_mensaje_id is None:
        return 'No se ha proporcionado un ID válido para el MR.'

    mr_cedula_receptor = re.sub('[^0-9]', '', cedula_receptor)
    if len(mr_cedula_receptor) != 12:
        mr_cedula_receptor = str(mr_cedula_receptor).zfill(12)
    elif mr_cedula_receptor is None:
        return (
            'No se ha proporcionado una cédula de receptor válida para el MR.')

    '''Verificamos si el consecutivo indicado para el mensaje receptor corresponde a numeros'''
    mr_consecutivo_receptor = re.sub('[^0-9]', '', consecutivo_receptor)
    if len(mr_consecutivo_receptor) != 20:
        return ('La clave del consecutivo para el mensaje receptor es inválida. '
                'Debe contener al menos 50 digitos')

    mr_monto_impuesto = monto_impuesto
    mr_detalle_mensaje = detalle_mensaje
    mr_total_factura = total_factura

    '''Iniciamos con la creación del mensaje Receptor'''
    sb = StringBuilder()
    sb.Append(
        '<MensajeReceptor xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ')
    sb.Append(
        'xmlns="https://cdn.comprobanteselectronicos.go.cr/xml-schemas/v4.3/mensajeReceptor" ')
    sb.Append(
        'xsi:schemaLocation="https://cdn.comprobanteselectronicos.go.cr/xml-schemas/v4.3/mensajeReceptor ')
    sb.Append(
        'https://www.hacienda.go.cr/ATV/ComprobanteElectronico/docs/esquemas/2016/v4.3/MensajeReceptor_V4.3.xsd">')
    sb.Append('<Clave>' + mr_clave + '</Clave>')
    sb.Append('<NumeroCedulaEmisor>' +
              mr_cedula_emisor + '</NumeroCedulaEmisor>')
    sb.Append('<FechaEmisionDoc>' + mr_fecha_emision + '</FechaEmisionDoc>')
    sb.Append('<Mensaje>' + str(mr_mensaje_id) + '</Mensaje>')

    if mr_detalle_mensaje is not None:
        sb.Append('<DetalleMensaje>' +
                  escape(mr_detalle_mensaje) + '</DetalleMensaje>')

    if mr_monto_impuesto is not None and mr_monto_impuesto > 0:
        sb.Append('<MontoTotalImpuesto>' +
                  str(mr_monto_impuesto) + '</MontoTotalImpuesto>')

    if codigo_actividad:
        sb.Append('<CodigoActividad>' +
                  str(codigo_actividad) + '</CodigoActividad>')

    sb.Append('<CondicionImpuesto>' +
              str(condicion_impuesto) + '</CondicionImpuesto>')

    # TODO: Estar atento a la publicación de Hacienda de cómo utilizar esto
    if monto_total_impuesto_acreditar:
        sb.Append(
            '<MontoTotalImpuestoAcreditar>' +
            str(monto_total_impuesto_acreditar) +
            '</MontoTotalImpuestoAcreditar>')

    # TODO: Estar atento a la publicación de Hacienda de cómo utilizar esto
    if monto_total_gasto_aplicable:
        sb.Append('<MontoTotalDeGastoAplicable>' +
                  str(monto_total_gasto_aplicable) +
                  '</MontoTotalDeGastoAplicable>')

    if mr_total_factura is not None and mr_total_factura > 0:
        sb.Append('<TotalFactura>' + str(mr_total_factura) + '</TotalFactura>')
    else:
        return (
            'El monto Total de la Factura para el Mensaje Receptro es inválido'
        )

    sb.Append('<NumeroCedulaReceptor>' +
              mr_cedula_receptor + '</NumeroCedulaReceptor>')
    sb.Append('<NumeroConsecutivoReceptor>' +
              mr_consecutivo_receptor + '</NumeroConsecutivoReceptor>')
    sb.Append('</MensajeReceptor>')

    return str(sb)


def company_xml(sb, issuing_company, document_type):
    if document_type == 'FEC':
        vat = re.sub('[^0-9]', '', issuing_company['numeroIdentificacion'])
        if not issuing_company['tipoIdentificacion']:
            if len(vat) == 9:  # cedula fisica
                id_code = '01'
            elif len(vat) == 10:  # cedula juridica
                id_code = '02'
            elif len(vat) == 11 or len(vat) == 12:  # dimex
                id_code = '03'
            else:
                id_code = '05'
        else:
            id_code = issuing_company['tipoIdentificacion']

        if issuing_company.get('nombre'):
            sb.Append('<Emisor>')
            sb.Append('<Nombre>' + escape(issuing_company['nombre']) + '</Nombre>')

            if document_type == 'FEE':
                if issuing_company.vat:
                    sb.Append('<IdentificacionExtranjero>' + issuing_company[
                        'numeroIdentificacion'] + '</IdentificacionExtranjero>')
            else:
                sb.Append('<Identificacion>')
                sb.Append('<Tipo>' + id_code + '</Tipo>')
                sb.Append('<Numero>' + vat + '</Numero>')
                sb.Append('</Identificacion>')

            if issuing_company.get('nombreComercial'):
                sb.Append('<NombreComercial>{}</NombreComercial>'
                          .format(issuing_company['nombreComercial']))

            if document_type != 'FEE':
                if issuing_company.get('provincia') and issuing_company.get('canton') and issuing_company.get(
                        'distrito'):
                    sb.Append('<Ubicacion>')
                    sb.Append('<Provincia>' + str(issuing_company['provincia'] or '') + '</Provincia>')
                    sb.Append('<Canton>' + str(issuing_company['canton'] or '') + '</Canton>')
                    sb.Append('<Distrito>' + str(issuing_company['distrito'] or '') + '</Distrito>')
                    sb.Append('<Barrio>' + (
                        '01' if not issuing_company.get('barrio') else str(issuing_company['barrio'])) + '</Barrio>')
                    sb.Append('<OtrasSenas>' + escape(str(issuing_company['otrasSenas'] or 'NA')) + '</OtrasSenas>')
                    sb.Append('</Ubicacion>')
                    sb.Append('<Telefono>')
                    sb.Append('<CodigoPais>' + str(issuing_company['codigoPais']) + '</CodigoPais>')
                    sb.Append('<NumTelefono>' + str(issuing_company['telefono']) + '</NumTelefono>')
                    sb.Append('</Telefono>')

                match = issuing_company['correo'] and re.match(
                    r'^(\s?[^\s,]+@[^\s,]+\.[^\s,]+\s?,)*(\s?[^\s,]+@[^\s,]+\.[^\s,]+)$',
                    issuing_company['correo'].lower())
                if match:
                    email_receptor = issuing_company['correo']
                else:
                    email_receptor = 'indefinido@indefinido.com'
                sb.Append('<CorreoElectronico>' + email_receptor + '</CorreoElectronico>')

            sb.Append('</Emisor>')
    else:
        sb.Append('<Emisor>')
        sb.Append('<Nombre>' + escape(issuing_company['name']) + '</Nombre>')
        sb.Append('<Identificacion>')
        sb.Append('<Tipo>' + issuing_company['type_identification'] + '</Tipo>')
        sb.Append('<Numero>' + issuing_company['identification_dni'] + '</Numero>')
        sb.Append('</Identificacion>')
        sb.Append('<NombreComercial>' + escape(str(issuing_company['tradename'] or 'NA')) + '</NombreComercial>')
        sb.Append('<Ubicacion>')
        sb.Append('<Provincia>' + issuing_company['state'] + '</Provincia>')
        sb.Append('<Canton>' + issuing_company['county'] + '</Canton>')
        sb.Append('<Distrito>' + issuing_company['district'] + '</Distrito>')
        sb.Append('<Barrio>' + str(issuing_company['neighborhood'] or '00') + '</Barrio>')
        sb.Append('<OtrasSenas>' + escape(issuing_company['address'] or 'NA') + '</OtrasSenas>')
        sb.Append('</Ubicacion>')
        sb.Append('<Telefono>')
        sb.Append('<CodigoPais>' + str(issuing_company['code_phone']) + '</CodigoPais>')
        sb.Append('<NumTelefono>' + str(issuing_company['phone']) + '</NumTelefono>')
        sb.Append('</Telefono>')

        sb.Append('<CorreoElectronico>' + str(issuing_company['email']) + '</CorreoElectronico>')
        sb.Append('</Emisor>')


def receptor_xml(sb, receiver_company, document_type):
    if document_type == 'FEC':
        sb.Append('<Receptor>')
        sb.Append('<Nombre>' + escape(receiver_company['name']) + '</Nombre>')
        sb.Append('<Identificacion>')
        sb.Append('<Tipo>' + receiver_company['type_identification'] + '</Tipo>')
        sb.Append('<Numero>' + receiver_company['identification_dni'] + '</Numero>')
        sb.Append('</Identificacion>')
        sb.Append('<NombreComercial>' + escape(str(receiver_company['tradename'] or 'NA')) + '</NombreComercial>')
        sb.Append('<Ubicacion>')
        sb.Append('<Provincia>' + receiver_company['state'] + '</Provincia>')
        sb.Append('<Canton>' + receiver_company['county'] + '</Canton>')
        sb.Append('<Distrito>' + receiver_company['district'] + '</Distrito>')
        sb.Append('<Barrio>' + str(receiver_company['neighborhood'] or '00') + '</Barrio>')
        sb.Append('<OtrasSenas>' + escape(receiver_company['address'] or 'NA') + '</OtrasSenas>')
        sb.Append('</Ubicacion>')
        sb.Append('<Telefono>')
        sb.Append('<CodigoPais>' + str(receiver_company['code_phone']) + '</CodigoPais>')
        sb.Append('<NumTelefono>' + str(receiver_company['phone']) + '</NumTelefono>')
        sb.Append('</Telefono>')

        sb.Append('<CorreoElectronico>' + str(receiver_company['email']) + '</CorreoElectronico>')
        sb.Append('</Receptor>')
    else:
        if not receiver_company: # document_type == 'TE' or (document_type == 'NC' and not receiver_company.get('numeroIdentificacion')):
            pass
        else:
            vat = re.sub('[^0-9]', '', receiver_company['numeroIdentificacion'])
            if not receiver_company['tipoIdentificacion']:
                if len(vat) == 9:  # cedula fisica
                    id_code = '01'
                elif len(vat) == 10:  # cedula juridica
                    id_code = '02'
                elif len(vat) == 11 or len(vat) == 12:  # dimex
                    id_code = '03'
                else:
                    id_code = '05'
            else:
                id_code = receiver_company['tipoIdentificacion']

            if receiver_company.get('nombre'):
                sb.Append('<Receptor>')
                sb.Append('<Nombre>' + escape(receiver_company['nombre']) + '</Nombre>')

                if document_type == 'FEE':
                    if receiver_company.vat:
                        sb.Append('<IdentificacionExtranjero>' + receiver_company[
                            'numero_identificacion'] + '</IdentificacionExtranjero>')
                else:
                    sb.Append('<Identificacion>')
                    sb.Append('<Tipo>' + id_code + '</Tipo>')
                    sb.Append('<Numero>' + vat + '</Numero>')
                    sb.Append('</Identificacion>')

                if receiver_company.get('nombreComercial'):
                    sb.Append('<NombreComercial>{}</NombreComercial>'
                              .format(receiver_company['nombreComercial']))

                if document_type != 'FEE':
                    if receiver_company.get('provincia') and receiver_company.get('canton') and receiver_company.get(
                            'distrito'):
                        sb.Append('<Ubicacion>')
                        sb.Append('<Provincia>' + str(receiver_company['provincia'] or '') + '</Provincia>')
                        sb.Append('<Canton>' + str(receiver_company['canton'] or '') + '</Canton>')
                        sb.Append('<Distrito>' + str(receiver_company['distrito'] or '') + '</Distrito>')
                        sb.Append('<Barrio>' + ('01' if not receiver_company.get('barrio') else str(
                            receiver_company['barrio'])) + '</Barrio>')
                        sb.Append(
                            '<OtrasSenas>' + escape(str(receiver_company['otrasSenas'] or 'NA')) + '</OtrasSenas>')
                        sb.Append('</Ubicacion>')
                        sb.Append('<Telefono>')
                        sb.Append('<CodigoPais>' + str(receiver_company['codigoPais']) + '</CodigoPais>')
                        sb.Append('<NumTelefono>' + str(receiver_company['telefono']) + '</NumTelefono>')
                        sb.Append('</Telefono>')

                    match = receiver_company['correo'] and re.match(
                        r'^(\s?[^\s,]+@[^\s,]+\.[^\s,]+\s?,)*(\s?[^\s,]+@[^\s,]+\.[^\s,]+)$',
                        receiver_company['correo'].lower())
                    if match:
                        email_receptor = receiver_company['correo']
                    else:
                        email_receptor = 'indefinido@indefinido.com'
                    sb.Append('<CorreoElectronico>' + email_receptor + '</CorreoElectronico>')

                sb.Append('</Receptor>')


def lines_xml(sb, lines, document_type):
    sb.Append('<DetalleServicio>')

    for v in lines:
        sb.Append('<LineaDetalle>')
        sb.Append('<NumeroLinea>' + str(v['numero']) + '</NumeroLinea>')

        if document_type == 'FEE' and v.get('partidaArancelaria'):
            sb.Append('<PartidaArancelaria>' + str(v['partidaArancelaria']) + '</PartidaArancelaria>')

        code = v['codigo']
        sb.Append('<Codigo>' + code + '</Codigo>')

        com_codes = v.get('codigoComercial', ())
        for cc in com_codes:
            sb.Append('<CodigoComercial>')
            sb.Append('<Tipo>' + str(cc['tipo']) + '</Tipo>')
            if 'codigo' in cc:
                sb.Append('<Codigo>' + str(cc['codigo']) + '</Codigo>')
            sb.Append('</CodigoComercial>')

        sb.Append('<Cantidad>' + str(v['cantidad']) + '</Cantidad>')
        sb.Append('<UnidadMedida>' + str(v['unidad']) + '</UnidadMedida>')
        if 'unidadMedidaComercial' in v:
            sb.Append('<UnidadMedidaComercial>{}</UnidadMedidaComercial>'
                      .format(v['unidadMedidaComercial']))
        if 'detalle' in v:
            sb.Append('<Detalle>' + v['detalle'] + '</Detalle>')
        sb.Append('<PrecioUnitario>' + str(v['precioUnitario']) + '</PrecioUnitario>')
        sb.Append('<MontoTotal>' + str(v['montoTotal']) + '</MontoTotal>')

        if 'descuento' in v:
            for b in v['descuento']:
                sb.Append('<Descuento>')
                sb.Append('<MontoDescuento>' +
                          str(b['monto']) + '</MontoDescuento>')
                sb.Append('<NaturalezaDescuento>' +
                          str(b['descripcionDescuento']) + '</NaturalezaDescuento>')
                sb.Append('</Descuento>')

        sb.Append('<SubTotal>' + str(v['subtotal']) + '</SubTotal>')

        if document_type != 'FEE' \
                and 'baseImponible' in v:
            sb.Append('<BaseImponible>' + str(v['baseImponible']) + '</BaseImponible>')

        if v.get('impuesto'):
            for b in v['impuesto']:
                if b.get('codigoTarifa') == '01':
                    continue

                sb.Append('<Impuesto>')
                sb.Append('<Codigo>' + str(b['codigo']) + '</Codigo>')
                if 'codigoTarifa' in b:
                    sb.Append('<CodigoTarifa>' + str(b['codigoTarifa']) + '</CodigoTarifa>')
                sb.Append('<Tarifa>' + str(b['tarifa']) + '</Tarifa>')

                if b['codigo'] == INCLUDES_IVAFACTOR_TAX_CODE:
                    sb.Append('<FactorIVA>{}</FactorIVA>'.format(
                        b['factorIVA']))

                sb.Append('<Monto>' + str(b['monto']) + '</Monto>')

                if document_type != 'FEE':
                    taxcut = b.get('exoneracion')
                    if taxcut:
                        for cut in taxcut:
                            sb.Append('<Exoneracion>')
                            sb.Append('<TipoDocumento>' + str(cut['Tipodocumento']) + '</TipoDocumento>')
                            sb.Append('<NumeroDocumento>' + str(cut['NumeroDocumento']) + '</NumeroDocumento>')
                            sb.Append(
                                '<NombreInstitucion>' + str(cut['NombreInstitucion']) + '</NombreInstitucion>')
                            sb.Append('<FechaEmision>' + str(cut['FechaEmision']) + '</FechaEmision>')
                            sb.Append('<PorcentajeExoneracion>' + str(
                                cut['porcentajeExoneracion']) + '</PorcentajeExoneracion>')
                            sb.Append(
                                '<MontoExoneracion>' + str(cut['montoExoneracion']) + '</MontoExoneracion>')
                            sb.Append('</Exoneracion>')

                sb.Append('</Impuesto>')

        sb.Append('<ImpuestoNeto>' + str(v['impuestoNeto']) + '</ImpuestoNeto>')
        sb.Append('<MontoTotalLinea>' + str(v['totalLinea']) + '</MontoTotalLinea>')
        sb.Append('</LineaDetalle>')
    sb.Append('</DetalleServicio>')


def other_charges(sb, otros_cargos):
    for otro_cargo in otros_cargos:
        sb.Append('<OtrosCargos>')
        sb.Append('<TipoDocumento>' +
                  otro_cargo['tipoDocumento'] +
                  '</TipoDocumento>')

        if 'numeroIdentidadTercero' in otro_cargo:
            sb.Append('<NumeroIdentidadTercero>' +
                      str(otro_cargo['numeroIdentidadTercero']) +
                      '</NumeroIdentidadTercero>')

        if 'nombreTercero' in otro_cargo:
            sb.Append('<NombreTercero>' +
                      otro_cargo['nombreTercero'] +
                      '</NombreTercero>')

        sb.Append('<Detalle>' +
                  otro_cargo['detalle'] +
                  '</Detalle>')

        if 'porcentaje' in otro_cargo:
            sb.Append('<Porcentaje>' +
                      str(otro_cargo['porcentaje']) +
                      '</Porcentaje>')

        sb.Append('<MontoCargo>' +
                  str(otro_cargo['montoCargo']) +
                  '</MontoCargo>')
        sb.Append('</OtrosCargos>')


# TODO: change this signature...
def gen_xml_v43(company_data, document_type, key_mh,
                consecutive, date, sale_conditions, activity_code,
                receptor, total_servicio_gravado, total_servicio_exento,
                totalServExonerado, total_mercaderia_gravado,
                total_mercaderia_exento, totalMercExonerada,
                totalOtrosCargos, base_total, total_impuestos,
                total_descuento, lines, otrosCargos, invoice_comments,
                referencia, payment_methods, plazo_credito, moneda,
                total_taxed, total_exone, total_untaxed, total_sales,
                total_return_iva, total_document):
    if document_type == 'FEC':
        issuing_company = receptor
        activity_code = receptor.get('codigoActividad', activity_code)
        receiver_company = company_data
    else:
        issuing_company = company_data
        receiver_company = receptor

    sb = StringBuilder()
    sb.Append(
        '<' + fe_enums.tagName[document_type] + ' xmlns="' + fe_enums.XmlnsHacienda[document_type] + '" ')
    sb.Append('xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:xsd="http://www.w3.org/2001/XMLSchema" ')
    sb.Append('xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ')
    sb.Append('xsi:schemaLocation="' + fe_enums.schemaLocation[document_type] + '">')

    sb.Append('<Clave>' + key_mh + '</Clave>')
    sb.Append('<CodigoActividad>' + activity_code + '</CodigoActividad>')
    sb.Append('<NumeroConsecutivo>' + consecutive + '</NumeroConsecutivo>')
    sb.Append('<FechaEmision>' + date + '</FechaEmision>')

    company_xml(sb, issuing_company, document_type)

    receptor_xml(sb, receiver_company, document_type)

    sb.Append('<CondicionVenta>' + sale_conditions + '</CondicionVenta>')
    sb.Append('<PlazoCredito>' + plazo_credito + '</PlazoCredito>')

    for pm in payment_methods:
        sb.Append('<MedioPago>' + pm['codigo'] + '</MedioPago>')

    lines_xml(sb, lines, document_type)

    if otrosCargos:
        other_charges(sb, otrosCargos)

    sb.Append('<ResumenFactura>')
    sb.Append('<CodigoTipoMoneda><CodigoMoneda>' +
              moneda['tipoMoneda'] +
              '</CodigoMoneda><TipoCambio>' +
              moneda['tipoCambio'] +
              '</TipoCambio></CodigoTipoMoneda>')

    sb.Append('<TotalServGravados>' + str(total_servicio_gravado) + '</TotalServGravados>')
    sb.Append('<TotalServExentos>' + str(total_servicio_exento) + '</TotalServExentos>')

    if document_type != NO_TAXCUT_DOC_TYPE:
        sb.Append('<TotalServExonerado>' + str(totalServExonerado) + '</TotalServExonerado>')

    sb.Append('<TotalMercanciasGravadas>' + str(total_mercaderia_gravado) + '</TotalMercanciasGravadas>')
    sb.Append('<TotalMercanciasExentas>' + str(total_mercaderia_exento) + '</TotalMercanciasExentas>')

    if document_type != NO_TAXCUT_DOC_TYPE:
        sb.Append('<TotalMercExonerada>' + str(totalMercExonerada) + '</TotalMercExonerada>')

    sb.Append('<TotalGravado>' + str(total_taxed) + '</TotalGravado>')
    sb.Append('<TotalExento>' + str(total_untaxed) + '</TotalExento>')

    if document_type != NO_TAXCUT_DOC_TYPE:
        sb.Append('<TotalExonerado>' + str(total_exone) + '</TotalExonerado>')

    sb.Append('<TotalVenta>' + str(total_sales) + '</TotalVenta>')
    sb.Append('<TotalDescuentos>' + str(total_descuento) + '</TotalDescuentos>')
    sb.Append('<TotalVentaNeta>' + str(base_total) + '</TotalVentaNeta>')
    sb.Append('<TotalImpuesto>' + str(total_impuestos) + '</TotalImpuesto>')
    if document_type not in NO_RETURNTAX_DOC_TYPES:
        sb.Append('<TotalIVADevuelto>' + str(total_return_iva) + '</TotalIVADevuelto>')
    sb.Append('<TotalOtrosCargos>' + str(totalOtrosCargos) + '</TotalOtrosCargos>')
    sb.Append('<TotalComprobante>' + str(total_document) + '</TotalComprobante>')
    sb.Append('</ResumenFactura>')

    if referencia:
        for ref in referencia:
            sb.Append('<InformacionReferencia>')
            sb.Append('<TipoDoc>' + str(ref['tipoDocumento']) + '</TipoDoc>')
            if 'numeroReferencia' in ref:
                sb.Append('<Numero>' + str(ref['numeroReferencia']) + '</Numero>')
            sb.Append('<FechaEmision>' + ref['fecha'] + '</FechaEmision>')
            if 'codigo' in ref:
                sb.Append('<Codigo>' + str(ref['codigo']) + '</Codigo>')
            if 'razon' in ref:
                sb.Append('<Razon>' + str(ref['razon']) + '</Razon>')
            sb.Append('</InformacionReferencia>')

    if invoice_comments:
        sb.Append('<Otros>')
        _other_text = invoice_comments.pop('otroTexto')
        if isinstance(_other_text, list):
            for _ot in _other_text:
                sb.Append('<OtroTexto>' + str(_ot) + '</OtroTexto>')
        else:
            sb.Append('<OtroTexto>' + str(_other_text) + ' </OtroTexto>')

        # killing off OtroContenido 'cuz not used. This section can handle it when it's relevant
        _other_content = invoice_comments.pop('otroContenido')
        # OtroContenido

        # for wallmart stuff
        for key, value in invoice_comments.items():
            sb.Append('<OtroTexto codigo="' + str(key) + '">' + str(value) + '</OtroTexto>')

        sb.Append('</Otros>')

    sb.Append('</' + fe_enums.tagName[document_type] + '>')

    return sb


def get_voucher_byid(clave, token):
    headers = {'Authorization': 'Bearer ' + token}
    endpoint = fe_enums.UrlHaciendaComprobantes['api-voucher']
    endpoint = endpoint + clave

    try:
        #  enviando solicitud get y guardando la respuesta como un objeto json
        response = requests.request(
            "GET", endpoint, headers=headers)
        # Verificamos el codigo devuelto, si es distinto de 202 es porque hacienda nos está devolviendo algun error
        if response.status_code != 200:
            error_caused_by = response.headers.get(
                'X-Error-Cause') if 'X-Error-Cause' in response.headers else ''
            error_caused_by += response.headers.get('validation-exception', '')
            _logger.info('Status: {}, Text {}'.format(
                response.status_code, error_caused_by))

            return {'status': response.status_code, 'text': error_caused_by}
        else:
            # respuesta_hacienda = response.status_code
            return {'status': response.status_code, 'text': response.text}
            # return respuesta_hacienda

    except ImportError:
        raise Exception('Error consultando el comprobante')


def get_vouchers(token, parameters):
    headers = {'Authorization': 'Bearer ' + token}
    endpoint = fe_enums.UrlHaciendaComprobantes['api-vouchers']

    endpoint = endpoint
    try:
        #  enviando solicitud get y guardando la respuesta como un objeto json
        response = requests.request(
            "GET", endpoint, headers=headers, params=parameters)
        print(response.url)

        # Verificamos el codigo devuelto, si es distinto de 202 es porque hacienda nos está devolviendo algun error
        if response.status_code < 200 or response.status_code > 206:
            error_caused_by = response.headers.get(
                'X-Error-Cause') if 'X-Error-Cause' in response.headers else ''
            error_caused_by += response.headers.get('validation-exception', '')
            _logger.info('Status: {}, Text {}'.format(
                response.status_code, error_caused_by))

            return {'status': response.status_code, 'text': error_caused_by}
        else:
            # respuesta_hacienda = response.status_code
            return {'status': response.status_code, 'text': json.loads(response.text)}
            # return respuesta_hacienda

    except ImportError:
        raise Exception('Error consultando los comprobantes')


# Funcion para enviar el XML al Ministerio de Hacienda
def send_xml_fe(_company, _receptor, _key_mh, token, date, xml, env):
    headers = {'Authorization': 'Bearer ' +
                                token, 'Content-type': 'application/json'}

    # establecer el ambiente al cual me voy a conectar
    endpoint = fe_enums.UrlHaciendaRecepcion[env]

    # xml is coming as bytes: json.dumps cannot serialize bytes by default, so let's try converting it to a string
    if isinstance(xml, bytes):
        # assuming this has to already be a b64 encoded byte-like object
        xml = xml.decode('utf-8')

    data = {'clave': _key_mh,
            'fecha': date,
            'emisor': {
                'tipoIdentificacion': _company['type_identification'],
                'numeroIdentificacion': _company['identification_dni']
            },
            'receptor': {
                'tipoIdentificacion': _receptor['dni_type_receiver'],
                'numeroIdentificacion': _receptor['dni_receiver']
            },
            'comprobanteXml': xml
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
        raise Exception('Error enviando el XML al Ministerior de Hacienda')


# def schema_validator(xml_file, xsd_file) -> bool:
def schema_validator(xml_file, xsd_file):  # not currently in use
    """
    verifies a xml
    :param xml_invoice: Invoice xml
    :param  xsd_file: XSD File Name
    :return:
    """

    xmlschema = etree.XMLSchema(etree.parse(os.path.join(
        os.path.dirname(__file__), "xsd/" + xsd_file
    )))

    xml_doc = base64decode(xml_file)
    root = etree.fromstring(xml_doc, etree.XMLParser(remove_blank_text=True))
    result = xmlschema.validate(root)

    return result


# Obtener Attachments para las Facturas Electrónicas
def get_invoice_attachments(invoice, record_id):  # duplicated in utils_mh and not used?
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


def parse_xml(name):
    return etree.parse(name).getroot()


# CONVIERTE UN STRING A BASE 64
def stringToBase64(s):
    return base64.b64encode(s).decode()


# TOMA UNA CADENA Y ELIMINA LOS CARACTERES AL INICIO Y AL FINAL
def stringStrip(s, start, end):
    return s[start:-end]


# Tomamos el XML y le hacemos el decode de base 64, esto por ahora es solo para probar
# la posible implementacion de la firma en python
def base64decode(string_decode):
    return base64.b64decode(string_decode)


# TOMA UNA CADENA EN BASE64 Y LA DECODIFICA PARA ELIMINAR EL b' Y DEJAR EL STRING CODIFICADO
# DE OTRA MANERA HACIENDA LO RECHAZA
def base64UTF8Decoder(s):
    return s.decode("utf-8")


# CLASE PERSONALIZADA (NO EXISTE EN PYTHON) QUE CONSTRUYE UNA CADENA MEDIANTE APPEND SEMEJANTE
# AL STRINGBUILDER DEL C#
class StringBuilder:
    _file_str = None

    def __init__(self):
        self._file_str = io.StringIO()

    def Append(self, _str):
        self._file_str.write(_str)

    def __str__(self):
        return self._file_str.getvalue()


def consulta_clave(clave, token,
                   tipo_ambiente):  # duplicated in utils_mh... are this two files just copies of each other???
    endpoint = fe_enums.UrlHaciendaRecepcion[tipo_ambiente] + clave

    headers = {
        'Authorization': 'Bearer {}'.format(token),
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    _logger.debug('MAB - consulta_clave - url: %s' % endpoint)

    try:
        # response = requests.request("GET", url, headers=headers)
        response = requests.get(endpoint, headers=headers)
        ############################
    except requests.exceptions.RequestException as e:
        _logger.error('Exception %s' % e)
        raise ServerError(
            status=InternalErrorCodes.INTERNAL_ERROR)  # TODO : new internal error code 4 hacienda key query

    if 200 <= response.status_code <= 299:
        response_json = {
            'status': 200,
            'ind-estado': response.json().get('ind-estado'),
            'respuesta-xml': response.json().get('respuesta-xml')
        }
    elif 400 <= response.status_code <= 499:  # now I know, but making it better?
        cause = response.headers.get('X-Error-Cause')
        if not cause:
            #  cause = 'Error'
            _logger.warning("""**Error Hacienda response:**
Endpoint: {}
Http Status: {}
Request Headers: {}
Response Headers: {}
Response Body: {}
""".format(
                endpoint, response.status_code,
                str(response.request.headers),
                str(response.headers), response.text)
            )
        response_json = {'status': response.status_code, 'ind-estado': 'error'}
    else:
        _logger.error("""MAB - consulta_clave failed.
Status code: {}
Reason: {}
Request Headers: {}
Response Headers: {}
Response Body: {}
""".format(response.status_code, response.reason,
           str(response.request.headers),
           str(response.headers), response.text))
        raise HaciendaError(
            http_status=response.status_code,
            headers=response.headers,
            body=response.text,
            status=InternalErrorCodes.HACIENDA_ERROR)
    return response_json


def get_economic_activities(company):  # not used... but, could be useful
    endpoint = "https://api.hacienda.go.cr/fe/ae?identificacion=" + company.vat

    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    try:
        response = requests.get(endpoint, headers=headers)
    except requests.exceptions.RequestException as e:
        _logger.error('Exception %s' % e)
        return {'status': -1, 'text': 'Excepcion %s' % e}

    if 200 <= response.status_code <= 299:
        _logger.error('MAB - get_economic_activities response: %s',
                      response.json())
        response_json = {
            'status': 200,
            'activities': response.json().get('actividades'),
            'name': response.json().get('nombre')
        }
    # elif 400 <= response.status_code <= 499:
    #    response_json = {'status': 400, 'ind-estado': 'error'}
    else:
        _logger.error('MAB - get_economic_activities failed.  error: %s',
                      response.status_code)
        response_json = {'status': response.status_code,
                         'text': 'get_economic_activities failed: %s' % response.reason}
    return response_json


def consulta_documentos(number_electronic, env, token_m_h, date_cr, document_type, consecutive_number_receiver=None):
    if document_type == 'CCE' or document_type == 'CPCE' or document_type == 'RCE':
        clave = str(number_electronic) + "-" + str(consecutive_number_receiver)
    else:
        clave = number_electronic

    response_json = consulta_clave(clave, token_m_h, env)
    _logger.debug(response_json)
    #  estado_m_h = response_json.get('ind-estado')

    #  if estado_m_h == 'aceptado':  # ??????
    #      state_tributacion = estado_m_h
    #      date_acceptance = date_cr
    return response_json


def send_message(inv, date_cr, xml, token, env):  # duplicated in utils_mh... and not used....
    endpoint = fe_enums.UrlHaciendaRecepcion[env]

    vat = re.sub('[^0-9]', '', inv.partner_id.vat)
    xml_base64 = stringToBase64(xml)

    comprobante = {
        'clave': inv.number_electronic,
        'consecutivoReceptor': inv.consecutive_number_receiver,
        "fecha": date_cr,
        'emisor': {
            'tipoIdentificacion': str(inv.partner_id.identification_id.code),
            'numeroIdentificacion': vat,
        },
        'receptor': {
            'tipoIdentificacion': str(inv.company_id.identification_id.code),
            'numeroIdentificacion': inv.company_id.vat,
        },
        'comprobanteXml': xml_base64,
    }

    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer {}'.format(token)}
    try:
        response = requests.post(endpoint, data=json.dumps(comprobante), headers=headers)

    except requests.exceptions.RequestException as e:
        _logger.info('Exception %s' % e)
        raise ServerError(status=InternalErrorCodes.INTERNAL_ERROR)
        # return {'status': 400, 'text': u'Excepción de envio XML'}
        # raise Exception(e)

    if not (200 <= response.status_code <= 299):
        _logger.error('MAB - ERROR SEND MESSAGE - RESPONSE:%s' %
                      response.headers.get('X-Error-Cause', 'Unknown'))
        return {'status': response.status_code, 'text': response.headers.get('X-Error-Cause', 'Unknown')}
    else:
        return {'status': response.status_code, 'text': response.text}


def load_xml_data(invoice, load_lines, account_id, product_id=False, analytic_account_id=False):  # not used...
    try:
        invoice_xml = etree.fromstring(base64.b64decode(invoice.xml_supplier_approval))
        document_type = re.search('FacturaElectronica|NotaCreditoElectronica|NotaDebitoElectronica',
                                  invoice_xml.tag).group(0)
    except Exception as e:
        return 'This XML file is not XML-compliant. Error: %s' % e

    namespaces = invoice_xml.nsmap
    inv_xmlns = namespaces.pop(None)
    namespaces['inv'] = inv_xmlns

    # invoice.consecutive_number_receiver = invoice_xml.xpath("inv:NumeroConsecutivo", namespaces=namespaces)[0].text
    invoice.reference = invoice.consecutive_number_receiver

    invoice.number_electronic = invoice_xml.xpath("inv:Clave", namespaces=namespaces)[0].text
    invoice.date_issuance = invoice_xml.xpath("inv:FechaEmision", namespaces=namespaces)[0].text
    invoice.date_invoice = invoice.date_issuance

    emisor = invoice_xml.xpath(
        "inv:Emisor/inv:Identificacion/inv:Numero",
        namespaces=namespaces)[0].text

    receptor = invoice_xml.xpath(
        "inv:Receptor/inv:Identificacion/inv:Numero",
        namespaces=namespaces)[0].text

    if receptor != invoice.company_id.vat:
        return ('El receptor no corresponde con la compañía actual con identificación ' +
                receptor + '. Por favor active la compañía correcta.')  # noqa

    currency_node = invoice_xml.xpath("inv:ResumenFactura/inv:CodigoTipoMoneda/inv:CodigoMoneda",
                                      namespaces=namespaces)
    if currency_node:
        invoice.currency_id = invoice.env['res.currency'].search([('name', '=', currency_node[0].text)],
                                                                 limit=1).id
    else:
        invoice.currency_id = invoice.env['res.currency'].search([('name', '=', 'CRC')], limit=1).id

    partner = invoice.env['res.partner'].search([('vat', '=', emisor),
                                                 ('supplier', '=', True),
                                                 '|',
                                                 ('company_id', '=', invoice.company_id.id),
                                                 ('company_id', '=', False)],
                                                limit=1)

    if partner:
        invoice.partner_id = partner
    else:
        return 'The provider in the invoice does not exists. Please review it.'

    invoice.account_id = partner.property_account_payable_id
    invoice.payment_term_id = partner.property_supplier_payment_term_id

    _logger.error('MAB - load_lines: %s - account: %s' %
                  (load_lines, account_id))

    if load_lines and not invoice.invoice_line_ids:
        # if True:  #load_lines:
        lines = invoice_xml.xpath("inv:DetalleServicio/inv:LineaDetalle", namespaces=namespaces)
        new_lines = invoice.env['account.invoice.line']
        for line in lines:
            product_uom = invoice.env['uom.uom'].search(
                [('code', '=', line.xpath("inv:UnidadMedida", namespaces=namespaces)[0].text)],
                limit=1).id
            total_amount = float(line.xpath("inv:MontoTotal", namespaces=namespaces)[0].text)

            discount_percentage = 0.0
            discount_note = None

            discount_node = line.xpath("inv:Descuento", namespaces=namespaces)
            if discount_node:
                discount_amount_node = discount_node[0].xpath("inv:MontoDescuento", namespaces=namespaces)[0]
                discount_amount = float(discount_amount_node.text or '0.0')
                discount_percentage = discount_amount / total_amount * 100
                discount_note = discount_node[0].xpath("inv:NaturalezaDescuento", namespaces=namespaces)[0].text
            else:
                discount_amount_node = line.xpath("inv:MontoDescuento", namespaces=namespaces)
                if discount_amount_node:
                    discount_amount = float(discount_amount_node[0].text or '0.0')
                    discount_percentage = discount_amount / total_amount * 100
                    discount_note = line.xpath("inv:NaturalezaDescuento", namespaces=namespaces)[0].text

            total_tax = 0.0
            taxes = []
            tax_nodes = line.xpath("inv:Impuesto", namespaces=namespaces)
            for tax_node in tax_nodes:
                tax_code = re.sub(r"[^0-9]+", "", tax_node.xpath("inv:Codigo", namespaces=namespaces)[0].text)
                tax_amount = float(tax_node.xpath("inv:Tarifa", namespaces=namespaces)[0].text) / 100
                _logger.debug('MAB - tax_code: %s', tax_code)
                _logger.debug('MAB - tax_amount: %s', tax_amount)
                tax = invoice.env['account.tax'].search(
                    [('tax_code', '=', tax_code),
                     ('amount', '=', tax_amount),
                     ('type_tax_use', '=', 'purchase')],
                    limit=1)
                if tax:
                    total_tax += float(tax_node.xpath("inv:Monto", namespaces=namespaces)[0].text)

                    # TODO: Add exonerations and exemptions

                    taxes.append((4, tax.id))
                else:
                    return ('Tax code %s and percentage %s is not registered in the system',
                            tax_code, tax_amount)
            _logger.debug('MAB - impuestos de linea: %s', taxes)
            invoice_line = invoice.env['account.invoice.line'].create({
                'name': line.xpath("inv:Detalle", namespaces=namespaces)[0].text,
                'invoice_id': invoice.id,
                'price_unit': line.xpath("inv:PrecioUnitario", namespaces=namespaces)[0].text,
                'quantity': line.xpath("inv:Cantidad", namespaces=namespaces)[0].text,
                'uom_id': product_uom,
                'sequence': line.xpath("inv:NumeroLinea", namespaces=namespaces)[0].text,
                'discount': discount_percentage,
                'discount_note': discount_note,
                # 'total_amount': total_amount,
                'product_id': product_id,
                'account_id': account_id,
                'account_analytic_id': analytic_account_id,
                'invoice_line_tax_id': taxes
            })

            new_lines += invoice_line

        invoice.invoice_line_ids = new_lines

    invoice.amount_total_electronic_invoice = \
        invoice_xml.xpath("inv:ResumenFactura/inv:TotalComprobante", namespaces=namespaces)[0].text

    tax_node = invoice_xml.xpath("inv:ResumenFactura/inv:TotalImpuesto", namespaces=namespaces)
    if tax_node:
        invoice.amount_tax_electronic_invoice = tax_node[0].text

    invoice.compute_taxes()
