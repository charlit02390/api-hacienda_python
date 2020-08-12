from . import api_facturae
from . import fe_enums
from . import makepdf

import base64

from service import emails
from infrastructure import companies
from infrastructure import documents


def create_document(data):
    _company_user = data['nombre_usuario']
    _type_document = fe_enums.TipoDocumentoApi[data['tipo']]
    _situation = data['situacion']
    _consecutive = data['consecutivo']
    _key_mh = data['clave']
    _terminal = data['terminal']
    _branch = data['sucursal']
    _datestr = api_facturae.get_time_hacienda()
    datecr = api_facturae.get_time_hacienda(True)
    _activity_code = data['codigoActividad']
    _other_phone = data['otro_telefono']
    if data.get('receptor'):
        _receptor = data['receptor']
        _email = _receptor['correo']
        _email_costs = _receptor['correo_gastos']
    else:
        _receptor = None
        _email = None
        _email_costs = None
    _sale_condition = data['condicionVenta']
    _credit_term = data['plazoCredito']
    _payment_methods = data['medioPago']
    _lines = data['detalles']
    _currency = data['codigoTipoMoneda']
    _total_serv_taxed = data['totalServGravados']
    _total_serv_untaxed = data['totalServExentos']
    _total_serv_exone = data['totalServExonerado']
    _total_merch_taxed = data['totalMercanciasGravados']
    _total_merch_untaxed = data['totalMercanciasExentos']
    _total_merch_exone = data['totalMercExonerada']
    _total_taxed = data['totalGravados']
    _total_untaxed = data['totalExentos']
    _total_exone = data['totalExonerado']
    _total_sales = data['totalVentas']
    _total_discount = data['totalDescuentos']
    _total_net_sales = data['totalVentasNetas']
    _total_taxes = data['totalImpuestos']
    _total_return_iva = data['totalIVADevuelto']
    _total_other_charges = data['totalOtrosCargos']
    _total_document = data['totalComprobantes']
    _other_charges = data['otrosCargos']
    _reference = data['referencia']
    _others = data['otros']

    company_data = companies.get_company_data(_company_user)

    xml = api_facturae.gen_xml_v43(company_data, _type_document, _key_mh, _consecutive, _datestr, _sale_condition,
                                   _activity_code, _receptor, _total_serv_taxed, _total_serv_untaxed, _total_serv_exone,
                                   _total_merch_taxed, _total_merch_untaxed, _total_merch_exone, _total_other_charges,
                                   _total_net_sales, _total_taxes, _total_discount, _lines, _other_charges, _others,
                                   _reference, _payment_methods, _credit_term, _currency, _total_taxed, _total_exone,
                                   _total_untaxed, _total_sales, _total_return_iva, _total_document)
    xml_to_sign = str(xml)

    signature = companies.get_sign_data(_company_user)


    xml_sign = api_facturae.sign_xml(
        signature['signature'],
        company_data[0]['pin_sig'], xml_to_sign)

    xmlencoded = base64.b64encode(xml_sign)

    _logo = companies.get_logo_data(_company_user)
    _logo = _logo['logo'].decode('utf-8')
    pdf = makepdf.render_pdf(company_data, fe_enums.tagNamePDF[_type_document], _key_mh, _consecutive, datecr.strftime("%Y-%m-%d %H:%M:%S"), _sale_condition,
                             _activity_code, _receptor, _total_serv_taxed, _total_serv_untaxed, _total_serv_exone,
                             _total_merch_taxed, _total_merch_untaxed, _total_merch_exone, _total_other_charges,
                             _total_net_sales, _total_taxes, _total_discount, _lines, _other_charges, _others,
                             _reference, _payment_methods, _credit_term, _currency, _total_taxed, _total_exone,
                             _total_untaxed, _total_sales, _total_return_iva, _total_document, _logo);

    #Prueba de creacion de correo
    #emails.sent_email(pdf, xml_sign)

    pdfencoded = base64.b64encode(pdf);

    result = documents.save_document(_company_user, _key_mh, xmlencoded, 'creado', datecr, _type_document,
                                     _receptor, _total_document, _total_taxes, pdfencoded, _email, _email_costs)

    _id_company = company_data[0]['id']

    if result is True:
        result = save_document_lines(_lines, _id_company, _key_mh)

    if result is True:
        return {'Respuesta Hacienda': 'creado'}
    else:
        return {'Error in Database': 'Found a problem when tried to save the document'}


def save_document_lines(lines, id_company, key_mh):
    for _line in lines:
        _line_number = _line['numero']
        _quantity = _line['cantidad']
        _unity = _line['unidad']
        _detail = _line['detalle']
        _unit_price = _line['precioUnitario']
        _net_tax = _line['impuestoNeto']
        _total_line = _line['totalLinea']

        result = documents.save_document_line_info(id_company, _line_number, _quantity, _unity
                                                   , _detail, _unit_price, _net_tax, _total_line, key_mh)
        if result is True and _line.get('impuesto'):
            result = save_document_taxes(_line, id_company, _line_number, key_mh)

    return result


def save_document_taxes(line, id_company, line_number, key_mh):
    _taxes = line['impuesto']
    for _tax in _taxes:
        _rate_code = _tax['codigoTarifa']
        _code = _tax['codigo']
        _rate = _tax['tarifa']
        _amount = _tax['monto']
        result = documents.save_document_line_taxes(id_company, line_number, _rate_code,
                                                    _code, _rate, _amount, key_mh)
    return result


def validate_documents():
    return


def validate_document(company_user, key_mh):
    document_data = documents.get_document(key_mh)
    company_data = companies.get_company_data(company_user)
    date_cr= api_facturae.get_time_hacienda(False)
    date = api_facturae.get_time_hacienda(True)

    token_m_h = api_facturae.get_token_hacienda(company_user, company_data[0]['user_mh'], company_data[0]['pass_mh'],
                                                company_data[0]['env'])

    response_json = api_facturae.send_xml_fe(company_data[0], document_data[0], key_mh, token_m_h, date_cr,
                                             document_data[0]['signxml'],
                                             company_data[0]['env'])

    response_status = response_json.get('status')
    response_text = response_json.get('text')

    if 200 <= response_status <= 299:
        state_tributacion = 'procesando'
        return_message = response_text
    else:
        if response_text.find('ya fue recibido anteriormente') != -1:
            state_tributacion = 'procesando'
            return_message = 'Ya recibido anteriormente, se pasa a consultar'
        else:
            state_tributacion = 'procesando'
            return_message = response_text

    result = documents.update_document(company_user, key_mh, None, state_tributacion, date)
    if result:
        return {'Respuesta Hacienda': return_message}
    else:
        return {'Error in Database': 'Found a problem when tried to update the document'}


def consult_documents():
    return


def consult_document(company_user, key_mh):
    document_data = documents.get_document(key_mh)
    company_data = companies.get_company_data(company_user)
    date = api_facturae.get_time_hacienda(True)

    token_m_h = api_facturae.get_token_hacienda(company_user, company_data[0]['user_mh'], company_data[0]['pass_mh'],
                                                company_data[0]['env'])

    response_json = api_facturae.consulta_documentos(key_mh, company_data[0]['env'], token_m_h, date,
                                                     document_data[0]['document_type'])

    response_status = response_json.get('ind-estado')
    response_text = response_json.get('respuesta-xml')
    result = documents.update_document(company_user, key_mh, response_text, response_status, date)
    if response_status == 'aceptado':
        emails.sent_email_fe(document_data[0])
    if result:
        return {'Respuesta Hacienda': response_status, 'xml-respuesta': response_text}
    else:
        return {'Error in Database': 'Found a problem when tried to save the document'}


def processing_documents(company_user, key_mh, is_consult):
    if is_consult:
        result = consult_document(company_user, key_mh)
    else:
        result = validate_document(company_user, key_mh)
    return result


def document_report(company_user, document_type):
    result = documents.get_documentsreport(company_user, document_type)
    return {'documents': result}

