from copy import deepcopy
from datetime import datetime

from service import fe_enums, utils
from helpers.debugging import time_my_func
from helpers.errors.exceptions import ValidationError
from helpers.errors.enums import ValidationErrorCodes


DATETIME_DISPLAY_FORMAT = '%d-%m-%Y'
DEFAULT_MONEY_VALUE = '0.00000'
DEFAULT_PDF_DECIMAL_VALUE = '0.0'
LOCAL_CURRENCY = 'CRC'
CREDIT_CONDITION_CODE = '02'
CREDIT_CURRENCY_EXCHANGE_POLICY = """\
Si la factura no se cancela dentro del mes de su facturación, \
se debe pagar al tipo de cambio oficial al dia de su cancelación."""


@time_my_func
def arrange_data(data: dict) -> tuple:
    xml_data = arrange_xml_data(data)
    pdf_data = arrange_pdf_data(data)

    xml_data['detalles'], pdf_data['lines'] = arrange_details(data['detalles'])

    return (xml_data, pdf_data)


@time_my_func
def arrange_xml_data(data: dict) -> dict:
    xml_data = deepcopy(data)

    xml_data['tipo'] = fe_enums.TipoDocumentoApi[data['tipo']]
    xml_data['fechafactura'] = parse_datetime(data['fechafactura'], 'fechafactura').isoformat()
    if 'referencia' in xml_data:
        references = xml_data.pop('referencia')
        if not isinstance(references, str): # if str, it's not useful, so let it out of our data
            if isinstance(references, dict) \
                    and len(references):
                references = [references]

            for ref in references:
                if 'fecha' in ref:
                    ref['fecha'] = parse_datetime(ref['fecha'], 'referencia => fecha').isoformat()

            if references:
                xml_data['referencia'] = references

    if 'receptor' in xml_data:
        recipient = xml_data['receptor']
        
        additional_emails = recipient.get('correosAdicionales', [])
        if additional_emails:
            additional_emails = list(set(additional_emails)) # remove duplicates
        else: # for now... falling back to "correo_gastos" if exists
            fallback_email = recipient.get('correo_gastos')
            if fallback_email and isinstance(fallback_email, str):
                additional_emails.append(fallback_email)

        recipient['correosAdicionales'] = additional_emails

    xml_data['totalServGravados'] = data.get('totalServGravados', DEFAULT_MONEY_VALUE)
    xml_data['totalServExentos'] = data.get('totalServExentos', DEFAULT_MONEY_VALUE)
    xml_data['totalServExonerado'] = data.get('totalServExonerado', DEFAULT_MONEY_VALUE)
    xml_data['totalMercanciasGravados'] = data.get('totalMercanciasGravados', DEFAULT_MONEY_VALUE)
    xml_data['totalMercanciasExentos'] = data.get('totalMercanciasExentos', DEFAULT_MONEY_VALUE)
    xml_data['totalMercExonerada'] =  data.get('totalMercExonerada', DEFAULT_MONEY_VALUE)
    xml_data['totalGravados'] = data.get('totalGravados', DEFAULT_MONEY_VALUE)
    xml_data['totalExentos'] =  data.get('totalExentos', DEFAULT_MONEY_VALUE)
    xml_data['totalExonerado'] = data.get('totalExonerado', DEFAULT_MONEY_VALUE)
    xml_data['totalDescuentos'] = data.get('totalDescuentos', DEFAULT_MONEY_VALUE)
    xml_data['totalImpuestos'] = data.get('totalImpuestos', DEFAULT_MONEY_VALUE)
    xml_data['totalIVADevuelto'] = data.get('totalIVADevuelto', DEFAULT_MONEY_VALUE)
    xml_data['totalOtrosCargos'] = data.get('totalOtrosCargos', DEFAULT_MONEY_VALUE)

    return xml_data


@time_my_func
def arrange_pdf_data(data: dict) -> dict:
    pdf_data = {}

    body_data = build_pdf_body_data(data)
    pdf_data['body'] = body_data

    header_data = build_pdf_header_data(data)
    pdf_data['header'] = header_data

    footer_data = build_pdf_footer_data(data)
    pdf_data['footer'] = footer_data

    return pdf_data


@time_my_func
def arrange_details(details: list) -> tuple:
    xml_details = []
    pdf_details = []

    line_count = 1
    for i in range(len(details)):
        line = deepcopy(details[i])

        pdf_line = {
            '_cabys': line['codigo'],
            'detalle': line.get('detalle',''),
            'cantidad': utils.stringRound(line['cantidad']) \
                    if line['cantidad'].strip('0.') \
                    else DEFAULT_PDF_DECIMAL_VALUE,
            'precioUnitario': utils.stringRound(line['precioUnitario']) \
                    if line['precioUnitario'].strip('0.') \
                    else DEFAULT_PDF_DECIMAL_VALUE,
            'impuestoNeto': utils.stringRound(line['impuestoNeto']) \
                    if line['impuestoNeto'].strip('0.') \
                    else DEFAULT_PDF_DECIMAL_VALUE,
            'subtotal': utils.stringRound(line['subtotal']) \
                    if line['subtotal'].strip('0.') \
                    else DEFAULT_PDF_DECIMAL_VALUE,
            'totalLinea': utils.stringRound(line['totalLinea']) \
                    if line['totalLinea'].strip('0.') \
                    else DEFAULT_PDF_DECIMAL_VALUE
        }
        if 'impuesto' in line:
            pdf_line['impuesto'] = deepcopy(line['impuesto'])


        cabys = line['codigo']
        amountTotal = line['montoTotal'].strip('0.')
        if cabys and amountTotal:
            xml_line = deepcopy(line)
            xml_line['numero'] = pdf_line['numero'] = line_count
            xml_details.append(xml_line)
            line_count += 1
        else:
            pdf_line['numero'] = '∟'
            pdf_line['_cabys'] =\
                pdf_line['cantidad'] =\
                pdf_line['precioUnitario'] =\
                pdf_line['impuestoNeto'] =\
                pdf_line['subtotal'] =\
                pdf_line['totalLinea'] = ''


        pdf_details.append(pdf_line)

    return (xml_details, pdf_details)


@time_my_func
def build_pdf_body_data(data: dict) -> dict:
    total_document = utils.stringRound(data['totalComprobantes'])
    recipient = data['receptor']
    currency = data['codigoTipoMoneda']

    body_data = {}
    body_data['key_mh'] = data['clavelarga']
    body_data['total_document'] = total_document
    body_data['total_taxes'] = utils.stringRound(data['totalImpuestos'])
    body_data['total_discounts'] = utils.stringRound(data['totalDescuentos'])
    body_data['total_sales'] = utils.stringRound(data['totalVentas'])
    body_data['receiver'] = recipient

    payment_methods_csvs = ', '.join(
        list(
            fe_enums.paymentMethods.get(
                pm.get('codigo'), 'Efectivo'
            ) for pm in data['medioPago']
        )
    )
    body_data['payment_method'] = payment_methods_csvs

    body_data['sale_condition'] = fe_enums.saleConditions.get(
        data['condicionVenta'], 'No especificada'
    )

    body_data['currency'] = {
        'tipoMoneda': currency['tipoMoneda'],
        'tipoCambio': utils.stringRound(currency['tipoCambio'])
    }

    body_data['currencySymbol'] = fe_enums.currencies.get(
        currency['tipoMoneda'], ''
    )

    body_data['activity_code'] = data['codigoActividad']
    body_data['total_document_words'] = utils.numToWord(
        total_document, currency['tipoMoneda']
    ).upper()
    body_data['total_returned_iva'] = utils.stringRound(data['totalIVADevuelto'])
    body_data['type_iden_receptor'] = fe_enums.tipoCedulaPDF.get(
        recipient.get('tipoIdentificacion'),
        'Tipo de identificación no especificada'
    )

    order_num = data.get('numOrden', data.get('numFecha', '')).strip();
    # just making sure "order_num" ain't suddenly a date...
    try:
        parse_datetime(order_num, 'numOrden/numFecha')
        order_num = None
    except ValidationError:
        pass
    if order_num:
        body_data['order_num'] =  order_num

    sale_condition = data['condicionVenta']
    if sale_condition == '02':
        issued_date = parse_datetime(
            data['fechafactura'], 'fechafactura'
        )
        term_days = data['plazoCredito']
        body_data['due_date'] = (issued_date + timedelta(
            days=int(term_days)
        )).strftime(DATETIME_DISPLAY_FORMAT)
        body_data['credit_term'] = term_days

    details = data['detalles']
    for line in details:
        exemption_found = False
        for tax in line.get('impuesto', []):
            exemption = tax.get('exoneracion')
            if exemption:
                body_data['exemption'] = {
                    'doc_type': fe_enums.ExemptionDocType[
                        exemption['Tipodocumento']
                    ],
                    'doc_number': exemption['NumeroDocumento'],
                    'issuer': exemption['NombreInstitucion'],
                    'issued_date': parse_datetime(
                        exemption['FechaEmision'], 'exoneracion => FechaEmision'
                    ).isoformat(),
                    'percentage': exemption['porcentajeExoneracion'],
                    'total_amount': data['totalExonerado']
                    }
                exemption_found = True
                break
        if exemption_found:
            break

    return body_data


@time_my_func
def build_pdf_header_data(data: dict) -> dict:
    header_data = {}

    api_doc_type = fe_enums.TipoDocumentoApi[data['tipo']]
    header_data['document_type'] = fe_enums.tagNamePDF.get(
        api_doc_type, 'Indefinido'
    )
    header_data['consecutive'] =  data['consecutivo']
    header_data['ref_num'] = data['numReferencia']
    header_data['date'] = parse_datetime(
        data['fechafactura'], 'fechafactura'
    ).strftime(DATETIME_DISPLAY_FORMAT)

    return header_data


@time_my_func
def build_pdf_footer_data(data: dict) -> dict:
    currency = data['codigoTipoMoneda']

    footer_data =  {}

    pdf_notes = data.get('notas',
                            data.get('observaciones',
                                  data.get('piedepagina', [])
        )
    )
    if not isinstance(pdf_notes, list):
        pdf_notes = []

    if data['condicionVenta'] == CREDIT_CONDITION_CODE \
            and currency['tipoMoneda'] != LOCAL_CURRENCY:
        pdf_notes.insert(0,
                         CREDIT_CURRENCY_EXCHANGE_POLICY)

    footer_data['notes'] = pdf_notes
    return footer_data


@time_my_func
def parse_datetime(value, field) -> datetime:
    if isinstance(value, datetime):
        return value

    EXPECTED_DATETIME_FORMATS = (
        '%d-%m-%YT%H:%M:%S%z',
        '%d/%m/%Y'
        )
    parsed = None
    for format in EXPECTED_DATETIME_FORMATS:
        try:
            parsed = datetime.strptime(value, format)
            break
        except ValueError:
            pass

    if not parsed: # if we still couldn't parse it, try isoformat
        try: 
            parsed = datetime.fromisoformat(value)
        except ValueError as ver:
            raise ValidationError(value, field,
                                  status=ValidationErrorCodes.INVALID_DATETIME_FORMAT) from ver

    return parsed
