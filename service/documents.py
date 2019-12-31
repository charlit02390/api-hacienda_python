import json
from . import api_facturae
from . import fe_enums
from . import makepdf
import base64

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
    _activity_code = data['codigo_actividad']
    _other_phone = data['otro_telefono']
    _receptor = data['receptor']
    _sale_condition = data['condicion_venta']
    _credit_term = data['plazo_credito']
    _payment_methods = data['medio_pago']
    _lines = data['detalles']
    _currency = data['codigo_moneda']
    _total_serv_taxed = data['total_serv_gravados']
    _total_serv_untaxed = data['total_serv_exentos']
    _total_serv_exone = data['total_serv_exonerado']
    _total_merch_taxed = data['total_merc_gravados']
    _total_merch_untaxed = data['total_merc_exentos']
    _total_merch_exone = data['total_merc_exonerada']
    _total_taxed = data['total_gravado']
    _total_untaxed = data['total_exento']
    _total_exone = data['total_exonerado']
    _total_sales = data['total_ventas']
    _total_discount = data['total_descuentos']
    _total_net_sales = data['total_ventas_netas']
    _total_taxes = data['total_impuestos']
    _total_return_iva = data['total_iva_devuelto']
    _total_other_charges = data['total_otros_cargos']
    _total_document = data['total_comprobante']
    _other_charges = data['otros_cargos']
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

    '''pdf = makepdf.render_pdf(company_data, _type_document, _key_mh, _consecutive, _datestr, _sale_condition,
                             _activity_code, _receptor, _total_serv_taxed, _total_serv_untaxed, _total_serv_exone,
                             _total_merch_taxed, _total_merch_untaxed, _total_merch_exone, _total_other_charges,
                             _total_net_sales, _total_taxes, _total_discount, _lines, _other_charges, _others,
                             _reference, _payment_methods, _credit_term, _currency, _total_taxed, _total_exone,
                             _total_untaxed, _total_sales, _total_return_iva, _total_document);
    pdfencoded = base64.b64encode(pdf);'''

    result = documents.save_document(_company_user, _key_mh, xmlencoded, 'creado', datecr, _type_document,
                                     _receptor['tipo_identificacion'], _receptor['numero_identificacion'],
                                     _total_document , _total_taxes)
    if result:
        return {'Respuesta Hacienda': 'creado'}
    else:
        return {'Error in Database': 'Found a problem when tried to save the document'}


def validate_documents():
    return


def validate_document(company_user, key_mh):
    document_data = documents.get_document(key_mh)
    company_data = companies.get_company_data(company_user)
    date = api_facturae.get_time_hacienda(False)

    token_m_h = api_facturae.get_token_hacienda(company_user, company_data[0]['user_mh'], company_data[0]['pass_mh'],
                                                company_data[0]['env'])

    response_json = api_facturae.send_xml_fe(company_data[0], document_data[0], key_mh, token_m_h, date, document_data[0]['signxml'],
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

    response_json = api_facturae.consulta_documentos(key_mh, company_data[0]['env'], token_m_h, date, document_data[0]['document_type'])

    response_status = response_json.get('ind-estado')
    response_text = response_json.get('respuesta-xml')
    result = documents.update_document(company_user, key_mh, response_text, response_status, date)
    if result:
        return {'Respuesta Hacienda': response_status, 'xml-respuesta': response_text}
    else:
        return {'Error in Database': 'Found a problem when tried to save the document'}
