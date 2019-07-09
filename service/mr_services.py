# -*- coding: utf-8 -*-
import json
import re
import utils
from . import fe_enums

from odoo.exceptions import UserError

from xml.sax.saxutils import escape

def get_mr_sequencevalue(inv):
    # '''Verificamos si el ID del mensaje receptor es válido# '''
    mr_mensaje_id = int( inv.state_invoice_partner )
    if mr_mensaje_id < 1 or mr_mensaje_id > 3:
        raise UserError( 'El ID del mensaje receptor es inválido.' )
    elif mr_mensaje_id is None:
        raise UserError( 'No se ha proporcionado un ID válido para el MR.' )

    if inv.state_invoice_partner == '1':
        detalle_mensaje = 'Aceptado'
        tipo = 1
        tipo_documento = fe_enums.TipoDocumento['CCE']
        sequence = inv.env['ir.sequence'].next_by_code(
            'sequece.electronic.doc.confirmation' )

    elif inv.state_invoice_partner == '2':
        detalle_mensaje = 'Aceptado parcial'
        tipo = 2
        tipo_documento = fe_enums.TipoDocumento['CPCE']
        sequence = inv.env['ir.sequence'].next_by_code(
            'sequece.electronic.doc.partial.confirmation' )
    else:
        detalle_mensaje = 'Rechazado'
        tipo = 3
        tipo_documento = fe_enums.TipoDocumento['RCE']
        sequence = inv.env['ir.sequence'].next_by_code(
            'sequece.electronic.doc.reject' )

    return {'detalle_mensaje': detalle_mensaje, 'tipo': tipo, 'tipo_documento': tipo_documento, 'sequence': sequence}

def gen_xml_42(clave, cedula_emisor, fecha_emision, id_mensaje, detalle_mensaje, cedula_receptor,
                  consecutivo_receptor,
                  monto_impuesto=0, total_factura=0):
    # '''Verificamos si la clave indicada corresponde a un numeros# '''
    mr_clave = re.sub( '[^0-9]', '', clave )
    if len( mr_clave ) != 50:
        raise UserError(
            'La clave a utilizar es inválida. Debe contener al menos 50 digitos' )

    # '''Obtenemos el número de identificación del Emisor y lo validamos númericamente# '''
    mr_cedula_emisor = re.sub( '[^0-9]', '', cedula_emisor )
    if len( mr_cedula_emisor ) != 12:
        mr_cedula_emisor = str( mr_cedula_emisor ).zfill( 12 )
    elif mr_cedula_emisor is None:
        raise UserError( 'La cédula del Emisor en el MR es inválida.' )

    mr_fecha_emision = fecha_emision
    if mr_fecha_emision is None:
        raise UserError( 'La fecha de emisión en el MR es inválida.' )

    # '''Verificamos si el ID del mensaje receptor es válido# '''
    mr_mensaje_id = int( id_mensaje )
    if mr_mensaje_id < 1 and mr_mensaje_id > 3:
        raise UserError( 'El ID del mensaje receptor es inválido.' )
    elif mr_mensaje_id is None:
        raise UserError( 'No se ha proporcionado un ID válido para el MR.' )

    mr_cedula_receptor = re.sub( '[^0-9]', '', cedula_receptor )
    if len( mr_cedula_receptor ) != 12:
        mr_cedula_receptor = str( mr_cedula_receptor ).zfill( 12 )
    elif mr_cedula_receptor is None:
        raise UserError(
            'No se ha proporcionado una cédula de receptor válida para el MR.' )

    # '''Verificamos si el consecutivo indicado para el mensaje receptor corresponde a numeros# '''
    mr_consecutivo_receptor = re.sub( '[^0-9]', '', consecutivo_receptor )
    if len( mr_consecutivo_receptor ) != 20:
        raise UserError( 'La clave del consecutivo para el mensaje receptor es inválida. '
                         'Debe contener al menos 50 digitos' )

    mr_monto_impuesto = monto_impuesto
    mr_detalle_mensaje = detalle_mensaje
    mr_total_factura = total_factura

    # '''Iniciamos con la creación del mensaje Receptor# '''
    sb = StringBuilder()
    sb.Append(
        '<MensajeReceptor xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' )
    sb.Append(
        'xmlns="https://tribunet.hacienda.go.cr/docs/esquemas/2017/v4.2/mensajeReceptor" ' )
    sb.Append(
        'xsi:schemaLocation="https://tribunet.hacienda.go.cr/docs/esquemas/2017/v4.2/mensajeReceptor ' )
    sb.Append(
        'https://tribunet.hacienda.go.cr/docs/esquemas/2017/v4.2/MensajeReceptor_4.2.xsd">' )
    sb.Append( '<Clave>' + mr_clave + '</Clave>' )
    sb.Append( '<NumeroCedulaEmisor>' +
               mr_cedula_emisor + '</NumeroCedulaEmisor>' )
    sb.Append( '<FechaEmisionDoc>' + mr_fecha_emision + '</FechaEmisionDoc>' )
    sb.Append( '<Mensaje>' + str( mr_mensaje_id ) + '</Mensaje>' )

    if mr_detalle_mensaje is not None:
        sb.Append( '<DetalleMensaje>' +
                   escape( mr_detalle_mensaje ) + '</DetalleMensaje>' )

    if mr_monto_impuesto is not None and mr_monto_impuesto > 0:
        sb.Append( '<MontoTotalImpuesto>' +
                   str( mr_monto_impuesto ) + '</MontoTotalImpuesto>' )

    if mr_total_factura is not None and mr_total_factura > 0:
        sb.Append( '<TotalFactura>' + str( mr_total_factura ) + '</TotalFactura>' )
    else:
        raise UserError(
            'El monto Total de la Factura para el Mensaje Receptro es inválido' )

    sb.Append( '<NumeroCedulaReceptor>' +
               mr_cedula_receptor + '</NumeroCedulaReceptor>' )
    sb.Append( '<NumeroConsecutivoReceptor>' +
               mr_consecutivo_receptor + '</NumeroConsecutivoReceptor>' )
    sb.Append( '</MensajeReceptor>' )

    mreceptor_bytes = str( sb )
    mr_to_base64 = stringToBase64( mreceptor_bytes )

    return base64UTF8Decoder( mr_to_base64 )


def gen_xml_43(clave, cedula_emisor, fecha_emision, id_mensaje,
                  detalle_mensaje, cedula_receptor,
                  consecutivo_receptor,
                  monto_impuesto=0, total_factura=0,
                  codigo_actividad=False,
                  monto_total_impuesto_acreditar=False,
                  monto_total_gasto_aplicable=False,
                  condicion_impuesto=False):
    # '''Verificamos si la clave indicada corresponde a un numeros# '''
    mr_clave = re.sub( '[^0-9]', '', clave )
    if len( mr_clave ) != 50:
        raise UserError(
            'La clave a utilizar es inválida. Debe contener al menos 50 digitos' )

    # '''Obtenemos el número de identificación del Emisor y lo validamos númericamente# '''
    mr_cedula_emisor = re.sub( '[^0-9]', '', cedula_emisor )
    if len( mr_cedula_emisor ) != 12:
        mr_cedula_emisor = str( mr_cedula_emisor ).zfill( 12 )
    elif mr_cedula_emisor is None:
        raise UserError( 'La cédula del Emisor en el MR es inválida.' )

    mr_fecha_emision = fecha_emision
    if mr_fecha_emision is None:
        raise UserError( 'La fecha de emisión en el MR es inválida.' )

    # '''Verificamos si el ID del mensaje receptor es válido# '''
    mr_mensaje_id = int( id_mensaje )
    if mr_mensaje_id < 1 and mr_mensaje_id > 3:
        raise UserError( 'El ID del mensaje receptor es inválido.' )
    elif mr_mensaje_id is None:
        raise UserError( 'No se ha proporcionado un ID válido para el MR.' )

    mr_cedula_receptor = re.sub( '[^0-9]', '', cedula_receptor )
    if len( mr_cedula_receptor ) != 12:
        mr_cedula_receptor = str( mr_cedula_receptor ).zfill( 12 )
    elif mr_cedula_receptor is None:
        raise UserError(
            'No se ha proporcionado una cédula de receptor válida para el MR.' )

    # '''Verificamos si el consecutivo indicado para el mensaje receptor corresponde a numeros# '''
    mr_consecutivo_receptor = re.sub( '[^0-9]', '', consecutivo_receptor )
    if len( mr_consecutivo_receptor ) != 20:
        raise UserError( 'La clave del consecutivo para el mensaje receptor es inválida. '
                         'Debe contener al menos 50 digitos' )

    mr_monto_impuesto = monto_impuesto
    mr_detalle_mensaje = detalle_mensaje
    mr_total_factura = total_factura

    # '''Iniciamos con la creación del mensaje Receptor# '''
    sb = StringBuilder()
    sb.Append(
        '<MensajeReceptor xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' )
    sb.Append(
        'xmlns="https://cdn.comprobanteselectronicos.go.cr/xml-schemas/v4.3/mensajeReceptor" ' )
    sb.Append(
        'xsi:schemaLocation="https://cdn.comprobanteselectronicos.go.cr/xml-schemas/v4.3/mensajeReceptor ' )
    sb.Append(
        'https://www.hacienda.go.cr/ATV/ComprobanteElectronico/docs/esquemas/2016/v4.3/MensajeReceptor_V4.3.xsd">' )
    sb.Append( '<Clave>' + mr_clave + '</Clave>' )
    sb.Append( '<NumeroCedulaEmisor>' +
               mr_cedula_emisor + '</NumeroCedulaEmisor>' )
    sb.Append( '<FechaEmisionDoc>' + mr_fecha_emision + '</FechaEmisionDoc>' )
    sb.Append( '<Mensaje>' + str( mr_mensaje_id ) + '</Mensaje>' )

    if mr_detalle_mensaje is not None:
        sb.Append( '<DetalleMensaje>' +
                   escape( mr_detalle_mensaje ) + '</DetalleMensaje>' )

    if mr_monto_impuesto is not None and mr_monto_impuesto > 0:
        sb.Append( '<MontoTotalImpuesto>' +
                   str( mr_monto_impuesto ) + '</MontoTotalImpuesto>' )

    if codigo_actividad:
        sb.Append( '<CodigoActividad>' +
                   str( codigo_actividad ) + '</CodigoActividad>' )

    # TODO: Estar atento a la publicación de Hacienda de cómo utilizar esto
    if condicion_impuesto:
        sb.Append( '<CondicionImpuesto>' +
                   str( condicion_impuesto ) + '</CondicionImpuesto>' )

    # TODO: Estar atento a la publicación de Hacienda de cómo utilizar esto
    if monto_total_impuesto_acreditar:
        sb.Append(
            '<MontoTotalImpuestoAcreditar>' +
            str( monto_total_impuesto_acreditar ) +
            '</MontoTotalImpuestoAcreditar>' )

    # TODO: Estar atento a la publicación de Hacienda de cómo utilizar esto
    if monto_total_gasto_aplicable:
        sb.Append( '<MontoTotalDeGastoAplicable>' +
                   str( monto_total_gasto_aplicable ) +
                   '</MontoTotalDeGastoAplicable>' )

    if mr_total_factura is not None and mr_total_factura > 0:
        sb.Append( '<TotalFactura>' + str( mr_total_factura ) + '</TotalFactura>' )
    else:
        raise UserError(
            'El monto Total de la Factura para el Mensaje Receptro es inválido'
        )

    sb.Append( '<NumeroCedulaReceptor>' +
               mr_cedula_receptor + '</NumeroCedulaReceptor>' )
    sb.Append( '<NumeroConsecutivoReceptor>' +
               mr_consecutivo_receptor + '</NumeroConsecutivoReceptor>' )
    sb.Append( '</MensajeReceptor>' )

    mreceptor_bytes = str( sb )
    mr_to_base64 = stringToBase64( mreceptor_bytes )

    return base64UTF8Decoder( mr_to_base64 )
