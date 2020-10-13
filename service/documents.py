from . import api_facturae
from . import fe_enums
from . import makepdf
from . import utils

import base64

from service import emails
from infrastructure import companies
from infrastructure import documents
from infrastructure.dbadapter import DbAdapterError, connectToMySql
from email.headerregistry import Address
from datetime import datetime, timedelta
from flask import g

from helpers.errors.enums import InputErrorCodes, ValidationErrorCodes, InternalErrorCodes
from helpers.errors.exceptions import InputError, ValidationError, ServerError
from helpers.utils import build_response_data


def create_document(data):
    _company_user = data['nombre_usuario']
    
    company_data = companies.get_company_data(_company_user)
    if not company_data:
        raise InputError('company', _company_user, status=InputErrorCodes.NO_RECORD_FOUND)

    signature = companies.get_sign_data(_company_user)
    if not signature:
        raise InputError(status=InputErrorCodes.NO_RECORD_FOUND,
                         message="No signature information was found for the company; can't sign the document, so the document can't be created.")

    _email_costs = None # MARKED FOR DEATH . Using _additional_emails now
    _additional_emails = []
    _email = None
    _receptor = data.get('receptor')
    # time for spaghetti
    if _receptor:
        _email = _receptor['correo']        

        # validate emails
        _additional_emails = _receptor.get('correosAdicionales')
        if _additional_emails is None or not isinstance(_additional_emails, list):
            _temp = _receptor.get('correo_gastos', '')
            _additional_emails = [_temp] if _temp != '' else [] # falling back to correo_gastos
        else:
            # remove duplicates
            _additional_emails = list(set(_additional_emails))
        validate_email(_email)
        for mail in _additional_emails:
            validate_email(mail)

    _type_document = fe_enums.TipoDocumentoApi[data['tipo']]
    _situation = data['situacion']
    _consecutive = data['consecutivo']
    _key_mh = data['clavelarga']
    _terminal = data['terminal']
    _branch = data['sucursal']
    _activity_code = data['codigoActividad']
    _other_phone = data['otro_telefono']
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

    _issued_date = parse_datetime(data['fechafactura'], 'fechafactura')

    if not isinstance(_reference, dict):
        _reference = None
    elif _reference:
        _reference['fecha'] = parse_datetime(_reference['fecha'], 'referencia => fecha').isoformat()

    _datestr = api_facturae.get_time_hacienda()
    datecr = api_facturae.get_time_hacienda(True)

    try:
        xml = api_facturae.gen_xml_v43(company_data, _type_document, _key_mh, _consecutive, _issued_date.isoformat(), _sale_condition,
                                   _activity_code, _receptor, _total_serv_taxed, _total_serv_untaxed, _total_serv_exone,
                                   _total_merch_taxed, _total_merch_untaxed, _total_merch_exone, _total_other_charges,
                                   _total_net_sales, _total_taxes, _total_discount, _lines, _other_charges, _others,
                                   _reference, _payment_methods, _credit_term, _currency, _total_taxed, _total_exone,
                                   _total_untaxed, _total_sales, _total_return_iva, _total_document)
    except KeyError as ker: # atm, this is just a baseImponible exception.
        raise # TODO : return {'error' : str(ker)} # INVALID DOCUMENT ERROR #TODO

    xml_to_sign = str(xml)

    try:
        xml_sign = api_facturae.sign_xml(
            signature['signature'],
            company_data['pin_sig'], xml_to_sign)
    except Exception as ex: # todo: be more specific about exceptions #TODO
         raise # TODO : return {'error' : 'A problem occurred when signing the XML Document.'}  # INTERNAL ERROR

    xmlencoded = base64.b64encode(xml_sign)
    
    pdfencoded = None;  # Por si ES tiquete que guarde nada como pdf
    if _type_document != 'TE':
        _logo = companies.get_logo_data(_company_user)
        if not _logo:
            raise InputError(status=InputErrorCodes.NO_RECORD_FOUND, message='No logo was found for the Company.')

        additional_pdf_fields = build_additional_pdf_fields(data)
        # don't know how we are calling this property, so just trying stuff out.
        pdf_notes = data.get('notas', data.get('observaciones', data.get('piedepagina',[])))
        _logo = _logo['logo'].decode('utf-8')
        try:
            pdf = makepdf.render_pdf(company_data, fe_enums.tagNamePDF[_type_document], _key_mh, _consecutive,
	                                _issued_date.strftime("%d-%m-%Y"), _sale_condition,
	                                _activity_code, _receptor, _total_serv_taxed, _total_serv_untaxed, _total_serv_exone,
	                                _total_merch_taxed, _total_merch_untaxed, _total_merch_exone, _total_other_charges,
	                                _total_net_sales, _total_taxes, _total_discount, _lines, _other_charges, pdf_notes,
	                                _reference, _payment_methods, _credit_term, _currency, _total_taxed, _total_exone,
	                                _total_untaxed, _total_sales, _total_return_iva, _total_document, _logo,
	                                additional_pdf_fields);
        except Exception as ex: #TODO : be more specific about exceptions
            raise # TODO : return {'error' : 'A problem occured when creating the PDF File for the document.'} # INTERNAL ERROR
        #Prueba de creacion de correo
        #emails.sent_email(pdf, xml_sign)
        pdfencoded = base64.b64encode(pdf);

    # Managing connection here...
    conn = connectToMySql()

    try:
            documents.save_document(_company_user, _key_mh, xmlencoded, 'creado', datecr, _type_document,
                                     _receptor, _total_document, _total_taxes, pdfencoded, _email, _email_costs,connection=conn)
            
            _id_company = company_data['id']

            if len(_additional_emails) > 0:
                save_additional_emails(_key_mh, _additional_emails, conn)

            save_document_lines(_lines,_id_company,_key_mh,conn)
            conn.commit()
    finally:
        conn.close()

    return build_response_data({'message' : 'Document successfully created.'})


def save_document_lines(lines, id_company, key_mh, conn):
    for _line in lines:
        _line_number = _line['numero']
        _quantity = _line['cantidad']
        _unity = _line['unidad']
        _detail = _line['detalle']
        _unit_price = _line['precioUnitario']
        _net_tax = _line['impuestoNeto']
        _total_line = _line['totalLinea']

        documents.save_document_line_info(id_company, _line_number, _quantity, _unity
                                                   , _detail, _unit_price, _net_tax, _total_line, key_mh,connection=conn)

        _taxes = _line.get('impuesto')
        if _taxes:
            save_document_taxes(_taxes,id_company,_line_number,key_mh, conn)

    return True


def save_document_taxes(taxes, id_company, line_number, key_mh, conn):
    for _tax in taxes:
        _rate_code = _tax['codigoTarifa']
        _code = _tax['codigo']
        _rate = _tax['tarifa']
        _amount = _tax['monto']

        documents.save_document_line_taxes(id_company, line_number, _rate_code,
                                                    _code, _rate, _amount, key_mh, connection=conn)

    return True


def save_additional_emails(key_mh, emails, conn):
    for email in emails:
        documents.save_document_additional_email(key_mh, email, connection=conn)

    return True

def validate_documents():
    return


def validate_document(company_user, key_mh):
    document_data = documents.get_document(key_mh)
    if not document_data:
        raise InputError('document', str(key_mh), status=InputErrorCodes.NO_RECORD_FOUND)

    company_data = companies.get_company_data(company_user)
    if not company_data:
        raise InputError('company', str(company_user), status=InputErrorCodes.NO_RECORD_FOUND)

    date_cr= api_facturae.get_time_hacienda(False)
    date = api_facturae.get_time_hacienda(True)

    try:
        token_m_h = api_facturae.get_token_hacienda(company_user, company_data['user_mh'], company_data['pass_mh'],
                                                company_data['env'])
    except Exception as ex: #TODO : be more specific about exceptions
        raise # TODO : return {'error' : 'A problem occured when attempting to get the token from Hacienda.'} # INTERNAL ERROR

    try:
        response_json = api_facturae.send_xml_fe(company_data, document_data, key_mh, token_m_h, date_cr,
                                             document_data['signxml'],
                                             company_data['env'])
    except Exception as ex: #TODO : be more specific about exceptions
        raise # TODO: return {'error' : 'A problem occurred when attempting to send the document to Hacienda.'} # INTERNAL ERROR

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

    documents.update_document(company_user, key_mh, None, state_tributacion, date)

    return build_response_data({'message' : return_message})


def consult_documents():
    return


def consult_document(company_user, key_mh):
    document_data = documents.get_document(key_mh)
    if not document_data:
        raise InputError('document', key_mh, status=InputErrorCodes.NO_RECORD_FOUND)

    company_data = companies.get_company_data(company_user)
    if not company_data:
        raise InputError('company', company_user, status=InputErrorCodes.NO_RECORD_FOUND)

    date = api_facturae.get_time_hacienda(True)

    try:
        token_m_h = api_facturae.get_token_hacienda(company_user, company_data['user_mh'], company_data['pass_mh'],
                                                company_data['env'])
    except Exception as ex: #TODO
        raise # TODO : return {'error' : 'A problem occured when attempting to get the token from Hacienda.'} # INTERNAL ERROR

    try:
        response_json = api_facturae.consulta_documentos(key_mh, company_data['env'], token_m_h, date,
                                                     document_data['document_type'])
    except Exception as ex: #TODO : be more specific about exceptions
        raise # TODO : return {'error' : 'A problem occurred when attempting to query the document to Hacienda.'} # INTERNAL ERROR

    response_status = response_json.get('ind-estado')
    response_text = response_json.get('respuesta-xml')

    documents.update_document(company_user, key_mh, response_text, response_status, date)

    result = {'data' : {}}
    if response_status == 'aceptado' and document_data['document_type'] != "TE":
        try:
            emails.sent_email_fe(document_data)
        except Exception as ex: #TODO : be more specific about exceptions
            result['data']['warning'] = 'A problem occurred when attempting to send the email.' # WARNING

    result['message'] = response_status
    result['data']['xml-respuesta'] = response_text
    return build_response_data(result)
    

def consult_document_notdatabase(company_user, key_mh, document_type):
    company_data = companies.get_company_data(company_user)
    if not company_data:
        raise InputError('company', company_user, status=InputErrorCodes.NO_RECORD_FOUND)

    date = api_facturae.get_time_hacienda(True)

    try:
        token_m_h = api_facturae.get_token_hacienda(company_user, company_data['user_mh'], company_data['pass_mh'],
                                                company_data['env'])
    except Exception as ex: #TODO : be more specific about exceptions
        raise # TODO : return {'error' : 'A problem occurred when attempting to get the token from Hacienda.'} # INTERNAL ERROR

    try:
        response_json = api_facturae.consulta_documentos(key_mh, company_data['env'], token_m_h, date,
                                                     document_type)
    except Exception as ex: #TODO : be more specific about exceptions
        raise # TODO: return {'error' : 'A problem occurred when attempting to fetch the document from Hacienda.'} # INTERNAL ERROR

    response_status = response_json.get('ind-estado')
    response_text = response_json.get('respuesta-xml')

    if response_text:
        return build_response_data({'message' : response_status, 'data' : {'xml-respuesta' : response_text} })
    else:
        raise ServerError(status=InternalErrorCodes.INTERNAL_ERROR) # TODO : new code: 2 bad data hacienda


def processing_documents(company_user, key_mh, is_consult):
    if is_consult:
        result = consult_document(company_user, key_mh)
    else:
        result = validate_document(company_user, key_mh)
    return result


def document_report(company_user, document_type):
    result = documents.get_documentsreport(company_user, document_type)
    return build_response_data({'data' : { 'documents' : result}})


def consult_vouchers(company_user, emisor, receptor, offset, limit):
    company_data = companies.get_company_data(company_user)
    if not company_data:
        raise InputError('company', company_user, status=InputErrorCodes.NO_RECORD_FOUND)

    try:
        token_m_h = api_facturae.get_token_hacienda(company_user, company_data['user_mh'], company_data['pass_mh'],
                                                 company_data['env'])
    except Exception as ex: #TODO : be more specific with exceptions
        raise # TODO : new InternalErrorCode 3 token. return {'error' : 'A problem occurred when attempting to get the token from Hacienda.'} # INTERNAL ERROR

    parameters = {}
    if emisor is not None:
        parameters['emisor'] = emisor
    if receptor is not None:
        parameters['receptor'] = receptor
    if offset is not None:
        parameters['offset'] = offset
    if limit is not None:
        parameters['limit'] = limit

    try:
        response_json = api_facturae.get_vouchers(token_m_h, parameters)
    except Exception as ex: #TODO : be more specific with exceptions
        raise # TODO : return {'error' : "A problem occurred when attempting to get the company's vouchers."} # INTERNAL ERROR

    response_status = response_json.get('status')
    response_text = response_json.get('text')

    if 200 <= response_status <= 206:
        return build_response_data({'data' : {'Comprobantes' : response_text}})
    else:
        raise ServerError(InternalErrorCodes.INTERNAL_ERROR) # TODO : Hacienda Unauthorized
        # return errors.build_internalerror_error('Hacienda considered the query as unauthorized.')


def consult_voucher_byid(company_user, clave):
    company_data = companies.get_company_data(company_user)
    if not company_data:
        raise InputError('company', company_user, status=InputErrorCodes.NO_RECORD_FOUND)

    try:
        token_m_h = api_facturae.get_token_hacienda(company_user, company_data['user_mh'], company_data['pass_mh'],
                                                company_data['env'])
    except Exception as ex: #TODO : be more specific with exceptions
        raise # TODO : hacienda token error return {'error' : 'A problem occurred when attempting to get the token from Hacienda.'} # INTERNAL ERROR

    try:
        response_json = api_facturae.get_voucher_byid(clave, token_m_h)
    except Exception as ex: #TODO : be more specific with exceptions
        raise # TODO : Internal get voucher error return {'error' : "A problem occurred when attempting to fetch the specified document."} # INTERNAL ERROR

    response_status = response_json.get('status')
    response_text = response_json.get('text')
    if response_status == 200:        
        return build_response_data({ 'data' : {'Comprobante' : response_text} })
    else:
        raise ServerError(InternalErrorCodes.INTERNAL_ERROR)
        # return errors.build_internalerror_error('Hacienda considered the query as unauthorized.')


def validate_email(email):
    """
    Validates an email by parsing it into an email.headerregistry.Address object.
    
    :param email: str - a string with the email to validate.
    :returns: bool - True if no errors were raised.
    :raises: ValueError - when 'email' is empty, 'email' is not a string, or email can't be parsed by Address, indicating the email is not valid.
    """
    if not email:
        raise ValidationError(status=ValidationErrorCodes.INVALID_EMAIL,
                              message='Empty Email')

    if not isinstance(email, str):
        raise ValidationError(status=ValidationErrorCodes.INVALID_EMAIL,
                              message='Email is not a string')

    try:
        Address(addr_spec=email)
    except (ValueError, IndexError):
        raise ValidationError(email, status=ValidationErrorCodes.INVALID_EMAIL)

    return True

def build_additional_pdf_fields(data):
    DATETIME_DISPLAY_FORMAT = '%d-%m-%Y'

    fields = {}
    ref_num = data.get('numReferencia')
    if ref_num:
        fields['ref_num'] = ref_num

    order_num = data.get('numOrden', data.get('numFecha', '')).strip();
    # just making sure "order_num" ain't suddenly a date...
    try:
        parse_datetime(order_num, 'numOrden/numFecha')
        order_num = None
    except ValidationError:
        pass

    if order_num:
        fields['order_num'] = order_num

    sale_condition = data['condicionVenta']
    if sale_condition == '02':
        issued_date = parse_datetime(data['fechafactura'], 'fechafactura')
        term_days = data['plazoCredito']
        # MARKED FOR DEATH : scraped in favor of not having to guess a date in the json...
        #due_date = None # data.get('numFecha') 
        #if isinstance(due_date, str) and due_date.strip():
        #    fields['due_date'] = parse_datetime(due_date).strftime(DATETIME_DISPLAY_FORMAT)
        #else:
        # END MFD
        fields['due_date'] = (issued_date + timedelta(days=int(term_days))).strftime(DATETIME_DISPLAY_FORMAT)
        fields['credit_term'] = term_days

    currency = data['codigoTipoMoneda']
    if currency['tipoMoneda'] != 'CRC':
        fields['currency_exchange'] = utils.stringRound(currency['tipoCambio'])

    details = data['detalles']
    for line in details:
        exemption_found = False
        for tax in line.get('impuesto', []):
            exemption = tax.get('exoneracion')
            if exemption:
                fields['exemption'] = {
                    'doc_type': fe_enums.ExemptionDocType[exemption['Tipodocumento']],
                    'doc_number': exemption['NumeroDocumento'],
                    'issuer': exemption['NombreInstitucion'],
                    'issued_date': parse_datetime(exemption['FechaEmision'], 'exoneracion => FechaEmision').isoformat(),
                    'percentage': exemption['porcentajeExoneracion'],
                    'total_amount': data['totalExonerado']
                    }
                exemption_found = True
                break
        if exemption_found:
            break

    return fields


def parse_datetime(value, field):
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
