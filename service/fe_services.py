# -*- coding: utf-8 -*-
import json
import re

from xml.sax.saxutils import escape


def gen_xml_v43(data, sale_conditions, total_servicio_gravado, total_servicio_exento,
                   totalServExonerado, total_mercaderia_gravado, total_mercaderia_exento, totalMercExonerada,
                   totalOtrosCargos, base_total, total_impuestos, total_descuento, lines, otrosCargos,
                   currency_rate, invoice_comments
                   ):
    numero_linea = 0

    sb = utils.StringBuilder()
    sb.Append(
        '<FacturaElectronica xmlns="https://cdn.comprobanteselectronicos.go.cr/xml-schemas/v4.3/facturaElectronica" ' )
    sb.Append(
        'xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:xsd="http://www.w3.org/2001/XMLSchema" ' )
    sb.Append( 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' )
    sb.Append(
        'xsi:schemaLocation="https://www.hacienda.go.cr/ATV/ComprobanteElectronico/docs/esquemas/2016/v4.3/FacturaElectronica_V4.3.xsd">' )

    sb.Append( '<Clave>' + str(inv.number_electronic) + '</Clave>' )
    sb.Append( '<CodigoActividad>' +
               str(inv.company_id.activity_id.code) + '</CodigoActividad>' )
    sb.Append( '<NumeroConsecutivo>' + str(inv.number_electronic[21:41]) + '</NumeroConsecutivo>' )
    sb.Append( '<FechaEmision>' + str(utils.get_time_hacienda()) + '</FechaEmision>' )
    sb.Append( '<Emisor>' )
    sb.Append( '<Nombre>' + str(escape( inv.company_id.name )) + '</Nombre>' )
    sb.Append( '<Identificacion>' )
    sb.Append( '<Tipo>' + str(inv.company_id.identification_id.code) + '</Tipo>' )
    sb.Append( '<Numero>' + str(inv.company_id.vat ) + '</Numero>' )
    sb.Append( '</Identificacion>' )
    sb.Append( '<NombreComercial>' +
               escape( str( inv.company_id.commercial_name or 'NA' ) ) + '</NombreComercial>' )
    sb.Append( '<Ubicacion>' )
    sb.Append( '<Provincia>' + str(inv.company_id.state_id.code ) + '</Provincia>' )
    sb.Append( '<Canton>' + str(inv.company_id.county_id.code ) + '</Canton>' )
    sb.Append( '<Distrito>' + str(inv.company_id.district_id.code ) + '</Distrito>' )
    sb.Append(
        '<Barrio>' + str( inv.company_id.neighborhood_id.code or '00' ) + '</Barrio>' )
    sb.Append( '<OtrasSenas>' +
               escape( str( inv.company_id.street or 'NA' ) ) + '</OtrasSenas>' )
    sb.Append( '</Ubicacion>' )
    sb.Append( '<Telefono>' )
    sb.Append( '<CodigoPais>' + str(inv.company_id.phone_code ) + '</CodigoPais>' )
    sb.Append( '<NumTelefono>' + str(
               re.sub( '[^0-9]+', '', inv.company_id.phone )) + '</NumTelefono>' )
    sb.Append( '</Telefono>' )
    sb.Append( '<CorreoElectronico>' +
               str( inv.company_id.email ) + '</CorreoElectronico>' )
    sb.Append( '</Emisor>' )
    sb.Append( '<Receptor>' )
    sb.Append( '<Nombre>' + escape( str( inv.partner_id.name[:80] ) ) + '</Nombre>' )

    if inv.partner_id.identification_id.code == '05':
        sb.Append( '<IdentificacionExtranjero>' +
                   str(inv.partner_id.vat ) + '</IdentificacionExtranjero>' )
    else:
        sb.Append( '<Identificacion>' )
        sb.Append( '<Tipo>' + str(inv.partner_id.identification_id.code ) + '</Tipo>' )
        sb.Append( '<Numero>' + str(inv.partner_id.vat) + '</Numero>' )
        sb.Append( '</Identificacion>' )

    sb.Append( '<Ubicacion>' )
    sb.Append( '<Provincia>' +
               str( inv.partner_id.state_id.code or '' ) + '</Provincia>' )
    sb.Append( '<Canton>' + str( inv.partner_id.county_id.code or '' ) + '</Canton>' )
    sb.Append( '<Distrito>' +
               str( inv.partner_id.district_id.code or '' ) + '</Distrito>' )
    sb.Append(
        '<Barrio>' + str( inv.partner_id.neighborhood_id.code or '00' ) + '</Barrio>' )
    sb.Append( '<OtrasSenas>' +
               escape( str( inv.partner_id.street or 'NA' ) ) + '</OtrasSenas>' )
    sb.Append( '</Ubicacion>' )
    sb.Append( '<Telefono>' )
    sb.Append( '<CodigoPais>' + str(inv.partner_id.phone_code) + '</CodigoPais>' )
    sb.Append( '<NumTelefono>' + str(
               re.sub( '[^0-9]+', '', inv.partner_id.phone )) + '</NumTelefono>' )
    sb.Append( '</Telefono>' )
    sb.Append( '<CorreoElectronico>' +
               str( inv.partner_id.email ) + '</CorreoElectronico>' )
    sb.Append( '</Receptor>' )
    sb.Append( '<CondicionVenta>' + str(sale_conditions) + '</CondicionVenta>' )
    sb.Append( '<PlazoCredito>' +
               str( inv.payment_term_id and inv.payment_term_id.line_ids[0].days or '0' ) + '</PlazoCredito>' )
    sb.Append( '<MedioPago>' + str(inv.payment_methods_id.sequence or '01') + '</MedioPago>' )
    sb.Append( '<DetalleServicio>' )

    detalle_factura = lines
    response_json = json.loads( detalle_factura )

    for (k, v) in response_json.items():
        numero_linea = numero_linea + 1

        sb.Append( '<LineaDetalle>' )
        sb.Append( '<NumeroLinea>' + str( numero_linea ) + '</NumeroLinea>' )
        # sb.Append('<CodigoComercial>' + str(str(v['codigoProducto']) + '</CodigoComercial>')
        sb.Append( '<Cantidad>' + str( v['cantidad'] ) + '</Cantidad>' )
        sb.Append( '<UnidadMedida>' +
                   str( v['unidadMedida'] ) + '</UnidadMedida>' )
        sb.Append( '<Detalle>' + str( v['detalle'] ) + '</Detalle>' )
        sb.Append( '<PrecioUnitario>' +
                   str( v['precioUnitario'] ) + '</PrecioUnitario>' )
        sb.Append( '<MontoTotal>' + str( v['montoTotal'] ) + '</MontoTotal>' )
        if v.get( 'montoDescuento' ):
            sb.Append( '<Descuento>' )
            sb.Append( '<MontoDescuento>' +
                       str( v['montoDescuento'] ) + '</MontoDescuento>' )
            if v.get( 'naturalezaDescuento' ):
                sb.Append( '<NaturalezaDescuento>' +
                           str( v['naturalezaDescuento'] ) + '</NaturalezaDescuento>' )
            sb.Append( '</Descuento>' )

        sb.Append( '<SubTotal>' + str( v['subtotal'] ) + '</SubTotal>' )

        # TODO: ¿qué es base imponible? ¿porqué podría ser diferente del subtotal?
        # sb.Append('<BaseImponible>' + str(str(v['subtotal']) + '</BaseImponible>')

        if v.get( 'impuesto' ):
            for (a, b) in v['impuesto'].items():
                sb.Append( '<Impuesto>' )
                sb.Append( '<Codigo>' + str( b['codigo'] ) + '</Codigo>' )
                sb.Append( '<CodigoTarifa>' +
                           str( b['iva_tax_code'] ) + '</CodigoTarifa>' )
                sb.Append( '<Tarifa>' + str( b['tarifa'] ) + '</Tarifa>' )
                sb.Append( '<Monto>' + str( b['monto'] ) + '</Monto>' )

                if b.get( 'exoneracion' ):
                    sb.Append( '<Exoneracion>' )
                    sb.Append( '<TipoDocumento>' +
                               str(inv.partner_id.type_exoneration.code) + '</TipoDocumento>' )
                    sb.Append( '<NumeroDocumento>' +
                               str(inv.partner_id.exoneration_number) + '</NumeroDocumento>' )
                    sb.Append( '<NombreInstitucion>' +
                               str(inv.partner_id.institution_name) + '</NombreInstitucion>' )
                    sb.Append( '<FechaEmision>' +
                               str( inv.partner_id.date_issue ) + 'T00:00:00-06:00' + '</FechaEmision>' )
                    sb.Append( '<PorcentajeExoneracion>' +
                               str( b['exoneracion']['porcentajeCompra'] ) + '</PorcentajeExoneracion>' )
                    sb.Append( '<MontoExoneracion>' +
                               str( b['exoneracion']['montoImpuesto'] ) + '</MontoExoneracion>' )
                    sb.Append( '</Exoneracion>' )

                sb.Append( '</Impuesto>' )
        sb.Append( '<ImpuestoNeto>' + str( v['impuestoNeto'] ) + '</ImpuestoNeto>' )

        sb.Append( '<MontoTotalLinea>' +
                   str( v['montoTotalLinea'] ) + '</MontoTotalLinea>' )
        sb.Append( '</LineaDetalle>' )
    sb.Append( '</DetalleServicio>' )

    # TODO: ¿Cómo implementar otros cargos a nivel de UI y model en Odoo?
    if otrosCargos:
        sb.Append( '<OtrosCargos>' )
        for otro_cargo in otrosCargos:
            sb.Append( '<TipoDocumento>' +
                       str( otrosCargos[otro_cargo]['TipoDocumento'] ) +
                       '</TipoDocumento>' )

            if otrosCargos[otro_cargo].get( 'NumeroIdentidadTercero' ):
                sb.Append( '<NumeroIdentidadTercero>' +
                           str( otrosCargos[otro_cargo]['NumeroIdentidadTercero'] ) +
                           '</NumeroIdentidadTercero>' )

            if otrosCargos[otro_cargo].get( 'NombreTercero' ):
                sb.Append( '<NombreTercero>' +
                           str( otrosCargos[otro_cargo]['NombreTercero'] ) +
                           '</NombreTercero>' )

            sb.Append( '<Detalle>' +
                       str( otrosCargos[otro_cargo]['Detalle'] ) +
                       '</Detalle>' )

            if otrosCargos[otro_cargo].get( 'Porcentaje' ):
                sb.Append( '<Porcentaje>' +
                           str( otrosCargos[otro_cargo]['Porcentaje'] ) +
                           '</Porcentaje>' )

            sb.Append( '<MontoCargo>' +
                       str( otrosCargos[otro_cargo]['MontoCargo'] ) +
                       '</MontoCargo>' )
        sb.Append( '</OtrosCargos>' )

    sb.Append( '<ResumenFactura>' )
    sb.Append( '<CodigoTipoMoneda><CodigoMoneda>' +
               str( inv.currency_id.name ) +
               '</CodigoMoneda><TipoCambio>' +
               str( currency_rate ) +
               '</TipoCambio></CodigoTipoMoneda>' )

    sb.Append( '<TotalServGravados>' +
               str( total_servicio_gravado ) + '</TotalServGravados>' )
    sb.Append( '<TotalServExentos>' +
               str( total_servicio_exento ) + '</TotalServExentos>' )

    # TODO: Hay que calcular TotalServExonerado
    sb.Append( '<TotalServExonerado>' + str( totalServExonerado ) + '</TotalServExonerado>' )

    sb.Append( '<TotalMercanciasGravadas>' +
               str( total_mercaderia_gravado ) + '</TotalMercanciasGravadas>' )
    sb.Append( '<TotalMercanciasExentas>' +
               str( total_mercaderia_exento ) + '</TotalMercanciasExentas>' )

    # TODO: Hay que calcular TotalMercExonerada
    sb.Append( '<TotalMercExonerada>' + str( totalMercExonerada ) + '</TotalMercExonerada>' )

    sb.Append( '<TotalGravado>' + str( total_servicio_gravado +
                                       total_mercaderia_gravado ) + '</TotalGravado>' )
    sb.Append( '<TotalExento>' + str( total_servicio_exento +
                                      total_mercaderia_exento ) + '</TotalExento>' )

    # TODO: Hay que calcular TotalExonerado
    sb.Append( '<TotalExonerado>' + str( totalServExonerado + totalMercExonerada ) + '</TotalExonerado>' )

    # TODO: agregar los exonerados en la suma
    sb.Append( '<TotalVenta>' + str(
        total_servicio_gravado + total_mercaderia_gravado + total_servicio_exento + total_mercaderia_exento + totalServExonerado + totalMercExonerada ) + '</TotalVenta>' )

    sb.Append( '<TotalDescuentos>' +
               str( round( total_descuento, 2 ) ) + '</TotalDescuentos>' )
    sb.Append( '<TotalVentaNeta>' +
               str( round( base_total, 2 ) ) + '</TotalVentaNeta>' )
    sb.Append( '<TotalImpuesto>' +
               str( round( total_impuestos, 2 ) ) + '</TotalImpuesto>' )

    # TODO: Hay que calcular el TotalIVADevuelto
    # sb.Append('<TotalIVADevuelto>' + str(str(¿de dónde sacamos esto?) + '</TotalIVADevuelto>')

    # TODO: Hay que calcular el TotalOtrosCargos
    # sb.Append('<TotalOtrosCargos>' + str(str(¿de dónde sacamos esto?) + '</TotalOtrosCargos>')

    sb.Append( '<TotalComprobante>' + str( round( base_total +
                                                  total_impuestos, 2 ) ) + '</TotalComprobante>' )
    sb.Append( '</ResumenFactura>' )
    sb.Append( '<Otros>' )
    sb.Append( '<OtroTexto>' +
               str( invoice_comments or 'Test FE V4.3' ) + '</OtroTexto>' )
    sb.Append( '</Otros>' )

    sb.Append( '</FacturaElectronica>' )

    return sb


def gen_xml_v42(inv, date_issuance, sale_conditions,
                   total_servicio_gravado, total_servicio_exento,
                   total_mercaderia_gravado, total_mercaderia_exento,
                   base_total, total_impuestos, total_descuento,
                   lines, currency_rate, invoice_comments):
    numero_linea = 0

    if inv._name == 'pos.order':
        plazo_credito = '0'
        cod_moneda = inv.company_id.currency_id.name
    else:
        plazo_credito = inv.payment_term_id and inv.payment_term_id.line_ids[0].days or 0
        cod_moneda = inv.currency_id.name

    sb = utils.StringBuilder()
    sb.Append(
        '<FacturaElectronica xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' )
    sb.Append(
        'xmlns="https://tribunet.hacienda.go.cr/docs/esquemas/2017/v4.2/facturaElectronica" ' )
    sb.Append(
        'xsi:schemaLocation="https://tribunet.hacienda.go.cr/docs/esquemas/2017/v4.2/facturaElectronica ' )
    sb.Append(
        'https://tribunet.hacienda.go.cr/docs/esquemas/2017/v4.2/FacturaElectronica_V.4.2.xsd">' )
    sb.Append( '<Clave>' + str(inv.number_electronic) + '</Clave>' )
    sb.Append( '<NumeroConsecutivo>' +
               inv.number_electronic[21:41] + '</NumeroConsecutivo>' )
    sb.Append( '<FechaEmision>' + date_issuance + '</FechaEmision>' )
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

    vat = inv.partner_id and inv.partner_id.vat and re.sub( '[^0-9]', '', inv.partner_id.vat )
    if inv.partner_id and vat:
        if not inv.partner_id.identification_id:
            if len( vat ) == 9:  # cedula fisica
                id_code = '01'
            elif len( vat ) == 10:  # cedula juridica
                id_code = '02'
            elif len( vat ) == 11 or len( vat ) == 12:  # dimex
                id_code = '03'
            else:
                id_code = '05'
        else:
            id_code = inv.partner_id.identification_id.code

        sb.Append( '<Receptor>' )
        sb.Append( '<Nombre>' + escape( str( inv.partner_id.name[:80] ) ) + '</Nombre>' )

        if id_code == '05':
            sb.Append( '<IdentificacionExtranjero>' + vat + '</IdentificacionExtranjero>' )
        else:
            sb.Append( '<Identificacion>' )
            sb.Append( '<Tipo>' + id_code + '</Tipo>' )
            sb.Append( '<Numero>' + vat + '</Numero>' )
            sb.Append( '</Identificacion>' )

        if inv.partner_id.state_id and inv.partner_id.county_id and inv.partner_id.district_id and inv.partner_id.neighborhood_id:
            sb.Append( '<Ubicacion>' )
            sb.Append( '<Provincia>' + str( inv.partner_id.state_id.code or '' ) + '</Provincia>' )
            sb.Append( '<Canton>' + str( inv.partner_id.county_id.code or '' ) + '</Canton>' )
            sb.Append( '<Distrito>' + str( inv.partner_id.district_id.code or '' ) + '</Distrito>' )
            sb.Append( '<Barrio>' + str( inv.partner_id.neighborhood_id.code or '00' ) + '</Barrio>' )
            sb.Append( '<OtrasSenas>' + escape( str( inv.partner_id.street or 'NA' ) ) + '</OtrasSenas>' )
            sb.Append( '</Ubicacion>' )
        telefono_receptor = inv.partner_id.phone and re.sub( '[^0-9]+', '', inv.partner_id.phone )
        if telefono_receptor:
            sb.Append( '<Telefono>' )
            sb.Append( '<CodigoPais>' + inv.partner_id.phone_code or '506' + '</CodigoPais>' )
            sb.Append( '<NumTelefono>' + telefono_receptor + '</NumTelefono>' )
            sb.Append( '</Telefono>' )
        match = inv.partner_id.email and re.match( r'^(\s?[^\s,]+@[^\s,]+\.[^\s,]+\s?,)*(\s?[^\s,]+@[^\s,]+\.[^\s,]+)$',
                                                   inv.partner_id.email.lower() )
        if match:
            email_receptor = inv.partner_id.email
        else:
            email_receptor = 'indefinido@indefinido.com'
        sb.Append( '<CorreoElectronico>' + email_receptor + '</CorreoElectronico>' )
        sb.Append( '</Receptor>' )
    sb.Append( '<CondicionVenta>' + sale_conditions + '</CondicionVenta>' )
    sb.Append( '<PlazoCredito>' + str( plazo_credito ) + '</PlazoCredito>' )
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
            sb.Append( '<Descuento><MontoDescuento>' +
                       str( v['montoDescuento'] ) + '</MontoDescuento>' )
            if v.get( 'naturalezaDescuento' ):
                sb.Append( '<NaturalezaDescuento>' +
                           str( v['naturalezaDescuento'] ) + '</NaturalezaDescuento>' )
            sb.Append( '</Descuento>' )
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
                        sb.Append( '</Exoneracion>' )

                sb.Append( '</Impuesto>' )
        sb.Append( '<MontoTotalLinea>' +
                   str( v['montoTotalLinea'] ) + '</MontoTotalLinea>' )
        sb.Append( '</LineaDetalle>' )
    sb.Append( '</DetalleServicio>' )
    sb.Append( '<ResumenFactura>' )
    sb.Append( '<CodigoMoneda>' + str( cod_moneda ) + '</CodigoMoneda>' )
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
               str( round( total_descuento, 5 ) ) + '</TotalDescuentos>' )
    sb.Append( '<TotalVentaNeta>' +
               str( round( base_total, 5 ) ) + '</TotalVentaNeta>' )
    sb.Append( '<TotalImpuesto>' +
               str( round( total_impuestos, 5 ) ) + '</TotalImpuesto>' )
    sb.Append( '<TotalComprobante>' + str( round( base_total +
                                                  total_impuestos, 5 ) ) + '</TotalComprobante>' )
    sb.Append( '</ResumenFactura>' )
    sb.Append( '<Normativa>' )
    sb.Append( '<NumeroResolucion>DGT-R-48-2016</NumeroResolucion>' )
    sb.Append( '<FechaResolucion>07-10-2016 08:00:00</FechaResolucion>' )
    sb.Append( '</Normativa>' )
    if invoice_comments:
        sb.Append( '<Otros>' )
        sb.Append( '<OtroTexto>' + str( invoice_comments ) + '</OtroTexto>' )
        sb.Append( '</Otros>' )

    sb.Append( '</FacturaElectronica>' )

    # felectronica_bytes = str(sb)
    return sb
    # return stringToBase64(felectronica_bytes)


def gen_xml_fee_v43(inv, consecutivo, date, sale_conditions, total_servicio_gravado, total_servicio_exento,
                    totalServExonerado,
                    total_mercaderia_gravado, total_mercaderia_exento, totalMercExonerada, totalOtrosCargos, base_total,
                    total_impuestos, total_descuento,
                    lines, otrosCargos, currency_rate, invoice_comments):
    numero_linea = 0

    sb = utils.StringBuilder()
    sb.Append( '<?xml version="1.0" encoding="utf-8"?>' )
    sb.Append(
        '<FacturaElectronica xmlns="https://cdn.comprobanteselectronicos.go.cr/xml-schemas/v4.3/facturaElectronicaExportacion" ' )
    sb.Append(
        'xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:xsd="http://www.w3.org/2001/XMLSchema" ' )
    sb.Append( 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' )
    sb.Append(
        'xsi:schemaLocation="https://www.hacienda.go.cr/ATV/ComprobanteElectronico/docs/esquemas/2016/v4.3/FacturaElectronicaExportacion_V4.3.xsd">' )

    sb.Append( '<Clave>' + str(inv.number_electronic) + '</Clave>' )
    sb.Append( '<CodigoActividad>' +
               inv.company_id.activity_id.code + '</CodigoActividad>' )
    sb.Append( '<NumeroConsecutivo>' + consecutivo + '</NumeroConsecutivo>' )
    sb.Append( '<FechaEmision>' + date + '</FechaEmision>' )
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

    if inv.partner_id.identification_id.code == '05':
        sb.Append( '<IdentificacionExtranjero>' +
                   inv.partner_id.vat + '</IdentificacionExtranjero>' )
    else:
        sb.Append( '<Identificacion>' )
        sb.Append( '<Tipo>' + inv.partner_id.identification_id.code + '</Tipo>' )
        sb.Append( '<Numero>' + inv.partner_id.vat + '</Numero>' )
        sb.Append( '</Identificacion>' )

    sb.Append( '<Ubicacion>' )
    sb.Append( '<Provincia>' +
               str( inv.partner_id.state_id.code or '' ) + '</Provincia>' )
    sb.Append( '<Canton>' + str( inv.partner_id.county_id.code or '' ) + '</Canton>' )
    sb.Append( '<Distrito>' +
               str( inv.partner_id.district_id.code or '' ) + '</Distrito>' )
    sb.Append(
        '<Barrio>' + str( inv.partner_id.neighborhood_id.code or '00' ) + '</Barrio>' )
    sb.Append( '<OtrasSenas>' +
               escape( str( inv.partner_id.street or 'NA' ) ) + '</OtrasSenas>' )
    sb.Append( '</Ubicacion>' )
    sb.Append( '<Telefono>' )
    sb.Append( '<CodigoPais>' + inv.partner_id.phone_code + '</CodigoPais>' )
    sb.Append( '<NumTelefono>' +
               re.sub( '[^0-9]+', '', inv.partner_id.phone ) + '</NumTelefono>' )
    sb.Append( '</Telefono>' )
    sb.Append( '<CorreoElectronico>' +
               str( inv.partner_id.email ) + '</CorreoElectronico>' )
    sb.Append( '</Receptor>' )
    sb.Append( '<CondicionVenta>' + sale_conditions + '</CondicionVenta>' )
    sb.Append( '<PlazoCredito>' +
               str( inv.partner_id.property_payment_term_id.line_ids[0].days or 0 ) + '</PlazoCredito>' )
    sb.Append( '<MedioPago>' + (inv.payment_methods_id.sequence or '01') + '</MedioPago>' )
    sb.Append( '<DetalleServicio>' )

    detalle_factura = lines
    response_json = json.loads( detalle_factura )

    for (k, v) in response_json.items():
        numero_linea = numero_linea + 1

        sb.Append( '<LineaDetalle>' )
        sb.Append( '<NumeroLinea>' + str( numero_linea ) + '</NumeroLinea>' )

        # TODO: Implementar esto en la interfaz y en la factura
        # sb.Append('<PartidaArancelaria>' +  + '</PartidaArancelaria>')

        sb.Append( '<CodigoComercial>' +
                   str( v['codigoProducto'] ) + '</CodigoComercial>' )
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

    sb.Append( '</FacturaElectronica>' )

    # felectronica_bytes = str(sb)

    # return stringToBase64(felectronica_bytes)
    return sb