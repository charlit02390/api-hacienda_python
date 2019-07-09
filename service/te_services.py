# -*- coding: utf-8 -*-
import json
import re
import utils

from xml.sax.saxutils import escape


def gen_xml_te_42(inv, sale_conditions, total_servicio_gravado, total_servicio_exento,
                  total_mercaderia_gravado, total_mercaderia_exento, base_total, total_impuestos, total_descuento,
                  lines, currency_rate, invoice_comments):
    numero_linea = 0

    sb = utils.StringBuilder()
    sb.Append( '<?xml version="1.0" encoding="utf-8"?>' )
    sb.Append(
        '<TiqueteElectronico xmlns="https://tribunet.hacienda.go.cr/docs/esquemas/2017/v4.2/tiqueteElectronico" ' )
    sb.Append(
        'xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:xsd="http://www.w3.org/2001/XMLSchema" ' )
    sb.Append( 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' )
    sb.Append(
        'xsi:schemaLocation="https://www.hacienda.go.cr/ATV/ComprobanteElectronico/docs/esquemas/2016/v4.2/TiqueteElectronico_V4.2.xsd">' )

    sb.Append( '<Clave>' + inv.number_electronic + '</Clave>' )
    sb.Append( '<NumeroConsecutivo>' + inv.number_electronic[21:41] + '</NumeroConsecutivo>' )
    sb.Append( '<FechaEmision>' + inv.date_issuance + '</FechaEmision>' )
    sb.Append( '<Emisor>' )
    sb.Append( '<Nombre>' + escape( inv.company_id.name ) + '</Nombre>' )
    sb.Append( '<Identificacion>' )
    sb.Append( '<Tipo>' + inv.company_id.identification_id.code + '</Tipo>' )
    sb.Append( '<Numero>' + inv.company_id.vat + '</Numero>' )
    sb.Append( '</Identificacion>' )
    sb.Append( '<NombreComercial>' +
               escape( str( inv.company_id.commercial_name or 'NA' ) ) + '</NombreComercial>' )
    sb.Append( '<Ubicacion>' )
    sb.Append( '<Provincia>' + inv.company_id.state_id.code + '</Provincia>' )
    sb.Append( '<Canton>' + inv.company_id.county_id.code + '</Canton>' )
    sb.Append( '<Distrito>' + inv.company_id.district_id.code + '</Distrito>' )
    sb.Append(
        '<Barrio>' + str( inv.company_id.neighborhood_id.code or '00' ) + '</Barrio>' )
    sb.Append( '<OtrasSenas>' +
               escape( str( inv.company_id.street or 'NA' ) ) + '</OtrasSenas>' )
    sb.Append( '</Ubicacion>' )
    sb.Append( '<Telefono>' )
    sb.Append( '<CodigoPais>' + inv.company_id.phone_code + '</CodigoPais>' )
    sb.Append( '<NumTelefono>' +
               re.sub( '[^0-9]+', '', inv.company_id.phone ) + '</NumTelefono>' )
    sb.Append( '</Telefono>' )
    sb.Append( '<CorreoElectronico>' +
               str( inv.company_id.email ) + '</CorreoElectronico>' )
    sb.Append( '</Emisor>' )
    sb.Append( '<CondicionVenta>' + sale_conditions + '</CondicionVenta>' )
    sb.Append( '<PlazoCredito>' +
               str( inv.payment_term_id and inv.payment_term_id.line_ids[0].days or '0' ) + '</PlazoCredito>' )
    sb.Append( '<MedioPago>' + (inv.payment_methods_id.sequence or '01') + '</MedioPago>' )
    sb.Append( '<DetalleServicio>' )

    detalle_factura = lines
    response_json = json.loads( detalle_factura )

    for (k, v) in response_json.items():
        numero_linea = numero_linea + 1

        sb.Append( '<LineaDetalle>' )
        sb.Append( '<NumeroLinea>' + str( numero_linea ) + '</NumeroLinea>' )
        sb.Append( '<Cantidad>' + str( v['cantidad'] ) + '</Cantidad>' )
        sb.Append( '<UnidadMedida>' +
                   str( v['unidadMedida'] ) + '</UnidadMedida>' )
        sb.Append( '<Detalle>' + str( v['detalle'] ) + '</Detalle>' )
        sb.Append( '<PrecioUnitario>' +
                   str( v['precioUnitario'] ) + '</PrecioUnitario>' )
        sb.Append( '<MontoTotal>' + str( v['montoTotal'] ) + '</MontoTotal>' )
        if v.get( 'montoDescuento' ):
            sb.Append( '<MontoDescuento>' +
                       str( v['montoDescuento'] ) + '</MontoDescuento>' )
        if v.get( 'naturalezaDescuento' ):
            sb.Append( '<NaturalezaDescuento>' +
                       str( v['naturalezaDescuento'] ) + '</NaturalezaDescuento>' )
        sb.Append( '<SubTotal>' + str( v['subtotal'] ) + '</SubTotal>' )

        if v.get( 'impuesto' ):
            for (a, b) in v['impuesto'].items():
                sb.Append( '<Impuesto>' )
                sb.Append( '<Codigo>' + str( b['codigo'] ) + '</Codigo>' )
                sb.Append( '<CodigoTarifa>' +
                           str( b['iva_tax_code'] ) + '</CodigoTarifa>' )
                sb.Append( '<Tarifa>' + str( b['tarifa'] ) + '</Tarifa>' )
                sb.Append( '<Monto>' + str( b['monto'] ) + '</Monto>' )

                if b.get( 'exoneracion' ):
                    for (c, d) in b['exoneracion']:
                        sb.Append( '<Exoneracion>' )
                        sb.Append( '<TipoDocumento>' +
                                   d['tipoDocumento'] + '</TipoDocumento>' )
                        sb.Append( '<NumeroDocumento>' +
                                   d['numeroDocumento'] + '</NumeroDocumento>' )
                        sb.Append( '<NombreInstitucion>' +
                                   d['nombreInstitucion'] + '</NombreInstitucion>' )
                        sb.Append( '<FechaEmision>' +
                                   d['fechaEmision'] + '</FechaEmision>' )
                        sb.Append( '<MontoImpuesto>' +
                                   d['montoImpuesto'] + '</MontoImpuesto>' )
                        sb.Append( '<PorcentajeCompra>' +
                                   d['porcentajeCompra'] + '</PorcentajeCompra>' )

                sb.Append( '</Impuesto>' )
        sb.Append( '<MontoTotalLinea>' +
                   str( v['montoTotalLinea'] ) + '</MontoTotalLinea>' )
        sb.Append( '</LineaDetalle>' )
    sb.Append( '</DetalleServicio>' )
    sb.Append( '<ResumenFactura>' )
    sb.Append( '<CodigoMoneda>' + str( inv.currency_id.name ) + '</CodigoMoneda>' )
    sb.Append( '<TipoCambio>' + str( currency_rate ) + '</TipoCambio>' )
    sb.Append( '<TotalServGravados>' +
               str( total_servicio_gravado ) + '</TotalServGravados>' )
    sb.Append( '<TotalServExentos>' +
               str( total_servicio_exento ) + '</TotalServExentos>' )
    sb.Append( '<TotalMercanciasGravadas>' +
               str( total_mercaderia_gravado ) + '</TotalMercanciasGravadas>' )
    sb.Append( '<TotalMercanciasExentas>' +
               str( total_mercaderia_exento ) + '</TotalMercanciasExentas>' )
    sb.Append( '<TotalGravado>' + str( total_servicio_gravado +
                                       total_mercaderia_gravado ) + '</TotalGravado>' )
    sb.Append( '<TotalExento>' + str( total_servicio_exento +
                                      total_mercaderia_exento ) + '</TotalExento>' )
    sb.Append( '<TotalVenta>' + str( total_servicio_gravado + total_mercaderia_gravado +
                                     total_servicio_exento + total_mercaderia_exento ) + '</TotalVenta>' )
    sb.Append( '<TotalDescuentos>' +
               str( round( total_descuento, 2 ) ) + '</TotalDescuentos>' )
    sb.Append( '<TotalVentaNeta>' +
               str( round( base_total, 2 ) ) + '</TotalVentaNeta>' )
    sb.Append( '<TotalImpuesto>' +
               str( round( total_impuestos, 2 ) ) + '</TotalImpuesto>' )
    sb.Append( '<TotalComprobante>' + str( round( base_total +
                                                  total_impuestos, 2 ) ) + '</TotalComprobante>' )
    sb.Append( '</ResumenFactura>' )
    sb.Append( '<Normativa>' )
    sb.Append( '<NumeroResolucion>DGT-R-48-2016</NumeroResolucion>' )
    sb.Append( '<FechaResolucion>07-10-2016 08:00:00</FechaResolucion>' )
    sb.Append( '</Normativa>' )
    sb.Append( '<Otros>' )
    sb.Append( '<OtroTexto>' + str( invoice_comments ) + '</OtroTexto>' )
    sb.Append( '</Otros>' )

    sb.Append( '</TiqueteElectronico>' )

    # telectronico_bytes = str(sb)
    # return stringToBase64(telectronico_bytes)
    return sb


def gen_xml_te_43(inv, sale_conditions, total_servicio_gravado, total_servicio_exento,
                  total_mercaderia_gravado, total_mercaderia_exento, base_total, total_impuestos, total_descuento,
                  lines, currency_rate, invoice_comments, otrosCargos):
    numero_linea = 0

    sb = utils.StringBuilder()
    sb.Append(
        '<TiqueteElectronico xmlns="https://cdn.comprobanteselectronicos.go.cr/xml-schemas/v4.3/tiqueteElectronico" ' )
    sb.Append(
        'xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:xsd="http://www.w3.org/2001/XMLSchema" ' )
    sb.Append( 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' )
    sb.Append(
        'xsi:schemaLocation="https://www.hacienda.go.cr/ATV/ComprobanteElectronico/docs/esquemas/2016/v4.3/TiqueteElectronico_V4.3.xsd">' )

    sb.Append( '<Clave>' + inv.number_electronic + '</Clave>' )
    sb.Append( '<CodigoActividad>' +
               inv.company_id.activity_id.code + '</CodigoActividad>' )
    sb.Append( '<NumeroConsecutivo>' + inv.number_electronic[21:41] + '</NumeroConsecutivo>' )
    sb.Append( '<FechaEmision>' + get_time_hacienda() + '</FechaEmision>' )
    sb.Append( '<Emisor>' )
    sb.Append( '<Nombre>' + escape( inv.company_id.name ) + '</Nombre>' )
    sb.Append( '<Identificacion>' )
    sb.Append( '<Tipo>' + inv.company_id.identification_id.code + '</Tipo>' )
    sb.Append( '<Numero>' + inv.company_id.vat + '</Numero>' )
    sb.Append( '</Identificacion>' )
    sb.Append( '<NombreComercial>' +
               escape( str( inv.company_id.commercial_name or 'NA' ) ) + '</NombreComercial>' )
    sb.Append( '<Ubicacion>' )
    sb.Append( '<Provincia>' + inv.company_id.state_id.code + '</Provincia>' )
    sb.Append( '<Canton>' + inv.company_id.county_id.code + '</Canton>' )
    sb.Append( '<Distrito>' + inv.company_id.district_id.code + '</Distrito>' )
    sb.Append(
        '<Barrio>' + str( inv.company_id.neighborhood_id.code or '00' ) + '</Barrio>' )
    sb.Append( '<OtrasSenas>' +
               escape( str( inv.company_id.street or 'NA' ) ) + '</OtrasSenas>' )
    sb.Append( '</Ubicacion>' )
    sb.Append( '<Telefono>' )
    sb.Append( '<CodigoPais>' + inv.company_id.phone_code + '</CodigoPais>' )
    sb.Append( '<NumTelefono>' +
               re.sub( '[^0-9]+', '', inv.company_id.phone ) + '</NumTelefono>' )
    sb.Append( '</Telefono>' )
    sb.Append( '<CorreoElectronico>' +
               str( inv.company_id.email ) + '</CorreoElectronico>' )
    sb.Append( '</Emisor>' )

    sb.Append( '<Receptor>' )
    sb.Append( '<Nombre>' + escape( str( inv.partner_id.name[:80] ) ) + '</Nombre>' )
    sb.Append( '</Receptor>' )

    sb.Append( '<CondicionVenta>' + sale_conditions + '</CondicionVenta>' )

    sb.Append( '<MedioPago>' + (inv.payment_methods_id.sequence or '01') + '</MedioPago>' )
    sb.Append( '<DetalleServicio>' )

    detalle_factura = lines
    response_json = json.loads( detalle_factura )

    for (k, v) in response_json.items():
        numero_linea = numero_linea + 1

        sb.Append( '<LineaDetalle>' )
        sb.Append( '<NumeroLinea>' + str( numero_linea ) + '</NumeroLinea>' )

        sb.Append( '<Cantidad>' + str( v['cantidad'] ) + '</Cantidad>' )
        sb.Append( '<UnidadMedida>' +
                   str( v['unidadMedida'] ) + '</UnidadMedida>' )
        sb.Append( '<Detalle>' + str( v['detalle'] ) + '</Detalle>' )
        sb.Append( '<PrecioUnitario>' +
                   str( v['precioUnitario'] ) + '</PrecioUnitario>' )
        sb.Append( '<MontoTotal>' + str( v['montoTotal'] ) + '</MontoTotal>' )
        if v.get( 'montoDescuento' ):
            sb.Append( '<MontoDescuento>' +
                       str( v['montoDescuento'] ) + '</MontoDescuento>' )
        if v.get( 'naturalezaDescuento' ):
            sb.Append( '<NaturalezaDescuento>' +
                       str( v['naturalezaDescuento'] ) + '</NaturalezaDescuento>' )
        sb.Append( '<SubTotal>' + str( v['subtotal'] ) + '</SubTotal>' )

        if v.get( 'impuesto' ):
            for (a, b) in v['impuesto'].items():
                sb.Append( '<Impuesto>' )
                sb.Append( '<Codigo>' + str( b['codigo'] ) + '</Codigo>' )
                sb.Append( '<Tarifa>' + str( b['tarifa'] ) + '</Tarifa>' )
                sb.Append( '<Monto>' + str( b['monto'] ) + '</Monto>' )

                if b.get( 'exoneracion' ):
                    for (c, d) in b['exoneracion']:
                        sb.Append( '<Exoneracion>' )
                        sb.Append( '<TipoDocumento>' +
                                   d['tipoDocumento'] + '</TipoDocumento>' )
                        sb.Append( '<NumeroDocumento>' +
                                   d['numeroDocumento'] + '</NumeroDocumento>' )
                        sb.Append( '<NombreInstitucion>' +
                                   d['nombreInstitucion'] + '</NombreInstitucion>' )
                        sb.Append( '<FechaEmision>' +
                                   d['fechaEmision'] + '</FechaEmision>' )
                        sb.Append( '<MontoImpuesto>' +
                                   d['montoImpuesto'] + '</MontoImpuesto>' )
                        sb.Append( '<PorcentajeCompra>' +
                                   d['porcentajeCompra'] + '</PorcentajeCompra>' )

                sb.Append( '</Impuesto>' )
        sb.Append( '<MontoTotalLinea>' +
                   str( v['montoTotalLinea'] ) + '</MontoTotalLinea>' )
        sb.Append( '</LineaDetalle>' )
    sb.Append( '</DetalleServicio>' )

    # TODO: ¿Cómo implementar otros cargos a nivel de UI y model en Odoo?
    if otrosCargos:
        sb.Append( '<OtrosCargos>' )
        response_json = json.loads( otrosCargos )
        for (k, v) in response_json.items():
            sb.Append( '<TipoDocumento>' +
                       str( v['TipoDocumento'] ) + '<TipoDocumento>' )

            if v.get( 'NumeroIdentidadTercero' ):
                sb.Append( '<NumeroIdentidadTercero>' +
                           str( v['NumeroIdentidadTercero'] ) + '<NumeroIdentidadTercero>' )

            if v.get( 'NombreTercero' ):
                sb.Append( '<NombreTercero>' +
                           str( v['NombreTercero'] ) + '<NombreTercero>' )

            sb.Append( '<Detalle>' + str( v['Detalle'] ) + '<Detalle>' )
            if v.get( 'Porcentaje' ):
                sb.Append( '<Porcentaje>' +
                           str( v['Porcentaje'] ) + '<Porcentaje>' )

            sb.Append( '<MontoCargo>' + str( v['MontoCargo'] ) + '<MontoCargo>' )
        sb.Append( '</OtrosCargos>' )

    sb.Append( '<ResumenFactura>' )
    sb.Append( '<CodigoTipoMoneda><CodigoMoneda>' + str( inv.currency_id.name ) +
               '</CodigoMoneda><TipoCambio>' + str( currency_rate ) + '</TipoCambio></CodigoTipoMoneda>' )
    sb.Append( '<TotalServGravados>' +
               str( total_servicio_gravado ) + '</TotalServGravados>' )
    sb.Append( '<TotalServExentos>' +
               str( total_servicio_exento ) + '</TotalServExentos>' )

    sb.Append( '<TotalMercanciasGravadas>' +
               str( total_mercaderia_gravado ) + '</TotalMercanciasGravadas>' )
    sb.Append( '<TotalMercanciasExentas>' +
               str( total_mercaderia_exento ) + '</TotalMercanciasExentas>' )

    sb.Append( '<TotalGravado>' + str( total_servicio_gravado +
                                       total_mercaderia_gravado ) + '</TotalGravado>' )
    sb.Append( '<TotalExento>' + str( total_servicio_exento +
                                      total_mercaderia_exento ) + '</TotalExento>' )

    # TODO: Hay que calcular TotalExonerado
    # sb.Append('<TotalExonerado>' + str(totalServExonerado + totalMercExonerada) + '</TotalExonerado>')

    # TODO: agregar los exonerados en la suma
    sb.Append( '<TotalVenta>' + str( total_servicio_gravado + total_mercaderia_gravado +
                                     total_servicio_exento + total_mercaderia_exento ) + '</TotalVenta>' )

    sb.Append( '<TotalDescuentos>' +
               str( round( total_descuento, 2 ) ) + '</TotalDescuentos>' )
    sb.Append( '<TotalVentaNeta>' +
               str( round( base_total, 2 ) ) + '</TotalVentaNeta>' )
    sb.Append( '<TotalImpuesto>' +
               str( round( total_impuestos, 2 ) ) + '</TotalImpuesto>' )

    # TODO: Hay que calcular el TotalIVADevuelto
    # sb.Append('<TotalIVADevuelto>' + str(¿de dónde sacamos esto?) + '</TotalIVADevuelto>')

    # TODO: Hay que calcular el TotalOtrosCargos
    # sb.Append('<TotalOtrosCargos>' + str(¿de dónde sacamos esto?) + '</TotalOtrosCargos>')

    sb.Append( '<TotalComprobante>' + str( round( base_total +
                                                  total_impuestos, 2 ) ) + '</TotalComprobante>' )
    sb.Append( '</ResumenFactura>' )

    sb.Append( '<Otros>' )
    sb.Append( '<OtroTexto>' + str( invoice_comments ) + '</OtroTexto>' )
    sb.Append( '</Otros>' )

    sb.Append( '</TiqueteElectronico>' )

    # telectronico_bytes = str(sb)
    # return stringToBase64(telectronico_bytes)
    return sb