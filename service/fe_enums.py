# -*- coding: utf-8 -*-

from enum import Enum

UrlHaciendaToken = {
    'api-stag': 'https://idp.comprobanteselectronicos.go.cr/auth/realms/rut-stag/protocol/openid-connect/token',
    'api-prod': 'https://idp.comprobanteselectronicos.go.cr/auth/realms/rut/protocol/openid-connect/token',
}

UrlHaciendaRecepcion = {
    'api-stag': 'https://api.comprobanteselectronicos.go.cr/recepcion-sandbox/v1/recepcion/',
    'api-prod': 'https://api.comprobanteselectronicos.go.cr/recepcion/v1/recepcion/',
}

UrlHaciendaComprobantes = {
    'api-vouchers': 'https://api.comprobanteselectronicos.go.cr/recepcion/v1/comprobantes',
    'api-voucher': 'https://api.comprobanteselectronicos.go.cr/recepcion/v1/comprobantes/',
}

TipoCedula = {  # no se está usando !!
    'Fisico': 'fisico',
    'Juridico': 'juridico',
    'Dimex': 'dimex',
    'Nite': 'nite',
    'Extranjero': 'extranjero',
}

SituacionComprobante = {
    'normal': '1',
    'contingencia': '2',
    'sininternet': '3',
}

TipoDocumento = {
    'FE': '01',  # Factura Electrónica
    'ND': '02',  # Nota de Débito
    'NC': '03',  # Nota de Crédito
    'TE': '04',  # Tiquete Electrónico
    'CCE': '05',  # confirmacion comprobante electronico
    'CPCE': '06',  # confirmacion parcial comprobante electronico
    'RCE': '07',  # rechazo comprobante electronico
    'FEC': '08',  # Factura Electrónica de Compra
    'FEE': '09',  # Factura Electrónica de Exportación
}

TipoDocumentoApi = {
    '1': 'FE',  # Factura Electrónica
    '2': 'ND',  # Nota de Débito
    '3': 'NC',  # Nota de Crédito
    '4': 'TE',  # Tiquete Electrónico
    '5': 'CCE',  # confirmacion comprobante electronico
    '6': 'CPCE',  # confirmacion parcial comprobante electronico
    '7': 'RCE',  # rechazo comprobante electronico
    '8': 'FEC',  # Factura Electrónica de Compra
    '9': 'FEE',  # Factura Electrónica de Exportación
}

TipoDocumentApiSwapped = {v: k for k, v in TipoDocumentoApi.items()}

# Xmlns used by Hacienda
XmlnsHacienda = {
    'FE': 'https://cdn.comprobanteselectronicos.go.cr/xml-schemas/v4.3/facturaElectronica',  # Factura Electrónica
    'ND': 'https://cdn.comprobanteselectronicos.go.cr/xml-schemas/v4.3/notaDebitoElectronica',  # Nota de Débito
    'NC': 'https://cdn.comprobanteselectronicos.go.cr/xml-schemas/v4.3/notaCreditoElectronica',  # Nota de Crédito
    'TE': 'https://cdn.comprobanteselectronicos.go.cr/xml-schemas/v4.3/tiqueteElectronico',  # Tiquete Electrónico
    'FEC': 'https://cdn.comprobanteselectronicos.go.cr/xml-schemas/v4.3/facturaElectronicaCompra',
    # Factura Electrónica de Compra
    'FEE': 'https://cdn.comprobanteselectronicos.go.cr/xml-schemas/v4.3/facturaElectronicaExportacion',
    # Factura Electrónica de Exportación
}

schemaLocation = {
    'FE': 'https://www.hacienda.go.cr/ATV/ComprobanteElectronico/docs/esquemas/2016/v4.3/FacturaElectronica_V4.3.xsd',
    # Factura Electrónica
    'ND': 'https://www.hacienda.go.cr/ATV/ComprobanteElectronico/docs/esquemas/2016/v4.3/NotaDebitoElectronica_V4.3.xsd',
    # Nota de Débito
    'NC': 'https://www.hacienda.go.cr/ATV/ComprobanteElectronico/docs/esquemas/2016/v4.3/NotaCreditoElectronica_V4.3.xsd',
    # Nota de Crédito
    'TE': 'https://www.hacienda.go.cr/ATV/ComprobanteElectronico/docs/esquemas/2016/v4.3/TiqueteElectronico_V4.3.xsd',
    # Tiquete Electrónico
    'FEC': 'https://www.hacienda.go.cr/ATV/ComprobanteElectronico/docs/esquemas/2016/v4.3/FacturaElectronicaCompra_V4.3.xsd',
    # Factura Electrónica de Compra
    'FEE': 'https://www.hacienda.go.cr/ATV/ComprobanteElectronico/docs/esquemas/2016/v4.3/FacturaElectronicaExportacion_V4.3.xsd',
    # Factura Electrónica de Exportación
}

tagName = {
    'FE': 'FacturaElectronica',  # Factura Electrónica
    'ND': 'NotaDebitoElectronica',  # Nota de Débito
    'NC': 'NotaCreditoElectronica',  # Nota de Crédito
    'TE': 'TiqueteElectronico',  # Tiquete Electrónico
    'FEC': 'FacturaElectronicaCompra',  # Factura Electrónica de Compra
    'FEE': 'FacturaElectronicaExportacion',  # Factura Electrónica de Exportación
}

tagNamePDF = {
    'FE': 'Factura Electronica',  # Factura Electrónica
    'ND': 'Nota Debito Electronica',  # Nota de Débito
    'NC': 'Nota Credito Electronica',  # Nota de Crédito
    'TE': 'Tiquete Electronico',  # Tiquete Electrónico
    'FEC': 'Factura Electronica Compra',  # Factura Electrónica de Compra
    'FEE': 'Factura Electronica Exportacion',  # Factura Electrónica de Exportación
}

tipoCedulaPDF = {
    '01': 'Cédula Física',
    '02': 'Cédula Jurídica',
    '03': 'DIMEX',
    '04': 'NITE',
    '05': 'Cédula Extranjera',  # <- this one is not mentioned as a valid value for the XML...
}

currencies = {'USD': '$', 'CRC': '₡', 'EUR': '€'}

paymentMethods = {
    '01': 'Efectivo',
    '02': 'Tarjeta',
    '03': 'Cheque',
    '04': 'Transferencia - depósito bancario',
    '05': 'Recaudado por terceros',
    '99': 'Otro: '
}

saleConditions = {
    '01': 'Contado',
    '02': 'Crédito',
    '03': 'Consignación',
    '04': 'Apartado',
    '05': 'Arrendamiento con opción de compra',
    '06': 'Arrendamiento en función financiera',
    '07': 'Cobro a favor de un tercero',
    '08': 'Servicios prestados al Estado a crédito',
    '09': 'Pago del servicios prestados al Estado',
    '99': 'Otros: '
}

ExemptionDocType = {
    '01': 'Compras autorizadas',
    '02': 'Ventas exentas a diplomáticos',
    '03': 'Autorizado por Ley especial',
    '04': 'Exenciones Dirección General de Hacienda',
    '05': 'Transitorio V',
    '06': 'Transitorio IX',
    '07': 'Transitorio XVII',
    '99': 'Otros'
}

MessageCodeDesc = {
    '1': 'Aceptado',
    '2': 'Aceptación parcial',
    '3': 'Rechazado'
}

ServiceCodeTypes = {
    '01': 'Código del producto del vendedor',
    '02': 'Código del producto del comprador',
    '03': 'Código del producto asignado por la industria',
    '04': 'Código uso interno',
    '99': 'Otros'
}
