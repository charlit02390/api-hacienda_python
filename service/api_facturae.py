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
from infrastructure import request_pool

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
DATA_STATUSES = (200, 206)
CONFIRMATION_STATUSES = (201, 202)


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
        data = {
            'client_id': env,
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
    data = {
        'client_id': tipo_ambiente,
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
            sb.append('<Emisor>')
            sb.append('<Nombre>' + escape(issuing_company['nombre']) + '</Nombre>')

            if document_type == 'FEE':
                if issuing_company['numeroIdentificacion']:
                    sb.append('<IdentificacionExtranjero>' + issuing_company[
                        'numeroIdentificacion'] + '</IdentificacionExtranjero>')
            else:
                sb.append('<Identificacion>')
                sb.append('<Tipo>' + id_code + '</Tipo>')
                sb.append('<Numero>' + vat + '</Numero>')
                sb.append('</Identificacion>')

            if issuing_company.get('nombreComercial'):
                sb.append('<NombreComercial>{}</NombreComercial>'
                          .format(issuing_company['nombreComercial']))

            if document_type != 'FEE':
                if issuing_company.get('provincia') and issuing_company.get('canton') and issuing_company.get(
                        'distrito'):
                    sb.append('<Ubicacion>')
                    sb.append('<Provincia>' + str(issuing_company['provincia'] or '') + '</Provincia>')
                    sb.append('<Canton>' + str(issuing_company['canton'] or '') + '</Canton>')
                    sb.append('<Distrito>' + str(issuing_company['distrito'] or '') + '</Distrito>')
                    sb.append('<Barrio>' + (
                        '01' if not issuing_company.get('barrio') else str(issuing_company['barrio'])) + '</Barrio>')
                    sb.append('<OtrasSenas>' + escape(str(issuing_company['otrasSenas'] or 'NA')) + '</OtrasSenas>')
                    sb.append('</Ubicacion>')
                    sb.append('<Telefono>')
                    sb.append('<CodigoPais>' + str(issuing_company['codigoPais']) + '</CodigoPais>')
                    sb.append('<NumTelefono>' + str(issuing_company['telefono']) + '</NumTelefono>')
                    sb.append('</Telefono>')

                match = issuing_company['correo'] and re.match(
                    r'^(\s?[^\s,]+@[^\s,]+\.[^\s,]+\s?,)*(\s?[^\s,]+@[^\s,]+\.[^\s,]+)$',
                    issuing_company['correo'].lower())
                if match:
                    email_receptor = issuing_company['correo']
                else:
                    email_receptor = 'indefinido@indefinido.com'
                sb.append('<CorreoElectronico>' + email_receptor + '</CorreoElectronico>')

            sb.append('</Emisor>')
    else:
        sb.append('<Emisor>')
        sb.append('<Nombre>' + escape(issuing_company['name']) + '</Nombre>')
        sb.append('<Identificacion>')
        sb.append('<Tipo>' + issuing_company['type_identification'] + '</Tipo>')
        sb.append('<Numero>' + issuing_company['identification_dni'] + '</Numero>')
        sb.append('</Identificacion>')
        sb.append('<NombreComercial>' + escape(str(issuing_company['tradename'] or 'NA')) + '</NombreComercial>')
        sb.append('<Ubicacion>')
        sb.append('<Provincia>' + issuing_company['state'] + '</Provincia>')
        sb.append('<Canton>' + issuing_company['county'] + '</Canton>')
        sb.append('<Distrito>' + issuing_company['district'] + '</Distrito>')
        sb.append('<Barrio>' + str(issuing_company['neighborhood'] or '00') + '</Barrio>')
        sb.append('<OtrasSenas>' + escape(issuing_company['address'] or 'NA') + '</OtrasSenas>')
        sb.append('</Ubicacion>')
        sb.append('<Telefono>')
        sb.append('<CodigoPais>' + str(issuing_company['code_phone']) + '</CodigoPais>')
        sb.append('<NumTelefono>' + str(issuing_company['phone']) + '</NumTelefono>')
        sb.append('</Telefono>')

        sb.append('<CorreoElectronico>' + str(issuing_company['email']) + '</CorreoElectronico>')
        sb.append('</Emisor>')


def receptor_xml(sb, receiver_company, document_type):
    if document_type == 'FEC':
        sb.append('<Receptor>')
        sb.append('<Nombre>' + escape(receiver_company['name']) + '</Nombre>')
        sb.append('<Identificacion>')
        sb.append('<Tipo>' + receiver_company['type_identification'] + '</Tipo>')
        sb.append('<Numero>' + receiver_company['identification_dni'] + '</Numero>')
        sb.append('</Identificacion>')
        sb.append('<NombreComercial>' + escape(str(receiver_company['tradename'] or 'NA')) + '</NombreComercial>')
        sb.append('<Ubicacion>')
        sb.append('<Provincia>' + receiver_company['state'] + '</Provincia>')
        sb.append('<Canton>' + receiver_company['county'] + '</Canton>')
        sb.append('<Distrito>' + receiver_company['district'] + '</Distrito>')
        sb.append('<Barrio>' + str(receiver_company['neighborhood'] or '00') + '</Barrio>')
        sb.append('<OtrasSenas>' + escape(receiver_company['address'] or 'NA') + '</OtrasSenas>')
        sb.append('</Ubicacion>')
        sb.append('<Telefono>')
        sb.append('<CodigoPais>' + str(receiver_company['code_phone']) + '</CodigoPais>')
        sb.append('<NumTelefono>' + str(receiver_company['phone']) + '</NumTelefono>')
        sb.append('</Telefono>')

        sb.append('<CorreoElectronico>' + str(receiver_company['email']) + '</CorreoElectronico>')
        sb.append('</Receptor>')
    else:
        if not receiver_company:
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
                sb.append('<Receptor>')
                sb.append('<Nombre>' + escape(receiver_company['nombre']) + '</Nombre>')

                if document_type == 'FEE':
                    if receiver_company['numero_identificacion']:
                        sb.append('<IdentificacionExtranjero>' + receiver_company[
                            'numero_identificacion'] + '</IdentificacionExtranjero>')
                else:
                    sb.append('<Identificacion>')
                    sb.append('<Tipo>' + id_code + '</Tipo>')
                    sb.append('<Numero>' + vat + '</Numero>')
                    sb.append('</Identificacion>')

                if receiver_company.get('nombreComercial'):
                    sb.append('<NombreComercial>{}</NombreComercial>'
                              .format(receiver_company['nombreComercial']))

                if document_type != 'FEE':
                    if receiver_company.get('provincia') and receiver_company.get('canton') and receiver_company.get(
                            'distrito'):
                        sb.append('<Ubicacion>')
                        sb.append('<Provincia>' + str(receiver_company['provincia'] or '') + '</Provincia>')
                        sb.append('<Canton>' + str(receiver_company['canton'] or '') + '</Canton>')
                        sb.append('<Distrito>' + str(receiver_company['distrito'] or '') + '</Distrito>')
                        sb.append('<Barrio>' + ('01' if not receiver_company.get('barrio') else str(
                            receiver_company['barrio'])) + '</Barrio>')
                        sb.append(
                            '<OtrasSenas>' + escape(str(receiver_company['otrasSenas'] or 'NA')) + '</OtrasSenas>')
                        sb.append('</Ubicacion>')
                        sb.append('<Telefono>')
                        sb.append('<CodigoPais>' + str(receiver_company['codigoPais']) + '</CodigoPais>')
                        sb.append('<NumTelefono>' + str(receiver_company['telefono']) + '</NumTelefono>')
                        sb.append('</Telefono>')

                    match = receiver_company['correo'] and re.match(
                        r'^(\s?[^\s,]+@[^\s,]+\.[^\s,]+\s?,)*(\s?[^\s,]+@[^\s,]+\.[^\s,]+)$',
                        receiver_company['correo'].lower())
                    if match:
                        email_receptor = receiver_company['correo']
                    else:
                        email_receptor = 'indefinido@indefinido.com'
                    sb.append('<CorreoElectronico>' + email_receptor + '</CorreoElectronico>')

                sb.append('</Receptor>')


def lines_xml(sb, lines, document_type):
    sb.append('<DetalleServicio>')

    for v in lines:
        sb.append('<LineaDetalle>')
        sb.append('<NumeroLinea>' + str(v['numero']) + '</NumeroLinea>')

        if document_type == 'FEE' and v.get('partidaArancelaria'):
            sb.append('<PartidaArancelaria>' + str(v['partidaArancelaria']) + '</PartidaArancelaria>')

        code = v['codigo']
        sb.append('<Codigo>' + code + '</Codigo>')

        com_codes = v.get('codigoComercial', ())
        for cc in com_codes:
            sb.append('<CodigoComercial>')
            sb.append('<Tipo>' + str(cc['tipo']) + '</Tipo>')
            if 'codigo' in cc:
                sb.append('<Codigo>' + str(cc['codigo']) + '</Codigo>')
            sb.append('</CodigoComercial>')

        sb.append('<Cantidad>' + str(v['cantidad']) + '</Cantidad>')
        sb.append('<UnidadMedida>' + str(v['unidad']) + '</UnidadMedida>')
        if 'unidadMedidaComercial' in v:
            sb.append('<UnidadMedidaComercial>{}</UnidadMedidaComercial>'
                      .format(v['unidadMedidaComercial']))
        if 'detalle' in v:
            sb.append('<Detalle>' + v['detalle'] + '</Detalle>')
        sb.append('<PrecioUnitario>' + str(v['precioUnitario']) + '</PrecioUnitario>')
        sb.append('<MontoTotal>' + str(v['montoTotal']) + '</MontoTotal>')

        if 'descuento' in v:
            for b in v['descuento']:
                sb.append('<Descuento>')
                sb.append('<MontoDescuento>' +
                          str(b['monto']) + '</MontoDescuento>')
                sb.append('<NaturalezaDescuento>' +
                          str(b['descripcionDescuento']) + '</NaturalezaDescuento>')
                sb.append('</Descuento>')

        sb.append('<SubTotal>' + str(v['subtotal']) + '</SubTotal>')

        if document_type != 'FEE' \
                and 'baseImponible' in v:
            sb.append('<BaseImponible>' + str(v['baseImponible']) + '</BaseImponible>')

        if v.get('impuesto'):
            for b in v['impuesto']:
                if b.get('codigoTarifa') == '01':
                    continue

                sb.append('<Impuesto>')
                sb.append('<Codigo>' + str(b['codigo']) + '</Codigo>')
                if 'codigoTarifa' in b:
                    sb.append('<CodigoTarifa>' + str(b['codigoTarifa']) + '</CodigoTarifa>')
                sb.append('<Tarifa>' + str(b['tarifa']) + '</Tarifa>')

                if b['codigo'] == INCLUDES_IVAFACTOR_TAX_CODE:
                    sb.append('<FactorIVA>{}</FactorIVA>'.format(
                        b['factorIVA']))

                sb.append('<Monto>' + str(b['monto']) + '</Monto>')

                if document_type != 'FEE':
                    taxcut = b.get('exoneracion')
                    if taxcut:
                        for cut in taxcut:
                            sb.append('<Exoneracion>')
                            sb.append('<TipoDocumento>' + str(cut['Tipodocumento']) + '</TipoDocumento>')
                            sb.append('<NumeroDocumento>' + str(cut['NumeroDocumento']) + '</NumeroDocumento>')
                            sb.append(
                                '<NombreInstitucion>' + str(cut['NombreInstitucion']) + '</NombreInstitucion>')
                            sb.append('<FechaEmision>' + str(cut['FechaEmision']) + '</FechaEmision>')
                            sb.append('<PorcentajeExoneracion>' + str(
                                cut['porcentajeExoneracion']) + '</PorcentajeExoneracion>')
                            sb.append(
                                '<MontoExoneracion>' + str(cut['montoExoneracion']) + '</MontoExoneracion>')
                            sb.append('</Exoneracion>')

                sb.append('</Impuesto>')

        sb.append('<ImpuestoNeto>' + str(v['impuestoNeto']) + '</ImpuestoNeto>')
        sb.append('<MontoTotalLinea>' + str(v['totalLinea']) + '</MontoTotalLinea>')
        sb.append('</LineaDetalle>')
    sb.append('</DetalleServicio>')


def other_charges(sb, otros_cargos):
    for otro_cargo in otros_cargos:
        sb.append('<OtrosCargos>')
        sb.append('<TipoDocumento>' +
                  otro_cargo['tipoDocumento'] +
                  '</TipoDocumento>')

        if 'numeroIdentidadTercero' in otro_cargo:
            sb.append('<NumeroIdentidadTercero>' +
                      str(otro_cargo['numeroIdentidadTercero']) +
                      '</NumeroIdentidadTercero>')

        if 'nombreTercero' in otro_cargo:
            sb.append('<NombreTercero>' +
                      otro_cargo['nombreTercero'] +
                      '</NombreTercero>')

        sb.append('<Detalle>' +
                  otro_cargo['detalle'] +
                  '</Detalle>')

        if 'porcentaje' in otro_cargo:
            sb.append('<Porcentaje>' +
                      str(otro_cargo['porcentaje']) +
                      '</Porcentaje>')

        sb.append('<MontoCargo>' +
                  str(otro_cargo['montoCargo']) +
                  '</MontoCargo>')
        sb.append('</OtrosCargos>')


# TODO: change this signature...
def gen_xml_v43(company_data, document_type, key_mh,
                consecutive, date, sale_conditions, activity_code,
                receptor, total_servicio_gravado, total_servicio_exento,
                total_serv_exonerado, total_mercaderia_gravado,
                total_mercaderia_exento, total_merc_exonerada,
                total_otros_cargos, base_total, total_impuestos,
                total_descuento, lines, otros_cargos, invoice_comments,
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
    sb.append(
        '<' + fe_enums.tagName[document_type] + ' xmlns="' + fe_enums.XmlnsHacienda[document_type] + '" ')
    sb.append('xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:xsd="http://www.w3.org/2001/XMLSchema" ')
    sb.append('xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ')
    sb.append('xsi:schemaLocation="' + fe_enums.schemaLocation[document_type] + '">')

    sb.append('<Clave>' + key_mh + '</Clave>')
    sb.append('<CodigoActividad>' + activity_code + '</CodigoActividad>')
    sb.append('<NumeroConsecutivo>' + consecutive + '</NumeroConsecutivo>')
    sb.append('<FechaEmision>' + date + '</FechaEmision>')

    company_xml(sb, issuing_company, document_type)

    receptor_xml(sb, receiver_company, document_type)

    sb.append('<CondicionVenta>' + sale_conditions + '</CondicionVenta>')
    sb.append('<PlazoCredito>' + plazo_credito + '</PlazoCredito>')

    for pm in payment_methods:
        sb.append('<MedioPago>' + pm['codigo'] + '</MedioPago>')

    lines_xml(sb, lines, document_type)

    if otros_cargos:
        other_charges(sb, otros_cargos)

    sb.append('<ResumenFactura>')
    sb.append('<CodigoTipoMoneda><CodigoMoneda>' +
              moneda['tipoMoneda'] +
              '</CodigoMoneda><TipoCambio>' +
              moneda['tipoCambio'] +
              '</TipoCambio></CodigoTipoMoneda>')

    sb.append('<TotalServGravados>' + str(total_servicio_gravado) + '</TotalServGravados>')
    sb.append('<TotalServExentos>' + str(total_servicio_exento) + '</TotalServExentos>')

    if document_type != NO_TAXCUT_DOC_TYPE:
        sb.append('<TotalServExonerado>' + str(total_serv_exonerado) + '</TotalServExonerado>')

    sb.append('<TotalMercanciasGravadas>' + str(total_mercaderia_gravado) + '</TotalMercanciasGravadas>')
    sb.append('<TotalMercanciasExentas>' + str(total_mercaderia_exento) + '</TotalMercanciasExentas>')

    if document_type != NO_TAXCUT_DOC_TYPE:
        sb.append('<TotalMercExonerada>' + str(total_merc_exonerada) + '</TotalMercExonerada>')

    sb.append('<TotalGravado>' + str(total_taxed) + '</TotalGravado>')
    sb.append('<TotalExento>' + str(total_untaxed) + '</TotalExento>')

    if document_type != NO_TAXCUT_DOC_TYPE:
        sb.append('<TotalExonerado>' + str(total_exone) + '</TotalExonerado>')

    sb.append('<TotalVenta>' + str(total_sales) + '</TotalVenta>')
    sb.append('<TotalDescuentos>' + str(total_descuento) + '</TotalDescuentos>')
    sb.append('<TotalVentaNeta>' + str(base_total) + '</TotalVentaNeta>')
    sb.append('<TotalImpuesto>' + str(total_impuestos) + '</TotalImpuesto>')
    if document_type not in NO_RETURNTAX_DOC_TYPES:
        sb.append('<TotalIVADevuelto>' + str(total_return_iva) + '</TotalIVADevuelto>')
    sb.append('<TotalOtrosCargos>' + str(total_otros_cargos) + '</TotalOtrosCargos>')
    sb.append('<TotalComprobante>' + str(total_document) + '</TotalComprobante>')
    sb.append('</ResumenFactura>')

    if referencia:
        for ref in referencia:
            sb.append('<InformacionReferencia>')
            sb.append('<TipoDoc>' + str(ref['tipoDocumento']) + '</TipoDoc>')
            if 'numeroReferencia' in ref:
                sb.append('<Numero>' + str(ref['numeroReferencia']) + '</Numero>')
            sb.append('<FechaEmision>' + ref['fecha'] + '</FechaEmision>')
            if 'codigo' in ref:
                sb.append('<Codigo>' + str(ref['codigo']) + '</Codigo>')
            if 'razon' in ref:
                sb.append('<Razon>' + str(ref['razon']) + '</Razon>')
            sb.append('</InformacionReferencia>')

    if invoice_comments:
        sb.append('<Otros>')
        _other_text = invoice_comments.pop('otroTexto')
        if isinstance(_other_text, list):
            for _ot in _other_text:
                sb.append('<OtroTexto>' + str(_ot) + '</OtroTexto>')
        else:
            sb.append('<OtroTexto>' + str(_other_text) + ' </OtroTexto>')

        # killing off OtroContenido 'cuz not used. This section can handle it when it's relevant
        if 'otroContenido' in invoice_comments:
            _other_content = invoice_comments.pop('otroContenido')
        # OtroContenido

        # for wallmart stuff
        for key, value in invoice_comments.items():
            sb.append('<OtroTexto codigo="' + str(key) + '">' + str(value) + '</OtroTexto>')

        sb.append('</Otros>')

    sb.append('</' + fe_enums.tagName[document_type] + '>')

    return sb


# Funcion para enviar el XML al Ministerio de Hacienda
def send_xml_fe(_company, _receptor, _key_mh, token, date, xml, env):
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-type': 'application/json'
    }

    # establecer el ambiente al cual me voy a conectar
    endpoint = fe_enums.UrlHaciendaRecepcion[env]

    # xml is coming as bytes: json.dumps cannot serialize bytes by default, so let's try converting it to a string
    if isinstance(xml, bytes):
        # assuming this has to already be a b64 encoded byte-like object
        xml = xml.decode('utf-8')

    data = {
        'clave': _key_mh,
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

    try:
        response = requests.post(url=endpoint, json=data,
                                 headers=headers)
    except requests.exceptions.RequestException as reqex:
        _logger.error('***requests Exception:***', exc_info=reqex)
        raise  # TODO: do stuff

    info = _handle_hacienda_api_response(response)
    if 'error' in info \
            and 'ya fue recibido anteriormente' not in info['error']['detail']:
        err_msg = info['error']['detail']
        raise ServerError(message=err_msg)

    return 'procesando'


def consulta_clave(clave, token,
                   tipo_ambiente):  # todo: REVIEW THIS, BIG IMPORTANT
    endpoint = fe_enums.UrlHaciendaRecepcion[tipo_ambiente] + clave

    headers = {
        'Authorization': 'Bearer {}'.format(token),
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    try:
        response = requests.get(endpoint, headers=headers)
    except requests.exceptions.RequestException as e:
        raise ServerError(
            error_code=InternalErrorCodes.INTERNAL_ERROR
        ) from e  # TODO : new internal error code 4 hacienda key query

    info = _handle_hacienda_api_response(response)
    if 'error' in info:
        if 'no ha sido recibido.' in info['error']['detail']:
            return {
                'ind-estado': 'creado',
                'respuesta-xml': None
            }

        raise HaciendaError(
            http_status=info['error']['http_status'],
            error_code=InternalErrorCodes.HACIENDA_ERROR,
            body=info['error']['detail'],
            headers={}
        )  # TODO: make raise _from_status function (http_status, message)

    return {
        'ind-estado': info.get('ind-estado'),
        'respuesta-xml': info.get('respuesta-xml')
    }


def _handle_hacienda_api_response(response: requests.Response):
    if response.status_code in DATA_STATUSES:  # responses that return info. Usually from a get request
        try:
            info = response.json()
        except ValueError as ver:
            _logger.error("""***Bad response body received:***
    Response body: {}""".format(response.text), exc_info=ver)
            info = {
                'error': {
                    'detail': 'Bad response body format received from Hacienda.',
                    'http_status': 400,
                    'code': 400
                }
            }

    # response that confirms creation or reception of a resource. Typically from a post request
    elif response.status_code in CONFIRMATION_STATUSES:
        location = response.headers.get('Location', '')
        info = {'location': location}

    # response that rejected a request due to not passing validation. Usually from post requests
    elif response.status_code == 400:
        val_exc = response.headers.get('validation-exception')
        cause = response.headers.get('X-Error-Cause', '')
        _logger.warning("""**Document not accepted by Hacienda**:
    Validation-Exception: {}
    Cause: {}""".format(val_exc, cause))
        info = {
            'error': {
                'http_status': 400,
                'code': 400,
                'detail': cause
            }
        }

    # not found response. Either the resource wasn't found or we have the wrong url...
    elif response.status_code == 404:
        cause = response.headers.get('X-Error-Cause')
        if not cause:
            cause = 'Bad URL'

        _logger.warning("""**Document not found:**
    Cause: {}""".format(cause))
        info = {
            'error': {
                'http_status': 404,
                'code': 404,
                'detail': cause
            }
        }

    # unathorized response. Either the oauth token is bad or something else happened...
    elif response.status_code == 401:
        _logger.error("""***Authorization challenge failed:
    Response Headers: {}
    Response Body: {}
    Request Headers: {}""".format(response.headers, response.text,
                                  response.request.headers))
        info = {
            'error': {
                'http_status': 401,
                'code': 401,
                'detail': response.reason
            }
        }

    # too many requests. Sent way too many requests in too short a time...
    elif response.status_code == 429:
        _logger.error("""***Rate Limit was hit:
    Response Headers: {}
    Response Body: {}
    Request Headers: {}""".format(response.headers,
                                  response.text,
                                  response.request.headers))

        retry_after = response.headers.get('retry-after', 600)
        request_pool.set_sleep(retry_after)

        info = {
            'error': {
                'http_status': 429,
                'code': 429,
                'detail': response.reason
            }
        }

    else:  # undocumented Hacienda response.
        _logger.info("""*Undocumented Hacienda response:*
    Status: {}
    Reason: {}
    Content: {}""".format(response.status_code, response.reason,
                          response.text))
        try:
            response.raise_for_status()
            info = {
                'error': {
                    'http_status': response.status_code,
                    'code': response.status_code,
                    'detail': 'Respuesta inesperada de hacienda: ' + response.text
                }
            }
        except requests.exceptions.HTTPError as httper:
            info = {
                'error': {
                    'http_status': response.status_code,
                    'code': response.status_code,
                    'detail': response.reason + '/' + str(httper) + '/' + response.text
                }
            }

    return info


# CLASE PERSONALIZADA (NO EXISTE EN PYTHON) QUE CONSTRUYE UNA CADENA MEDIANTE APPEND SEMEJANTE
# AL STRINGBUILDER DEL C#
class StringBuilder:
    _file_str = None

    def __init__(self):
        self._file_str = io.StringIO()

    def append(self, _str):
        self._file_str.write(_str)

    def __str__(self):
        return self._file_str.getvalue()


# Utilizada para establecer un limite de caracteres en la cedula del cliente, no mas de 20
# de lo contrario hacienda lo rechaza
def limit(_str, _limit):
    return (_str[:_limit - 3] + '...') if len(_str) > _limit else _str


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
